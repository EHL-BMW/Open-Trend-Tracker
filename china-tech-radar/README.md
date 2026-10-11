# China EV Tech Radar & BMW Product Intelligence Pipeline

An evidence-backed, AI-assisted automotive intelligence module built for the **BMW Group Hackathon Challenge: AI for Product Decision Making**.

This module ingests, scores, and links internal customer feedback data (F70, G60, G68, G70 series) with cutting-edge Chinese New Energy Vehicle (NEV) tech megatrends to help BMW Product Managers formulate actionable, prioritized vehicle requirements for next-generation platforms.

---

## 🎯 Key Capabilities

### 1. China EV & Tech Megatrends Radar (`china_megatrends.html`)
* **Real-Time Statistical Evidence Engine**: Quantifies real Chinese automotive media and engineering feeds across **7 critical technological domains**:
  1. *Solid-State & High-Nickel Batteries* (CATL Freevoy, Shenxing Plus, WeLion, QingTao)
  2. *800V/900V Silicon Carbide (SiC) & Ultra-Fast Mega-Watt Charging*
  3. *End-to-End Autonomous Driving & Solid-State LiDAR* (Huawei ADS 3.0, XPeng Turing / XNGP, Li Auto)
  4. *Large AI Models & Smart Cockpit* (Qualcomm Snapdragon 8295, HarmonyOS Cockpit, Xiaomi HyperOS)
  5. *Steer-by-Wire, Rear-Wheel Steering & Active Suspension*
  6. *Low-Altitude eVTOL & Flying Car Land-Aircraft Carriers* (XPeng AeroHT, EHang)
  7. *Gigapress Integrated Die-Casting & Cell-to-Chassis (CTC/CTB)*
* **Product Manager UX**: Minimalist, high signal-to-noise ratio interface (KISS principle).
* **Direct Verification & Live Refresh**: One-click dynamic update button triggers fresh ingestion with clickable original Chinese news links (*IT Home, 36Kr, Dongchedi, CLS, Sina Auto*).
* **Mathematical Urgency Formula**:
  $$\text{Urgency Score} = \min\left(100, 30 + 3.2 \times \text{Mentions} + 22 \times \text{Relevance} + 12 \times \text{Tech Density}\right)$$

### 2. Multi-Source Pipeline & Customer Feedback Analysis (`bmw_pipeline_story.html`)
* Synthesizes 4 BMW internal data streams:
  1. *Customer Verbatims* (F70, G60, G70 complaints, wants, pain points)
  2. *Customer Study Scores* (Attribute satisfaction ratings)
  3. *Sales Volume Impact* (Units by powertrain and market)
  4. *Option & Equipment Packages* (Standard vs optional equipment codes)
* Directly links customer complaints with Chinese market disruption threats to derive explainable PM requirements with audit trails.

### 3. Global EV Catalog & Explorer (`index.html`)
* Complete tri-catalog explorer:
  - **China Top 500 NEV (纯自主品牌)**: 500 domestic Chinese models with specifications and price brackets.
  - **Europe Top 500**: 500 European BEV/PHEV models cross-referenced with ADAC Autokatalog.
  - **BMW Electrified Fleet**: All 53 serial BEV & PHEV BMW variants.

---

## 📁 Repository Structure

| File / Directory | Description |
| :--- | :--- |
| `china_megatrends.html` | Live China Tech Megatrends Radar web dashboard |
| `bmw_pipeline_story.html` | End-to-end customer verbatim & requirements pipeline explorer |
| `index.html` | Global Top 500 & BMW Electrified Fleet 3-way explorer |
| `scrape_china_tech_trends.py` | Scraping, normalization, NLP classification & quantitative scoring engine with quota mitigation |
| `trends_server.py` | Lightweight Python server with live `/api/trends` and `/api/scrape` endpoints |
| `china_tech_trends.json` | Real-time structured trends database (mentions, urgency score, speed, keywords) |
| `china_tech_trends_data.js` | Browser-ready dataset export (`window.CHINA_TECH_TRENDS_DATA`) |
| `china_tech_trends_articles.csv` | Scraped and verified news articles with timestamp, source, domain, and original URL |
| `BMW_EV_Customer_Complaints_Study_Report.pdf` | Executive PDF study analyzing recurring customer pain points |
| `BMW_EV_Technology_Domains_Analysis_Report.pdf` | Comprehensive PDF report on the 7 technological domains |
| `BMW_Technology_Domains_Ranking_and_Methodology.pdf` | Mathematical scoring methodology paper |
| `bmw_ev_technology_sentiment_pipeline.json` | Structured sentiment and priority pipeline dataset |
| `generate_domain_pdf_report.py` | Script to regenerate domain analysis PDF report |
| `generate_methodology_pdf.py` | Script to regenerate methodology PDF report |

---

## 🚀 Quickstart & Local Setup

### 1. Launch the Web Application
```bash
# Inside the china-tech-radar directory:
python3 trends_server.py 3000
```
Then navigate to:
- **China Tech Megatrends Radar**: [http://localhost:3000/china_megatrends.html](http://localhost:3000/china_megatrends.html)
- **BMW Pipeline & Decision Story**: [http://localhost:3000/bmw_pipeline_story.html](http://localhost:3000/bmw_pipeline_story.html)
- **Global EV Catalog**: [http://localhost:3000/index.html](http://localhost:3000/index.html)

### 2. Run the Real-Time Scraper on Demand
```bash
python3 scrape_china_tech_trends.py
```
The scraper queries primary Chinese news channels via RSS feeds, parses full content, extracts vehicle parameters (LiDAR, 800V, CLTC, ADAS, AI models), computes statistical velocities, and refreshes the data files automatically.
