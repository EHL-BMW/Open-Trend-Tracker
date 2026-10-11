# Open-Trend-Tracker
Build an AI-powered application that turns customer feedback, product and sales data, and web research into traceable, evidence-backed customer requirements for an automobile, with a product manager in control of every decision that matters.

## Current implementation

- `backend/app/grabbers/`: official BMW and Chinese-OEM data acquisition.
- `backend/app/`: preprocessing, taxonomy mapping, unified evidence, recommendation scoring, and plots.
- `backend/app/services/`: frontend-ready forecast, price, engineering-comparison, and customer-document services.
- `frontend/`: OpenTT planner (React + TypeScript); `npm run dev:backend` runs it on the real `/api/v1` backend.
- [`docs/FRONTEND_BACKEND_HANDOFF.md`](docs/FRONTEND_BACKEND_HANDOFF.md): complete coworker handoff,
  endpoint contract, examples, refresh commands, limitations, and verification steps.

## Quick Start

```bash
./run.sh
```
Starts both backend (port 8000) and frontend (port 5173) in a single command.

Quick verification:

```bash
cd backend && uv sync && uv run pytest
cd ../frontend && npm ci && npm test && npm run build
```
Here is the **distilled requirements specification for your hackathon project**—filtering out all the background reading and focusing strictly on **what your application must do, what is in/out of scope, and what you must submit**.

---

# Hackathon Project Requirements Specification
**Challenge:** *AI for Product Decision Making* (BMW Group)  
**Goal:** Build an AI-assisted application that turns diverse data into evidence-backed customer requirements for a successor vehicle, keeping the Product Manager (PM) in control.

---

## 1. Functional Requirements (What the Application Must Do)

### FR-1: Data Ingestion & Web Enrichment
* **FR-1.1**: Ingest the 4 provided BMW internal data sources:
  1. *Customer Verbatims* (free-text complaints, likes, wants, defects)
  2. *Customer Study* (quantitative satisfaction ratings across vehicle attributes)
  3. *Sales Volumes* (units by market, powertrain, and year)
  4. *Equipment Lists / Option Lists* (current standard and optional packages)
* **FR-1.2**: Enrich internal data with **structured external web knowledge** (e.g., competitor capabilities like Tesla/Audi/Mercedes, automotive market trends, technology shifts for 2028–2030).

### FR-2: Signal Extraction & Source Linkage
* **FR-2.1**: Extract actionable signals from the data:
  * Recurring customer complaints & pain points
  * Unmet customer needs
  * Competitor advantages
  * Forward-looking market/tech trends
* **FR-2.2**: **Strict Traceability**: Every extracted signal must be visibly and verifiably linked to its source (e.g., exact verbatim ID/quote, study score, option code, or web source).

### FR-3: Customer Requirement Derivation
* **FR-3.1**: Translate extracted signals into **customer-facing product requirements**.
* **FR-3.2**: Requirements must be:
  * **Clear & Actionable**: Specific enough for product planning.
  * **Customer-Facing**: Focused on user experience and perceived value, not internal engineering specs.
  * **Realistic**: Plausible for a 3–5 year horizon (successor vehicle).

### FR-4: Explainable Prioritization Logic
* **FR-4.1**: Prioritize/rank the derived requirements using a **defined, transparent scoring logic**.
* **FR-4.2**: The prioritization rationale must be explainable (e.g., factoring in severity of customer pain, market sales volume impact, competitor urgency, and feasibility).

### FR-5: Human-in-the-Loop (PM Decision Control)
* The PM must **not** be a passive reader. The app must allow the PM to:
  * **Approve** a requirement.
  * **Reject** a requirement (with rationale).
  * **Edit / Modify** a requirement, its scope, or its priority.
  * **Challenge** a requirement (interrogate the underlying assumptions, trade-offs, and evidence).

### FR-6: Complete Audit Trail
* **FR-6.1**: Maintain an immutable, chronological log of all events within the system:
  * Every PM action (approve, reject, edit, challenge)
  * Every parameter or weight change
  * Timestamps, actor identification, before/after states, and notes.
* **FR-6.2**: The audit trail must be viewable and auditable.

---

## 2. Scope Boundaries

| In Scope (What to focus on) | Out of Scope (Do NOT spend time here) |
| :--- | :--- |
| **Customer-facing product experience:** | **Regulatory & homologation:** |
| • Features & equipment packages | • Crash test certification, emissions compliance, type approval |
| • Comfort, seating & interior space | **Technical & engineering specifications:** |
| • Usability, HMI & physical vs. digital controls | • Component specs, bus architectures, supplier selection |
| • Infotainment, software & digital services | **Detailed financial / cost models:** |
| • Driving dynamics & ride feel (customer perception) | • Precise bill-of-materials (BOM) cost, margin calculations |
| • Range & charging experience (as experienced by user) | *(Rough effort or cost may only be used as a high-level ranking factor)* |

---

## 3. Demonstration & Testing Requirements

* **Minimum Test Case**: Demonstrate the app working end-to-end for **at least one derivative in one market** (e.g., *BMW 5 Series G60/G68 in Europe, US, or China*).
* **Extensibility**: The system must **not be hardcoded as a one-off**—the architecture must demonstrate that it can ingest and run for the other vehicle lines (BMW 1 Series F70, 7 Series G70) and other markets.

---

## 4. Judging Criteria (How You Will Be Scored)

1. **Decision and Scoring Logic**: Is the prioritization methodology sound, transparent, and explainable?
2. **Workflow and Human Decision-Making**: Does the app genuinely empower the PM to steer, challenge, and decide rather than blindly trusting black-box AI?
3. **Traceability and Auditability**: Can every decision and requirement be traced back to concrete evidence and logged in a verifiable audit trail?
4. **Solution Quality, Usability, and Feasibility**: Is the interface intuitive, robust, and practical for an automotive OEM workflow?
5. **Innovation, Scalability, and Business Impact**: Does this approach scale across BMW's vehicle portfolio and drive real product value?

---

## 5. Submission Deliverables

1. **Live Demo**: A working, interactive prototype demonstrating the end-to-end workflow (Ingestion $\rightarrow$ Signal Extraction $\rightarrow$ Requirement Derivation $\rightarrow$ Prioritization $\rightarrow$ PM Interaction $\rightarrow$ Audit Trail).
2. **Pitch Deck**: Presentation covering the problem, solution architecture, PM workflow, and business impact.
3. **GitHub Repository**: Clean, well-documented source code.

---

## OpenTT – Series Improvement Planner (frontend)

PM tool that turns Sales, Customer, Trends / Competition and Features / Engineering data into a weighted, explainable
Top 5 of improvements for an existing BMW model series, with every recommendation traced back to its source records.

- Code: [`frontend/`](frontend/) (React + TypeScript + Vite; `npm run dev` uses a mock backend, `npm run dev:backend`
  the real one in `backend/app/services/planner.py`)
- Guide and setup: [`docs/PLANNER.md`](docs/PLANNER.md)
- API contract for the backend: [`docs/API.md`](docs/API.md)

```bash
cd frontend
npm install
npm run dev
```
