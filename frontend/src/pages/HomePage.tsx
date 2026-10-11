import { HeroVideo } from "../components/hero/HeroVideo";
import { Footer } from "../components/layout/Footer";
import { NavBar } from "../components/layout/NavBar";
import { config } from "../config";
import { usePageTitle } from "./usePageTitle";

/** Start page: the full-screen video intro with what OpenTT does and the way into the planner. */
export function HomePage() {
  usePageTitle("Home");
  return (
    <>
      <NavBar mockMode={config.useMocks} />
      <HeroVideo />
      <Footer />
    </>
  );
}
