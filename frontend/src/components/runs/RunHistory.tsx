import { errorMessage } from "../../api/client";
import { useRunHistory } from "../../api/queries";
import { CATEGORIES, WEIGHTED_KEYS } from "../../domain/categories";
import { StateMessage } from "../common/StateMessage";
import styles from "./RunHistory.module.css";

interface Props {
  currentRunId: string | null;
  openingId: string | null;
  onOpen: (id: string) => void;
}

const formatTime = (iso: string) => new Date(iso).toLocaleString([], { dateStyle: "short", timeStyle: "medium" });

/** Audit trail: every run stored by the backend, with its weights and ranking. */
export function RunHistory({ currentRunId, openingId, onOpen }: Props) {
  const runs = useRunHistory();

  return (
    <section aria-labelledby="history-title">
      <h2 id="history-title" className={styles.title}>
        Run history
      </h2>
      <p className={styles.sub}>
        Every run is stored with its filters and weights, so the same inputs reproduce the same ranking. Open a run to
        restore its settings and results.
      </p>
      <div className={`card ${styles.card}`}>
        {runs.isPending ? (
          <div className={styles.loading} aria-busy="true">
            <div className="skeleton" />
            <div className="skeleton" />
          </div>
        ) : runs.isError ? (
          <StateMessage
            tone="error"
            title="Couldn't load the run history"
            action={
              <button type="button" className="btn-tinted" onClick={() => void runs.refetch()}>
                Try again
              </button>
            }
          >
            {errorMessage(runs.error)}
          </StateMessage>
        ) : runs.data.items.length === 0 ? (
          <StateMessage title="No runs yet">Runs appear here after you run the analysis.</StateMessage>
        ) : (
          <div className={styles.scroll}>
            <table>
              <thead>
                <tr>
                  <th scope="col">Time</th>
                  <th scope="col">Run ID</th>
                  <th scope="col">Weights</th>
                  <th scope="col">Top results</th>
                  <th scope="col">
                    <span className="visually-hidden">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {runs.data.items.map((run) => (
                  <tr key={run.id} aria-current={run.id === currentRunId ? "true" : undefined}>
                    <td>{formatTime(run.createdAt)}</td>
                    <td>
                      <code>{run.fingerprint}</code>
                    </td>
                    <td>
                      {WEIGHTED_KEYS.map(
                        (k) =>
                          `${CATEGORIES[k].name.split(" ")[0]} ${run.enabled[k] ? `${Math.round(run.effectiveWeights[k] * 100)}%` : "off"}`,
                      ).join(" · ")}
                    </td>
                    <td>
                      <ol className={styles.top}>
                        {run.topTitles.map((t) => (
                          <li key={t}>{t}</li>
                        ))}
                      </ol>
                    </td>
                    <td className={styles.action}>
                      {run.id === currentRunId ? (
                        <span className={styles.current}>Showing</span>
                      ) : (
                        <button
                          type="button"
                          className="btn-tinted"
                          onClick={() => onOpen(run.id)}
                          disabled={openingId !== null}
                        >
                          {openingId === run.id ? "Opening…" : "Open"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
