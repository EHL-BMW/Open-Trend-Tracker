import { Link } from "react-router-dom";
import { useCatalog } from "../../api/queries";
import { ROUTES } from "../../routes";
import styles from "./Footer.module.css";

export const FOOTER_ID = "site-footer";

/** Site footer: confidentiality note, data version from the backend catalog, link to the method page. */
export function Footer() {
  const catalog = useCatalog();
  const dataVersion = catalog.data?.dataVersion;

  return (
    <footer id={FOOTER_ID} className={styles.footer}>
      <div className={styles.inner}>
        <span>BMW Group · Internal use only · Confidential</span>
        <span className={styles.right}>
          <span className={styles.data}>{dataVersion ? `Data ${dataVersion}` : "Data not loaded"}</span>
          <Link to={ROUTES.howItWorks}>How it works</Link>
        </span>
      </div>
    </footer>
  );
}
