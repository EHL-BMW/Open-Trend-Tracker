import { useEffect, useState, type ReactNode } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { NAV_ITEMS, ROUTES } from "../../routes";
import { HERO_ID } from "../hero/HeroVideo";
import { SettingsMenu } from "./SettingsMenu";
import styles from "./NavBar.module.css";

interface Props {
  mockMode: boolean;
  /** Page-specific buttons on the right (e.g. Reset / Run analysis on the planner). */
  actions?: ReactNode;
}

/** True while the intro video is still visible under the 78px nav bar. */
function useOverHero() {
  const { pathname } = useLocation();
  const [over, setOver] = useState(false);
  useEffect(() => {
    const hero = document.getElementById(HERO_ID);
    if (!hero || typeof IntersectionObserver === "undefined") {
      setOver(false);
      return;
    }
    // Edge-adjacent counts as "intersecting" with a zero-height overlap; require visible pixels.
    const observer = new IntersectionObserver(
      ([entry]) => setOver(Boolean(entry?.isIntersecting && entry.intersectionRect.height > 0)),
      { rootMargin: "-78px 0px 0px 0px", threshold: [0, 0.01] },
    );
    observer.observe(hero);
    return () => observer.disconnect();
  }, [pathname]);
  return over;
}

function NavLinks() {
  return (
    <ul>
      {NAV_ITEMS.map((item) => (
        <li key={item.to}>
          <NavLink
            to={item.to}
            end={item.to === ROUTES.planner}
            className={({ isActive }) => (isActive ? styles.active : undefined)}
          >
            {item.label}
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

/** Site header like bmw.de: roundel far left, main navigation, page actions right, menu on small screens. */
export function NavBar({ mockMode, actions }: Props) {
  const overHero = useOverHero();
  const { pathname } = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  // Close the mobile menu on navigation and with Esc.
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const transparent = overHero && !menuOpen;

  return (
    <header className={`${styles.nav} ${transparent ? styles.overHero : ""}`}>
      <div className={styles.inner}>
        <Link to={ROUTES.planner} className={styles.brand} aria-label="OpenTT, go to the planner">
          {/* Official BMW roundel (2020): white over the video and in dark mode, gray on the light header. */}
          <img
            className={`${styles.logo} ${styles.logoWhite}`}
            src="/brand/bmw-logo-white.svg"
            alt=""
            width={51}
            height={51}
          />
          <img
            className={`${styles.logo} ${styles.logoGray}`}
            src="/brand/bmw-logo-gray.svg"
            alt=""
            width={51}
            height={51}
          />
          <span className={styles.wordmark}>OpenTT</span>
          {mockMode && (
            <span
              className={styles.badge}
              title="Invented sample figures from the built-in demo backend, not real BMW data."
            >
              Demo data
            </span>
          )}
        </Link>

        <nav aria-label="Main" className={styles.links}>
          <NavLinks />
        </nav>

        <div className={styles.right}>
          <SettingsMenu />
          {actions && <div className={styles.actions}>{actions}</div>}

          <button
            type="button"
            className={styles.menuButton}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span className={`${styles.burger} ${menuOpen ? styles.burgerOpen : ""}`} aria-hidden="true" />
          </button>
        </div>
      </div>

      {menuOpen && (
        <nav id="mobile-menu" aria-label="Main mobile" className={styles.mobileMenu}>
          <NavLinks />
        </nav>
      )}
    </header>
  );
}
