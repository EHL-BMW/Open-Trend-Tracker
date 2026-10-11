import { Component, type ErrorInfo, type ReactNode } from "react";
import { StateMessage } from "./StateMessage";

interface State {
  error: Error | null;
}

/** Shows a calm message instead of a blank page if rendering crashes. */
export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unhandled render error", error, info.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div style={{ maxWidth: 640, margin: "96px auto", padding: "0 16px" }}>
        <div className="card">
          <StateMessage
            tone="error"
            title="Something went wrong"
            action={
              <button type="button" className="btn-primary" onClick={() => window.location.reload()}>
                Reload the page
              </button>
            }
          >
            This page hit an unexpected error. Reloading usually fixes it.
          </StateMessage>
        </div>
      </div>
    );
  }
}
