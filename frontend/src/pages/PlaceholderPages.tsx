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

/** Placeholder until the team writes the questions and answers. */
export function FaqPage() {
  return (
    <ContentPage eyebrow="Help" title="FAQ" lead="Answers to common questions about OpenTT.">
      <ComingSoon title="Coming soon" text="The frequently asked questions are being written." />
    </ContentPage>
  );
}

/** Placeholder until the newsletter sign-up exists. */
export function NewsletterPage() {
  return (
    <ContentPage eyebrow="Stay informed" title="Newsletter" lead="Updates on new data, features and releases.">
      <ComingSoon title="Coming soon" text="The newsletter sign-up isn't available yet." />
    </ContentPage>
  );
}

export function NotFoundPage() {
  return (
    <ContentPage title="Page not found" lead="This page doesn't exist.">
      <ComingSoon title="Nothing here" text="The link may be outdated or mistyped." />
    </ContentPage>
  );
}
