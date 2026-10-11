import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { CATEGORIES, CATEGORY_ORDER, categoryColor } from "../domain/categories";
import { ROUTES } from "../routes";
import { ContentPage } from "./ContentPage";
import styles from "./ContentPage.module.css";

const SOURCE_TAGS: Record<string, string[]> = {
  sales: ["Evidence", "Weighted", "Filter: line, powertrain"],
  customer: ["Evidence", "Weighted", "Filter: pain points / praise"],
  trends: ["Assumption", "Weighted", "Filter: technology"],
  features: ["Context only", "Not weighted", "Filter: BMW features"],
};

export function HowItWorksPage() {
  return (
    <ContentPage
      eyebrow="Method"
      title="How it works"
      lead="OpenTT helps product managers improve an existing BMW series. It weighs sales, customer voices and market trends, ranks the improvements that matter most, and traces every recommendation back to its source records."
    >
      <section className={styles.section} aria-labelledby="sources">
        <h2 id="sources">Four sources</h2>
        <p>
          Every recommendation is built from the same four sources. Three of them carry a weight; Features / Engineering
          only filters and shows what BMW cars already offer.
        </p>
        <div className={styles.cards}>
          {CATEGORY_ORDER.map((key) => {
            const meta = CATEGORIES[key];
            return (
              <article
                key={key}
                className={`card ${styles.infoCard} ${meta.evidence ? "" : styles.dashed}`}
                style={{ "--c": categoryColor(key) } as CSSProperties}
              >
                <h3>{meta.name}</h3>
                <p>{meta.description}</p>
                <div className={styles.tags}>
                  {SOURCE_TAGS[key]?.map((t) => (
                    <span key={t} className={styles.tag}>
                      {t}
                    </span>
                  ))}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className={styles.section} aria-labelledby="steps">
        <h2 id="steps">From data to recommendation</h2>
        <p>Four steps, the same every time. The same inputs always give the same ranking.</p>
        <ol className={styles.steps}>
          <li className="card">
            <h3>Choose and filter</h3>
            <p>
              Switch sources on or off and narrow each one with its filters, for example only BEV or only pain points.
            </p>
          </li>
          <li className="card">
            <h3>Weigh</h3>
            <p>
              Give each weighted source its share. Weights always add up to 100%; a source switched off keeps its weight
              frozen and leaves the analysis.
            </p>
          </li>
          <li className="card">
            <h3>Score and rank</h3>
            <p>
              Each candidate gets a score per source, combined by your weights into one score out of 100. The Top 5 come
              out.
            </p>
          </li>
          <li className="card">
            <h3>Explain and decide</h3>
            <p>
              Open the reasoning for any recommendation: the verdict, a graph from source records to score, every cited
              record, and the signals to check.
            </p>
          </li>
        </ol>
      </section>

      <section className={styles.section} aria-labelledby="score">
        <h2 id="score">How the score is calculated</h2>
        <div className={`card ${styles.formula}`}>
          For every candidate and every switched-on source:
          <code>{`source score  = candidate's signal ÷ best candidate's signal × 100
points        = source score × effective weight
total score   = sum of points over all sources   (0–100)`}</code>
          <p>
            The effective weight is a source&apos;s weight divided by the sum of all switched-on weights, so the shares
            still add up to 100% when a source is off.
          </p>
        </div>
      </section>

      <section className={styles.section} aria-labelledby="evidence">
        <h2 id="evidence">Evidence vs. assumption</h2>
        <p>
          Sales and customer data describe what has happened: they count as evidence. The China EV trend forecast
          describes what might happen: it counts as an assumption. Every recommendation shows how much of its score
          rests on assumptions, and trend contributions are marked with dashed lines and outlines throughout the app.
        </p>
      </section>

      <section className={styles.section} aria-labelledby="audit">
        <h2 id="audit">Traceable and reproducible</h2>
        <p>
          Each run is stored with its filters, weights, data version and a fingerprint. The run history lists every run,
          and opening one restores its exact settings and results, so any ranking can be checked later.
        </p>
      </section>

      <div className={`card ${styles.cta}`}>
        <div>
          <h2>Ready to plan?</h2>
          <p>Set your sources and weights, then run the analysis.</p>
        </div>
        <Link className={styles.ctaLink} to={ROUTES.planner}>
          Open the planner
        </Link>
      </div>
    </ContentPage>
  );
}
