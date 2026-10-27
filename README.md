# EconoCausal — Dynamic Pricing via Double Machine Learning

[![CI](https://github.com/your-org/econocausal/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/econocausal/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)

**EconoCausal** answers one question per customer: *"Would this customer buy **only if** we give them a discount?"*

It uses **Double/Debiased Machine Learning (EconML + DoWhy)** to estimate individual causal effects of discounts on purchase probability from confounded historical data, then allocates a fixed marketing budget to maximise incremental profit via a **SciPy LP optimiser**. A **FastAPI** backend and **React + Plotly** dashboard deliver everything end-to-end.

> Internship project — Infotact Solutions, Ref ITS/DSML/1142 (Oct–Nov 2026)

---

## Quick Start (< 10 min from clean clone)

```bash
# 1. Prerequisites: Python 3.11, uv (pip install uv), Node 18+
# 2. Clone and enter repo
git clone https://github.com/your-org/econocausal.git
cd econocausal

# 3. Install backend deps
make setup

# 4. Run full demo pipeline (data → train → evaluate → audit → optimise → report)
make demo

# 5. Start API + frontend in separate terminals
make api   # http://localhost:8000/docs
make web   # http://localhost:5173
```

Or with Docker:
```bash
cp .env.example .env
make docker-up   # http://localhost:8000 (API)  |  http://localhost:5173 (UI)
```

---

## Architecture

```
React + Plotly Dashboard (Setup | Graph | Uplift | Audit | Allocation | Summary | Monitoring)
        │ REST/JSON
    FastAPI (pydantic v2, async jobs, pagination)
        │
  ┌─────────────────────────────────────────────────────────┐
  │ data/      causal/       optimize/    evaluate/   monitor/│
  │ simulator  graph(DoWhy)  economics    metrics     drift   │
  │ loaders    propensity    allocator    qini        PSI/KS  │
  │ schema     dml(EconML)   strategies   policy_val  ATE-shift│
  │ splits     baselines     (SciPy)      report              │
  └─────────────────────────────────────────────────────────┘
        │
  registry/ (artifacts/models/{id}: model.joblib, metrics.json, ...)
```

---

## Key Concepts

| Segment | Buys without discount? | Buys with discount? | Action |
|---|---|---|---|
| **Persuadable** ✅ | No | Yes | Target! |
| **Sure Thing** ❌ | Yes | Yes | Skip (wastes budget) |
| **Lost Cause** ❌ | No | No | Skip |
| **Sleeping Dog** ❌ | Yes | No | Never target |

DML removes **confounding** (marketing historically targeted lapsed-but-valuable customers) via orthogonal ML: residualise Y and T on X, then fit the heterogeneous effect on residuals.

---

## Make Targets

| Target | Description |
|---|---|
| `make setup` | Install all Python deps with uv |
| `make data` | Generate synthetic data splits (5 seeds, 100k rows each) |
| `make train` | Train DML + baseline models |
| `make evaluate` | Run full evaluation → reports/evaluation_report.md |
| `make audit` | Run DoWhy refutation tests |
| `make optimize BUDGET=5000` | Run LP optimiser at given budget |
| `make api` | Start FastAPI backend |
| `make web` | Start React dev server |
| `make demo` | Full pipeline (data→train→evaluate→audit→optimize→report) |
| `make check` | Lint + types + tests (must pass) |
| `make e2e` | Playwright end-to-end tests |
| `make docker-up` | Build + start Docker services |

---

## Tech Stack

- **Causal**: DoWhy (graph, refutation), EconML (CausalForestDML, LinearDML)
- **ML**: LightGBM nuisance models, cross-fitting (K=5)
- **Optimisation**: SciPy linprog / milp (HiGHS)
- **Data**: pandas, pyarrow, pandera, numpy
- **API**: FastAPI, pydantic v2, uvicorn
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Plotly.js, TanStack Query/Table, React Flow

---

## Documentation

- [`docs/PROJECT.md`](docs/PROJECT.md) — System design, methodology, API contract
- [`docs/DATA_SPEC.md`](docs/DATA_SPEC.md) — Data schema, DGP, splits
- [`docs/EVALUATION.md`](docs/EVALUATION.md) — Metrics, targets, evaluation protocol
- [`docs/DELIVERABLES.md`](docs/DELIVERABLES.md) — Internship submission guide
- [`PRD.md`](PRD.md) — Product requirements
- [`plan.md`](plan.md) — Execution plan with checkboxes

---

## Evaluation Targets

| Metric | Target | Status |
|---|---|---|
| ATE relative error | ≤ 10% | 🔲 |
| √PEHE vs S-learner | ≥ 25% lower | 🔲 |
| Spearman ρ | ≥ 0.60 | 🔲 |
| Normalised Qini | beats predictive targeting | 🔲 |
| Profit vs blanket | ≥ +25% | 🔲 |
| Budget compliance | 100% | 🔲 |

---

## Project Structure

```
econocausal/
├── AGENTS.md              # AI agent rules (read first)
├── PRD.md                 # Product requirements
├── plan.md                # Execution plan
├── docs/                  # Detailed specifications
├── backend/
│   ├── src/econocausal/   # Core Python package
│   ├── scripts/           # CLI scripts (generate_data, train, evaluate)
│   └── tests/             # Unit, integration, API, E2E tests
├── frontend/              # React + TypeScript dashboard
├── data/                  # Generated data (git-ignored)
├── artifacts/             # Models & allocations (git-ignored)
└── reports/               # Evaluation reports & figures
```

---

## Assumptions & Limitations

1. **Unconfoundedness**: all confounders are observed in X (unverifiable; tested via sensitivity analysis)
2. **SUTVA**: no interference between customers
3. **Overlap**: all customers have >0 probability of any discount level
4. Uses **synthetic data** — results demonstrate method behaviour, not real-world profit
5. Discount targeting without fairness constraints may create price discrimination
