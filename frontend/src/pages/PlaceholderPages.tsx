import { Link } from "react-router-dom";
import { ROUTES } from "../routes";
import { ContentPage } from "./ContentPage";
import styles from "./ContentPage.module.css";

function ComingSoon({ title, text }: { title: string; text: string }) {
  return (
    <div className={`card ${styles.empty}`}>
      <h2>{title}</h2>
      <p>{text}</p>
      <Link className={styles.ctaLink} to={ROUTES.planner}>
        Back to the planner
      </Link>
    </div>
  );
}


export function NotFoundPage() {
  return (
    <ContentPage title="Page not found" lead="This page doesn't exist.">
      <ComingSoon title="Nothing here" text="The link may be outdated or mistyped." />
    </ContentPage>
  );
}
