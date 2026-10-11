import { briefing, clockTime, humanize, type NewsItem } from "../content/briefing";
import { ContentPage } from "./ContentPage";
import styles from "./NewsletterPage.module.css";
import page from "./ContentPage.module.css";

const formatIssueDate = (value: string) => {
  const d = new Date(value.replace(" UTC", "Z").replace(" ", "T"));
  return Number.isNaN(d.getTime()) ? value : d.toLocaleDateString([], { dateStyle: "long" });
};

const IMPACT_CLASS: Record<string, string | undefined> = {
  CRITICAL: styles.critical,
  HIGH: styles.high,
};

/** Newsletter: the China tech briefing from the china-tech-radar module. */
export function NewsletterPage() {
  if (!briefing) {
    return (
      <ContentPage eyebrow="Newsletter" title="China tech briefing">
        <div className={`card ${page.empty}`}>
          <h2>This issue can&apos;t be shown</h2>
          <p>The briefing data has an unexpected format. Refresh it with npm run sync:newsletter.</p>
        </div>
      </ContentPage>
    );
  }

  const { feed_metadata: meta, megatrends_summary: trends, news_items: news } = briefing;

  return (
    <ContentPage
      eyebrow={`Newsletter · ${formatIssueDate(meta.last_updated)}`}
      title="China tech briefing"
      lead="What China's new-energy carmakers are shipping right now, and what it means for BMW. Curated from Chinese automotive media."
    >
      <p className={styles.issueMeta}>
        {meta.feed_name} · {news.length} stories · {meta.sources_monitored.length} sources monitored · updated{" "}
        {meta.last_updated}
      </p>

      {trends.length > 0 && (
        <section className={page.section} aria-labelledby="megatrends">
          <h2 id="megatrends">Megatrends at a glance</h2>
          <ul className={styles.trends}>
            {trends.map((t) => (
              <li key={t.trend_id} className={`card ${styles.trend}`}>
                <span className={styles.status}>{humanize(t.status)}</span>
                <h3>{t.title_en}</h3>
                <p>{t.executive_takeaway}</p>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className={page.section} aria-labelledby="stories">
        <h2 id="stories">In this issue</h2>
        <ol className={styles.stories}>
          {news.map((item) => (
            <Story key={item.id} item={item} />
          ))}
        </ol>
      </section>

      <section className={page.section} aria-labelledby="about-briefing">
        <h2 id="about-briefing">About this briefing</h2>
        <p>
          External market signals, not BMW evidence: in the planner they feed the Trends / Competition source, which is
          always marked as an assumption. Sources: {meta.sources_monitored.join(", ")}.
        </p>
      </section>
    </ContentPage>
  );
}

function Story({ item }: { item: NewsItem }) {
  return (
    <li className={`card ${styles.story}`}>
      <div className={styles.storyMeta}>
        <span className={`${styles.impact} ${IMPACT_CLASS[item.impact] ?? ""}`}>{humanize(item.impact)} impact</span>
        <span>{item.category}</span>
        <span className={styles.dot} aria-hidden="true">
          ·
        </span>
        <span>
          {item.source_tag ?? item.source}, {clockTime(item.publish_time)}
        </span>
      </div>
      <h3>{item.title_en}</h3>
      {item.title_cn && (
        <p className={styles.titleCn} lang="zh">
          {item.title_cn}
        </p>
      )}
      <p className={styles.summary}>{item.summary_en}</p>

      {(item.bmw_relevance || item.pm_action) && (
        <dl className={styles.takeaways}>
          {item.bmw_relevance && (
            <div>
              <dt>Why it matters for BMW</dt>
              <dd>{item.bmw_relevance}</dd>
            </div>
          )}
          {item.pm_action && (
            <div>
              <dt>Suggested PM action</dt>
              <dd>{item.pm_action}</dd>
            </div>
          )}
        </dl>
      )}

      <div className={styles.storyFoot}>
        {item.keywords.length > 0 && (
          <ul className={styles.keywords} aria-label="Keywords">
            {item.keywords.map((k) => (
              <li key={k}>{k}</li>
            ))}
          </ul>
        )}
        {item.original_url && (
          <a className={styles.source} href={item.original_url} target="_blank" rel="noopener noreferrer">
            Read the original ({item.source}) ↗
          </a>
        )}
      </div>
    </li>
  );
}
