import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ROUTES } from "../routes";
import { Flow } from "./FaqFlow";
import styles from "./FaqPage.module.css";

/** FAQ entries for the two Impact tabs: how the data is collected and how it becomes an impact number. */

const SRNI = "https://arxiv.org/abs/2401.05395";
const CAMERON_MILLER = "https://doi.org/10.3368/jhr.50.2.317";
const FWL = "https://doi.org/10.2307/1907330";
const LOVELL = "https://doi.org/10.1080/01621459.1963.10480682";
const BLP = "https://doi.org/10.2307/2171802";
const BH = "https://doi.org/10.1111/j.2517-6161.1995.tb02031.x";
const ANGRIST_PISCHKE = "https://press.princeton.edu/books/paperback/9780691120355/mostly-harmless-econometrics";
const CPCA = "http://www.cpcaauto.com/";

export const impactFaqs: {
  id: string;
  category: "impactData" | "impactMath";
  question: string;
  content: ReactNode;
}[] = [
  // ---------- Impact 1: data collection ----------
  {
    id: "impact-data-unit",
    category: "impactData",
    question: "Impact Analysis: what is measured, and what is one data point?",
    content: (
      <>
        <p>
          The question is:{" "}
          <strong>
            when a Chinese car got an update that added feature X, how did its China sales develop over the next four
            years
          </strong>
          , compared with the market and with updates that did not add X?
        </p>
        <p>
          One data point is a <strong>version pair</strong>: one nameplate (for example BYD Han) moving from its
          previous version to an updated version on a known launch date. For each pair we record what the update added,
          the nameplate&apos;s annual China sales for the year before the launch and the four years after, and the
          market totals for the same years.
        </p>
        <Flow
          label="Data collection flow for one version pair"
          steps={[
            { title: "1 · Find a dated update", detail: "Launch article or OEM release with the launch date" },
            {
              title: "2 · Record what was added",
              detail: "OEM wording, with a short quote and URL, mapped to a shared feature name",
            },
            {
              title: "3 · Attach nameplate sales",
              detail: "Annual China sales for the baseline year and years 1–4, from one source series",
            },
            { title: "4 · Attach market totals", detail: "China passenger-car market for the same years" },
            { title: "5 · Check and flag", detail: "Missing years, source changes, later updates, partial baseline" },
            { title: "Analysis-ready pair", tone: "accent" },
          ]}
        />
        <p>
          The result is four tables in <code>data/external/chinese_pairs/</code>: <code>pairs.csv</code> (one row per
          update), <code>features.csv</code> (what each update added), <code>model_sales.csv</code> (annual sales per
          nameplate and source series) and <code>market_sales.csv</code> (market totals). Every row keeps its source
          URL.
        </p>
        <p>
          The data is curated by hand in reviewed sessions rather than scraped. The analysis itself is deterministic and
          makes no AI calls, so the same tables always give the same numbers.
        </p>
      </>
    ),
  },
  {
    id: "impact-data-sales",
    category: "impactData",
    question: "Impact Analysis: where do the sales numbers come from?",
    content: (
      <>
        <ul>
          <li>
            <strong>SRNI-CAR</strong> (
            <a href={SRNI} target="_blank" rel="noreferrer">
              Ding et al., 2023
            </a>
            ): a peer-reviewed dataset of monthly sales for about 1,200 vehicle series in China, 2016–2022 (licence CC
            BY-NC 4.0). The file was downloaded once and its SHA-256 checksum recorded; the raw file is not copied into
            the project. An annual value is the sum of the 12 monthly values for the exact Chinese series name. The
            market total for these pairs comes from the same file, so nameplate and market are counted the same way.
          </li>
          <li>
            <strong>Published annual tables, 2020–2025</strong>: Wikipedia sales tables that cite Gasgoo or Yiche, plus
            CnEVPost and Gasgoo reports. When the underlying provider changes between years, the year gets a{" "}
            <code>provider_change</code> flag.
          </li>
          <li>
            <strong>Market totals</strong>:{" "}
            <a href={CPCA} target="_blank" rel="noreferrer">
              CPCA
            </a>{" "}
            (China Passenger Car Association) full-year passenger-car retail, total and NEV, 2020–2025, via CnEVPost,
            NBD and China Securities Journal.
          </li>
        </ul>
        <p>
          A pair needs its baseline year plus four full years, so the sales source decides which updates qualify.
          SRNI-CAR (2016–2022) covers updates launched January 2017 to March 2019; the published tables (to 2025) cover
          updates launched up to March 2022.
        </p>
      </>
    ),
  },
  {
    id: "impact-data-features",
    category: "impactData",
    question: "Impact Analysis: where do the feature labels come from, and how are they standardized?",
    content: (
      <>
        <p>
          Features come only from <strong>dated launch material</strong>: OEM press releases, Gasgoo, CnEVPost,
          Autohome/Yiche articles, and Wikipedia text with citations. Each feature row keeps a short quote and its URL.
          Labels are never taken from what happened to sales afterwards, so the outcome cannot leak into the input.
        </p>
        <div className={styles.formulaBox}>
          OEM wording (&quot;Shenxing 4C LFP battery&quot;) → shared feature (&quot;4C+ fast-charging battery&quot;) →
          subcategory (22, e.g. Charging &amp; replenishment) → category (8 technology domains)
        </div>
        <p>
          The shared feature name lets the same technology from different brands count together. Subcategories are the
          level where most estimates become possible. They use the same ids as the Newsletter topics, which is how a
          news signal is linked to its historical sales evidence.
        </p>
      </>
    ),
  },
  {
    id: "impact-data-rules",
    category: "impactData",
    question: "Impact Analysis: which pairs count, and which are excluded?",
    content: (
      <>
        <Flow
          label="Filter from all pairs to publication-eligible observations"
          steps={[
            { title: "All collected pairs" },
            {
              title: "Valid four-year pair",
              detail: "Baseline year and years 1–4 all observed in the same sales series",
            },
            {
              title: "Independent observation",
              detail: "Trims of one car that share an identical sales history are merged into one",
            },
            {
              title: "Publication-eligible",
              detail:
                "One source series throughout · on sale for the whole baseline year · no later update recorded inside the four years",
              tone: "accent",
            },
          ]}
        />
        <ul>
          <li>
            <strong>Same series throughout</strong>: a change from wholesale to registration numbers is not a sales
            change, so a year that is only available in another series counts as a <code>series_break</code> and is not
            used.
          </li>
          <li>
            <strong>Full baseline year</strong>: a car first sold after February of its baseline year would show
            artificial growth.
          </li>
          <li>
            <strong>No successor inside the window</strong>: a later update would mix a second change into the same
            years.
          </li>
          <li>
            <strong>Complete months</strong> (newer SRNI pairs): every year in the window must report all 12 months.
            Some older SRNI pairs still contain years with missing months; this is a known gap under review.
          </li>
        </ul>
        <p>
          Pairs that fail a rule are kept and flagged rather than deleted. The broad exploratory panel uses them, with
          the flags as controls. The current counts are shown in the header of{" "}
          <Link to={ROUTES.impactForecast}>Impact Analysis</Link>.
        </p>
      </>
    ),
  },

  // ---------- Impact 2: analysis and calculation ----------
  {
    id: "impact-math-overview",
    category: "impactMath",
    question: "Impact Analysis: how does downloaded data become an impact number?",
    content: (
      <>
        <Flow
          label="Analysis flow from raw sales to published or exploratory impact"
          steps={[
            { title: "Raw sales", detail: "SRNI-CAR monthly rows, or published annual tables" },
            { title: "Annual nameplate sales", detail: "Sum of 12 months; one source series per car" },
            { title: "Align years", detail: "Baseline year and years 1–4 after the launch" },
            { title: "Market-adjusted change", detail: "Car growth minus market growth, per year" },
            { title: "Merge duplicate trims", detail: "One independent observation per sales history" },
            { title: "Balanced panel", detail: "Observations with all four years" },
            [
              {
                title: "A · Isolated effect (gated)",
                detail: "Feature separated from its bundle; published only if every gate passes",
                tone: "accent",
              },
              {
                title: "B · Bundle association (exploratory)",
                detail: "Launches with vs without the item; shown dashed and labelled",
                tone: "warn",
              },
            ],
            { title: "Impact in % and vehicles, years 1–4", detail: "With a 95% interval" },
          ]}
        />
        <p>
          The code is in <code>backend/app/analysis/chinese_pairs.py</code> (path A) and{" "}
          <code>bundle_exploratory.py</code> (path B). The steps are explained one by one in the next questions.
        </p>
      </>
    ),
  },
  {
    id: "impact-math-years",
    category: "impactMath",
    question: "Impact Analysis: how are the launch year and the years after it aligned?",
    content: (
      <>
        <div className={styles.formulaBox}>
          Year 1 = launch year, if launched January–March; otherwise the next calendar year
          <br />
          Baseline = the calendar year before the launch year
          <br />
          Year k = Year 1 + (k − 1), for k = 1…4
        </div>
        <p>
          Sales are annual, so a launch late in the year mixes old and new versions; that mixed year is skipped.
          Example: an update launched in September 2018 has baseline 2017, then years 1–4 are 2019–2022.
        </p>
      </>
    ),
  },
  {
    id: "impact-math-market",
    category: "impactMath",
    question: "Impact Analysis: how is a sales change adjusted for the market?",
    content: (
      <>
        <div className={styles.formulaBox}>
          excess<sub>k</sub> = ln(S<sub>k</sub> / S<sub>baseline</sub>) − ln(M<sub>k</sub> / M<sub>baseline</sub>)
        </div>
        <p>
          S is the car&apos;s sales and M the market it competes in: the NEV or ICE part of the CPCA market, or the
          SRNI-CAR total for SRNI pairs. Zero means the car grew exactly as fast as its market. +0.2 means about 22%
          better than the market (e<sup>0.2</sup> − 1).
        </p>
        <p>
          Logs make growth symmetric and let controls add up. Comparing the car&apos;s change with the market&apos;s
          change over the same years is the difference-in-differences idea (
          <a href={ANGRIST_PISCHKE} target="_blank" rel="noreferrer">
            Angrist &amp; Pischke, 2009
          </a>
          ). It removes market-wide shifts such as the NEV boom from every pair.
        </p>
      </>
    ),
  },
  {
    id: "impact-math-isolated",
    category: "impactMath",
    question: "Impact Analysis: how is one feature's effect separated from the rest of the update?",
    content: (
      <>
        <p>
          An update usually brings several features at once. To credit one of them, path A compares updates with and
          without the item <strong>while holding the other recorded differences fixed</strong>:
        </p>
        <div className={styles.formulaBox}>
          excess<sub>k</sub> = α + β · [added the item] + Σ γ · [added each common peer item] + controls + error
          <br />
          controls: NEV or ICE · size of baseline sales · number of other items in the update · calendar year ·
          data-quality flags
        </div>
        <Flow
          label="Steps of the isolated-effect estimate"
          steps={[
            { title: "Remove what the controls explain", detail: "From both the sales change and the item indicator" },
            {
              title: "Compare what is left",
              detail: "β = how much of the remaining sales change goes with the remaining item variation",
            },
            {
              title: "Uncertainty clustered by car",
              detail: "Several observations of one nameplate count as one source of evidence",
            },
            { title: "Convert", detail: "impact % = (e^β − 1) × 100 · 95% interval from β ± 1.96 × SE" },
          ]}
        />
        <p>
          Removing the controls first and then comparing the residuals gives the same β as the full regression (the
          Frisch–Waugh–Lovell theorem;{" "}
          <a href={FWL} target="_blank" rel="noreferrer">
            Frisch &amp; Waugh, 1933
          </a>
          ;{" "}
          <a href={LOVELL} target="_blank" rel="noreferrer">
            Lovell, 1963
          </a>
          ). It also shows directly how much independent variation is left in the item. Standard errors are
          cluster-robust by nameplate (
          <a href={CAMERON_MILLER} target="_blank" rel="noreferrer">
            Cameron &amp; Miller, 2015
          </a>
          ).
        </p>
        <p>
          The effect in vehicles is the year-k sales of each car with the item times (1 − e<sup>−β</sup>), averaged per
          nameplate: the sales that car would not have had without the effect.
        </p>
      </>
    ),
  },
  {
    id: "impact-math-gates",
    category: "impactMath",
    question: "Impact Analysis: what are the publication gates?",
    content: (
      <>
        <p>
          A value is published only if <strong>all four years</strong> pass every gate, using publication-eligible
          observations only. Otherwise the page shows &quot;not identified&quot; and the reason.
        </p>
        <table className={styles.gateTable}>
          <thead>
            <tr>
              <th>Gate</th>
              <th>Threshold</th>
              <th>Why</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Cars with the item</td>
              <td>≥ 5 nameplates</td>
              <td>One or two cars cannot represent a feature</td>
            </tr>
            <tr>
              <td>Cars without the item</td>
              <td>≥ 5 nameplates</td>
              <td>A comparison group is needed</td>
            </tr>
            <tr>
              <td>Clusters</td>
              <td>≥ 10 nameplates</td>
              <td>Clustered uncertainty is unreliable with fewer</td>
            </tr>
            <tr>
              <td>Separable from the bundle</td>
              <td>residual variation ≥ 0.5</td>
              <td>After the controls, the item must still vary on its own</td>
            </tr>
            <tr>
              <td>Residual degrees of freedom</td>
              <td>≥ 8</td>
              <td>Enough data left after the controls</td>
            </tr>
            <tr>
              <td>Leverage</td>
              <td>&lt; 0.8 for every car</td>
              <td>No single car may decide the result</td>
            </tr>
            <tr>
              <td>Precision</td>
              <td>SE of β ≤ 0.35</td>
              <td>Keeps the 95% interval within about ×0.5 to ×2 of the estimate</td>
            </tr>
          </tbody>
        </table>
      </>
    ),
  },
  {
    id: "impact-math-exploratory",
    category: "impactMath",
    question: "Impact Analysis: what are the dashed exploratory lines, and how should I read them?",
    content: (
      <>
        <p>
          Path B uses the same sales change and controls but <strong>drops the peer items and the bundle size</strong>.
          It answers a simpler question:{" "}
          <em>how did updates that included X sell, compared with updates that did not?</em> The other items in the same
          update are part of that answer.
        </p>
        <ul>
          <li>
            Kept: ≥ 5 cars with and ≥ 5 without the item, ≥ 8 residual degrees of freedom, clustered 95% interval.
            Dropped: the precision gate.
          </li>
          <li>
            <strong>Strict panel</strong>: publication-eligible observations only. <strong>Broad panel</strong>: every
            complete observation, with the quality flags as controls.
          </li>
          <li>
            <strong>Direction</strong>: whether both panels show the same sign in every year they both estimate.
          </li>
        </ul>
        <p>
          <strong>How to read it.</strong> Carmakers often refresh models that are already declining, so a negative
          value can reflect which cars got the update rather than harm from the feature. With hundreds of estimates,
          about 1 in 20 intervals excludes zero by chance (
          <a href={BH} target="_blank" rel="noreferrer">
            Benjamini &amp; Hochberg, 1995
          </a>
          ). Trust a direction only when both panels and several years agree. That buyers value cars as bundles of
          characteristics is a classic result in car-demand research (
          <a href={BLP} target="_blank" rel="noreferrer">
            Berry, Levinsohn &amp; Pakes, 1995
          </a>
          ), which is why the bundle is hard to split.
        </p>
      </>
    ),
  },
  {
    id: "impact-math-references",
    category: "impactMath",
    question: "Impact Analysis: references",
    content: (
      <ol className={styles.refList}>
        <li>
          Ding, R., Chen, B., Wilson, J. M., Yan, Z., &amp; Huang, Y. (2023). SRNI-CAR: A comprehensive dataset for
          analyzing the Chinese automotive market. <em>IEEE International Conference on Big Data</em>, 3405–3412.{" "}
          <a href={SRNI} target="_blank" rel="noreferrer">
            arXiv:2401.05395
          </a>{" "}
          ·{" "}
          <a href="https://srni-car.github.io/" target="_blank" rel="noreferrer">
            dataset
          </a>
        </li>
        <li>
          China Passenger Car Association (CPCA). Monthly and annual passenger-car retail statistics.{" "}
          <a href={CPCA} target="_blank" rel="noreferrer">
            cpcaauto.com
          </a>
        </li>
        <li>
          Frisch, R., &amp; Waugh, F. V. (1933). Partial time regressions as compared with individual trends.{" "}
          <em>Econometrica</em>, 1(4), 387–401.{" "}
          <a href={FWL} target="_blank" rel="noreferrer">
            doi:10.2307/1907330
          </a>
        </li>
        <li>
          Lovell, M. C. (1963). Seasonal adjustment of economic time series and multiple regression analysis.{" "}
          <em>Journal of the American Statistical Association</em>, 58(304), 993–1010.{" "}
          <a href={LOVELL} target="_blank" rel="noreferrer">
            doi:10.1080/01621459.1963.10480682
          </a>
        </li>
        <li>
          Cameron, A. C., &amp; Miller, D. L. (2015). A practitioner&apos;s guide to cluster-robust inference.{" "}
          <em>Journal of Human Resources</em>, 50(2), 317–372.{" "}
          <a href={CAMERON_MILLER} target="_blank" rel="noreferrer">
            doi:10.3368/jhr.50.2.317
          </a>
        </li>
        <li>
          Angrist, J. D., &amp; Pischke, J.-S. (2009).{" "}
          <em>Mostly Harmless Econometrics: An Empiricist&apos;s Companion</em>. Princeton University Press.{" "}
          <a href={ANGRIST_PISCHKE} target="_blank" rel="noreferrer">
            publisher page
          </a>
        </li>
        <li>
          Berry, S., Levinsohn, J., &amp; Pakes, A. (1995). Automobile prices in market equilibrium.{" "}
          <em>Econometrica</em>, 63(4), 841–890.{" "}
          <a href={BLP} target="_blank" rel="noreferrer">
            doi:10.2307/2171802
          </a>
        </li>
        <li>
          Benjamini, Y., &amp; Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful
          approach to multiple testing. <em>Journal of the Royal Statistical Society B</em>, 57(1), 289–300.{" "}
          <a href={BH} target="_blank" rel="noreferrer">
            doi:10.1111/j.2517-6161.1995.tb02031.x
          </a>
        </li>
      </ol>
    ),
  },
];
