import { useEffect, type ReactNode } from "react";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { usePageTitle } from "./usePageTitle";
import styles from "./ContentPage.module.css";

interface Props {
  title: string;
  eyebrow?: string;
  lead?: ReactNode;
  children?: ReactNode;
}

/** Layout for the text pages (How it works, FAQ, Newsletter): solid header, page title, content. */
export function ContentPage({ title, eyebrow, lead, children }: Props) {
  usePageTitle(title);
  // A new page starts at the top, not at the previous page's scroll position.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <main className={styles.page}>
        <header className={styles.header}>
          {eyebrow && <p className={styles.eyebrow}>{eyebrow}</p>}
          <h1>{title}</h1>
          {lead && <p className={styles.lead}>{lead}</p>}
        </header>
        {children}
      </main>
      <Footer />
    </>
  );
}
