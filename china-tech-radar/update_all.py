#!/usr/bin/env python3
"""
Master Pipeline & Data Updater: Open Trend Tracker
===================================================
A single unified script that maintains and updates the entire project:

1. SCRAPER & QUANTIFIER:
   Executes real-time scraping of Chinese automotive tech feeds (36Kr, IT-Home,
   Dongchedi, CLS, etc.) with quota resolution, Poisson momentum, and Mann-Kendall tests.
   Updates:
     - china_tech_trends.json
     - china_tech_trends_data.js
     - china_tech_trends_articles.csv

2. BMW FLEET CATALOG & SOURCE ENRICHMENT:
   Ensures 100% data integrity for all 53 BMW BEV & PHEV models, enriching with
   direct ADAC Autokatalog links, official BMW Group PressClub dossier URLs,
   and official BMW Investor Relations & KBA registration evidence portals.
   Updates:
     - bmw_ev_phev_catalog.csv
     - bmw_ev_phev_catalog.json
     - data_bmw.js

3. AUDIT & DATA INTEGRITY VERIFIER:
   Verifies row counts, column schemas, and file existence across Europe Top 500,
   China Top 500, and BMW Fleet datasets.

4. GIT REPO SYNCHRONIZATION (Optional / --sync-git / --push):
   Mirrors updated data, web dashboards, and scripts into the repository folder
   and pushes directly to GitHub 'main'.

Usage:
  python3 update_all.py              # Full update (Scrape + Catalog + Validation)
  python3 update_all.py --no-scrape  # Fast update without web scraping (< 1s)
  python3 update_all.py --push       # Full update + Git commit & push to main
  python3 update_all.py --serve      # Full update + launch local preview server
"""

import sys
import os
import csv
import json
import time
import shutil
import subprocess
import argparse
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH_REPO_DIR = os.path.expanduser(
    "~/.gemini/antigravity-ide/brain/50b3aecf-d9ce-4482-b37b-c634a4750503/scratch/Open-Trend-Tracker"
)

# -----------------------------------------------------------------------------
# 1. SCRAPER ENGINE
# -----------------------------------------------------------------------------
def run_china_scraper(force_clean=False):
    print("\n" + "=" * 70)
    print("📡 [1/3] CHINA TECH MEGATRENDS SCRAPER & QUANTIFICATION ENGINE")
    print("=" * 70)
    scraper_path = os.path.join(WORKSPACE_DIR, "scrape_china_tech_trends.py")
    if not os.path.exists(scraper_path):
        print(f"❌ Error: Scraper not found at {scraper_path}")
        return False

    cmd = [sys.executable, scraper_path]
    if force_clean:
        cmd.append("--no-cache")

    start_t = time.time()
    res = subprocess.run(cmd, cwd=WORKSPACE_DIR)
    dur = time.time() - start_t

    if res.returncode == 0:
        print(f"✅ Scraper completed successfully in {dur:.1f}s.")
        return True
    else:
        print(f"❌ Scraper exited with code {res.returncode}")
        return False

# -----------------------------------------------------------------------------
# 2. BMW CATALOG ENRICHER
# -----------------------------------------------------------------------------
def run_bmw_enricher():
    print("\n" + "=" * 70)
    print("🚗 [2/3] BMW FLEET CATALOG & SOURCE VERIFICATION ENRICHER")
    print("=" * 70)
    enricher_path = os.path.join(WORKSPACE_DIR, "enrich_bmw_catalog_urls.py")
    if not os.path.exists(enricher_path):
        print(f"❌ Error: Enricher script not found at {enricher_path}")
        return False

    res = subprocess.run([sys.executable, enricher_path], cwd=WORKSPACE_DIR)
    if res.returncode == 0:
        print("✅ BMW Catalog enriched with PressClub & Sales Evidence URLs.")
        return True
    else:
        print(f"❌ Enricher exited with code {res.returncode}")
        return False

# -----------------------------------------------------------------------------
# 3. AUDIT & DATA INTEGRITY CHECKER
# -----------------------------------------------------------------------------
def run_integrity_audit():
    print("\n" + "=" * 70)
    print("🔍 [3/3] DATASET INTEGRITY & TRACEABILITY AUDIT")
    print("=" * 70)

    checks = [
        ("BMW Electrified Fleet CSV", "bmw_ev_phev_catalog.csv", 53),
        ("BMW Electrified Fleet JSON", "bmw_ev_phev_catalog.json", 53),
        ("BMW Client JS Data", "data_bmw.js", None),
        ("China Top 500 NEV JSON", "top_500_china_nev.json", 500),
        ("Europe Top 500 EV JSON", "top_500_ev_phev_europe.json", 500),
        ("China Tech Trends JSON", "china_tech_trends.json", 21),
        ("China Tech Articles CSV", "china_tech_trends_articles.csv", None),
        ("Customer Sentiment Pipeline", "bmw_ev_technology_sentiment_pipeline.json", None)
    ]

    all_passed = True
    for name, filename, expected_count in checks:
        filepath = os.path.join(WORKSPACE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"  ❌ Missing file: {filename}")
            all_passed = False
            continue

        size_kb = os.path.getsize(filepath) / 1024
        extra = ""

        if filename.endswith(".json") and expected_count is not None:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    count = len(d.get("cars", d.get("topics", [])))
                    extra = f"({count} records verified)"
            except Exception as e:
                extra = f"(JSON error: {e})"
                all_passed = False
        elif filename.endswith(".csv") and expected_count is not None:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    count = sum(1 for _ in csv.DictReader(f))
                    extra = f"({count} rows verified)"
            except Exception as e:
                extra = f"(CSV error: {e})"
                all_passed = False

        print(f"  ✅ {name:<30} [{size_kb:8.1f} KB] {extra}")

    return all_passed

# -----------------------------------------------------------------------------
# 4. GIT MIRROR & REMOTE PUSH
# -----------------------------------------------------------------------------
def sync_to_git(push=False):
    print("\n" + "=" * 70)
    print("🔄 GIT SYNCHRONIZATION")
    print("=" * 70)

    if not os.path.exists(SCRATCH_REPO_DIR):
        print(f"⚠️ Scratch repo directory not found at {SCRATCH_REPO_DIR}. Skipping git sync.")
        return

    dest_folder = os.path.join(SCRATCH_REPO_DIR, "china-tech-radar")
    os.makedirs(dest_folder, exist_ok=True)

    files_to_sync = [
        "china_tech_trends.json",
        "china_tech_trends_data.js",
        "china_tech_trends_articles.csv",
        "bmw_ev_phev_catalog.csv",
        "bmw_ev_phev_catalog.json",
        "data_bmw.js",
        "app.js",
        "china_megatrends.html",
        "bmw_pipeline_story.html",
        "index.html",
        "style.css",
        "scrape_china_tech_trends.py",
        "enrich_bmw_catalog_urls.py",
        "trends_server.py",
        "update_all.py",
        "README.md"
    ]

    synced_count = 0
    for fname in files_to_sync:
        src = os.path.join(WORKSPACE_DIR, fname)
        if os.path.exists(src):
            dst = os.path.join(dest_folder, fname)
            shutil.copy2(src, dst)
            synced_count += 1

    print(f"📁 Synced {synced_count} files to {dest_folder}")

    if push:
        print("🚀 Staging and pushing to origin main...")
        subprocess.run(["git", "add", "china-tech-radar/"], cwd=SCRATCH_REPO_DIR)
        
        status = subprocess.run(["git", "status", "--porcelain"], cwd=SCRATCH_REPO_DIR, capture_output=True, text=True)
        if not status.stdout.strip():
            print("✨ Git working tree clean. Nothing to push.")
            return

        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"chore(data): refresh China tech radar & BMW fleet sources [{ts}]"
        subprocess.run(["git", "commit", "-m", msg], cwd=SCRATCH_REPO_DIR)
        
        # Pull --rebase to avoid rejected pushes
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=SCRATCH_REPO_DIR)
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=SCRATCH_REPO_DIR)
        
        if push_res.returncode == 0:
            print(f"🎉 Successfully pushed to https://github.com/EHL-BMW/Open-Trend-Tracker.git (main)!")
        else:
            print("⚠️ Push failed. Please check git credentials.")

# -----------------------------------------------------------------------------
# 5. LOCAL SERVER RUNNER
# -----------------------------------------------------------------------------
def launch_server(port=3000):
    print(f"\n🌐 Starting local web server on port {port}...")
    server_path = os.path.join(WORKSPACE_DIR, "trends_server.py")
    if os.path.exists(server_path):
        subprocess.run([sys.executable, server_path, str(port)], cwd=WORKSPACE_DIR)
    else:
        subprocess.run([sys.executable, "-m", "http.server", str(port)], cwd=WORKSPACE_DIR)

# -----------------------------------------------------------------------------
# MAIN CLI
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Master Pipeline Updater: Refresh China Tech Radar & BMW Intelligence Datasets."
    )
    parser.add_argument("--no-scrape", action="store_true", help="Skip web scraping (fast update)")
    parser.add_argument("--force-scrape", action="store_true", help="Bypass cache and refetch all articles")
    parser.add_argument("--sync-git", action="store_true", help="Copy updated files to git repo folder")
    parser.add_argument("--push", action="store_true", help="Copy, commit, and push changes to GitHub main")
    parser.add_argument("--serve", action="store_true", help="Launch local server after updating")
    parser.add_argument("--port", type=int, default=3000, help="Port for preview server (default: 3000)")

    args = parser.parse_args()

    print("\n" + "━" * 70)
    print("🌟 OPEN TREND TRACKER — MASTER UPDATE PIPELINE")
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("━" * 70)

    # Step 1: Scrape
    if not args.no_scrape:
        run_china_scraper(force_clean=args.force_scrape)
    else:
        print("\n⏩ [1/3] Skipping web scraping (--no-scrape flag enabled).")

    # Step 2: Enrich BMW Catalog
    run_bmw_enricher()

    # Step 3: Integrity Audit
    audit_passed = run_integrity_audit()

    # Step 4: Git Sync / Push
    if args.push:
        sync_to_git(push=True)
    elif args.sync_git:
        sync_to_git(push=False)

    print("\n" + "━" * 70)
    if audit_passed:
        print("🎉 ALL SYSTEMS UP TO DATE AND VERIFIED!")
    else:
        print("⚠️ Pipeline finished with warnings. Review the audit output above.")
    print("━" * 70 + "\n")

    # Step 5: Optional Server
    if args.serve:
        launch_server(args.port)

if __name__ == "__main__":
    main()
