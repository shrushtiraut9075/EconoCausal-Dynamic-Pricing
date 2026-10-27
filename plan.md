# plan.md — EconoCausal Execution Plan

> Timeline follows the Infotact assignment letter: **10 Oct 2026 → 10 Nov 2026** (4 weeks + mid-project review + final review).
> Tick checkboxes as work completes. Every task has an ID, an owner-visible output, and an acceptance check.

## 0. Principles
1. **Causal correctness before polish.** Never ship a number that hasn't been validated against ground truth/RCT.
2. **Vertical slices.** Each week ends with something demoable end-to-end, however thin.
3. **Evaluation first.** The evaluation harness is built *before* the fancy model so every change is measured.
4. **Honest reporting.** Missed targets are documented with diagnosis, never hidden.
5. **Reproducible.** Seeds, pinned deps, one-command pipeline.

## 1. Tech Stack (decisions)

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.11 | EconML/DoWhy support |
| Env / deps | `uv` + `pyproject.toml` | fast, lockable |
| Causal graph & refutation | **DoWhy** | letter requires it |
| Causal ML | **EconML** (`CausalForestDML`, `LinearDML`) | letter requires it |
| Nuisance learners | **LightGBM** (primary), sklearn RandomForest (fallback) | speed + accuracy |
| Optimisation | **SciPy** (`linprog`/`milp`, HiGHS) | letter requires it |
| Data | pandas, numpy, pyarrow, pandera | validation + Parquet |
| API | FastAPI, pydantic v2, uvicorn | typed, OpenAPI |
| Frontend | React 18 + TypeScript + Vite, Tailwind, **Plotly.js** (react-plotly), TanStack Query/Table, React Flow (DAG) | letter requires React & Plotly |
| Testing / quality | pytest, hypothesis, ruff, mypy, vitest, Playwright (smoke) | |
| Packaging | Docker (backend, frontend), docker-compose, Makefile | |

## 2. Repository Layout (target)

```
econocausal/
├── AGENTS.md  PRD.md  plan.md  prompt.md  README.md
├── docs/ PROJECT.md DATA_SPEC.md EVALUATION.md DELIVERABLES.md
├── Makefile  pyproject.toml  docker-compose.yml  .env.example
├── backend/
│   ├── src/econocausal/
│   │   ├── config.py  logging.py
│   │   ├── data/        simulator.py  loaders.py  schema.py  splits.py  public_data.py
│   │   ├── causal/      graph.py  propensity.py  dml.py  baselines.py  refute.py  segments.py
│   │   ├── optimize/    economics.py  allocator.py  strategies.py
│   │   ├── evaluate/    metrics.py  qini.py  policy_value.py  report.py
│   │   ├── monitor/     drift.py
│   │   ├── nl/          summary.py
│   │   ├── registry/    store.py
│   │   └── api/         main.py  deps.py  schemas.py  routes/{datasets,models,optimize,monitor}.py
│   ├── scripts/         generate_data.py  train.py  evaluate.py  run_pipeline.py  download_public_data.py
│   └── tests/           unit/  integration/  api/
├── frontend/
│   └── src/ pages/{Setup,Graph,Uplift,Audit,Allocation,Summary,Monitoring}  components/  api/  lib/
├── data/ raw/ processed/ external/        (git-ignored except .gitkeep)
├── artifacts/ models/ allocations/ reports/
└── notebooks/ 01_eda.ipynb  02_causal_walkthrough.ipynb
```

## 3. Week-by-Week Plan

### WEEK 1 — 10–16 Oct · Foundations: Causal Graph + Dashboard Scaffold
**Goal:** a typed repo, a trustworthy simulator, a DAG, and a React shell that uploads data and sets constraints.

| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] 1.1 | Repo scaffold, uv, ruff, mypy, pytest, Makefile, pre-commit, CI workflow | green `make check` | CI passes on empty tests |
| [x] 1.2 | Implement `SimConfig` + simulator per `DATA_SPEC.md` | `data/simulator.py` | unit tests: shapes, ranges, shares of T within ±5pt, base rate 0.15–0.25, `gt_*` present, seed determinism |
| [x] 1.3 | Confounding proof test | `test_confounding.py` | naive diff-in-means ATE differs from true ATE by > 20% (proves confounding exists) |
| [x] 1.4 | Splits + RCT holdout + Parquet writer | `splits.py`, `generate_data.py` | `make data` yields 5 splits + gt files |
| [x] 1.5 | pandera schema + CSV loader + column mapping | `schema.py`, `loaders.py` | invalid CSVs produce readable errors; `gt_` columns rejected in training frame |
| [x] 1.6 | DoWhy graph builder + estimand identification + JSON export | `causal/graph.py` | JSON matches spec; backdoor adjustment set correct; unit test |
| [x] 1.7 | Propensity module + overlap diagnostics + SMD balance table | `causal/propensity.py` | overlap report on `train`; ESS computed |
| [x] 1.8 | EDA notebook (distributions, treatment by covariate, confounding plot) | `01_eda.ipynb` | notebook runs top-to-bottom |
| [x] 1.9 | FastAPI skeleton: `/health`, `POST /datasets`, `POST /datasets/demo`, `GET /datasets/{id}/profile`, `GET /graph` | running API | OpenAPI shows endpoints; API tests pass |
| [x] 1.10 | React app scaffold: layout, router, API client, **Setup page** (upload / demo / column map / budget & levels form), **Graph page** (React Flow DAG) | UI shell | can load demo data and see DAG + profile |

**Week-1 DoD:** demo data → profile → DAG visible in UI. Mentor update #1 sent (see `DELIVERABLES.md`).

### WEEK 2 — 17–23 Oct · Double ML Training + Uplift Visualisation
**Goal:** a trained causal model that provably beats baselines, with curves in the UI.

| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] 2.1 | Evaluation harness: ATE error, PEHE, Spearman, calibration-by-decile, Qini/AUUC, policy value | `evaluate/*` | metrics unit-tested on toy data with known answers |
| [x] 2.2 | Baselines: naive, S/T/X-learner, propensity-purchase targeting, random | `causal/baselines.py` | all produce ITE arrays on `test_obs` |
| [x] 2.3 | Nuisance model tuning on `valid` only (LightGBM small search); report R² and AUC | tuning config + report | no use of test sets (checked by test) |
| [x] 2.4 | `LinearDML` multi-valued treatment | `causal/dml.py` | ATE within 15% of truth |
| [x] 2.5 | `CausalForestDML` multi-valued treatment, cross-fitting `cv=5`, effect intervals | `causal/dml.py` | √PEHE ≥ 25% better than S-learner; Spearman ≥ 0.6 |
| [x] 2.6 | Model registry (`artifacts/models/{id}`) + train job (background) | `registry/store.py`, `POST /models/train`, `GET /jobs/{id}` | model reload gives identical predictions |
| [x] 2.7 | API: `GET /models/{id}/summary`, `/uplift`, `/cate/distribution` | endpoints | schema tests |
| [x] 2.8 | **Uplift page**: Qini curves (DML vs baselines vs random), uplift-by-decile bars, ITE histogram, predicted-vs-true calibration (synthetic only) | Plotly views | each chart has caption; curves match API data |
| [x] 2.9 | Stability study: 5 seeds × main metrics | `reports/stability.md` | mean ± sd reported |

**Week-2 DoD:** `make train && make evaluate` produces metrics table; UI shows uplift curves proving DML > predictive targeting. Mentor update #2.

### MID-PROJECT REVIEW — 24 Oct · Causal Audit + Data Load
| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] M.1 | DoWhy refuters on binary slices (0 vs 10, 0 vs 20): placebo, random common cause, data subset, unobserved common cause | `causal/refute.py` | PASS/WARN/FAIL logic per `EVALUATION.md §6` |
| [x] M.2 | Permutation test on treatment (own implementation) | in `refute.py` | placebo ATE CI contains 0 |
| [x] M.3 | Hidden-confounder stress test (`hidden_confounder_strength ∈ {0, 0.5, 1.0}`) | table in report | degradation documented |
| [x] M.4 | `GET /models/{id}/audit` + **Audit page** (cards with PASS/WARN/FAIL, effect-vs-refuter plots) | UI | all four tests render |
| [x] M.5 | Data-load test: dashboard filter/sort 50k ITE rows | server-side pagination + virtualised table | filter latency ≤ 1 s |
| [x] M.6 | Mid-review demo script + slides (5 slides) | `docs/` | rehearsed ≤ 7 min |

### WEEK 3 — 25–31 Oct · Prescriptive Optimisation + Allocation Matrix
| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] 3.1 | Economics module: margin, incremental profit, expected spend per (customer, level) | `optimize/economics.py` | hand-computed examples match |
| [x] 3.2 | Baseline outcome model `P0(x)` (LightGBM on T=0 + DR-adjusted) and calibration check | in `economics.py` | Brier/ECE reported |
| [x] 3.3 | Allocator: LP relaxation (HiGHS) + rounding, MILP for ≤ 5k customers, greedy fallback; constraints (max treat %, segment caps, min uplift) | `optimize/allocator.py` | spend ≤ budget always; LP value ≥ greedy; property-based tests (hypothesis) |
| [x] 3.4 | Conservative mode using CI lower bound | `allocator.py` | fewer Sleeping Dogs treated; documented trade-off |
| [x] 3.5 | Strategy comparison (optimised vs blanket vs random vs predictive vs oracle) + budget-sweep frontier | `optimize/strategies.py` | targets in PRD §8.2 evaluated |
| [x] 3.6 | API: `POST /optimize`, `GET /allocations/{id}` (paginated, filters), `/export.csv` | endpoints | CSV matches table |
| [x] 3.7 | **Allocation page**: budget slider, matrix (customer, segment, discount, uplift ± CI, spend), filters, segment donut, frontier chart | UI | 50k rows smooth |

**Week-3 DoD:** budget $5,000 → allocation table + comparison vs strategies, visible in UI. Mentor update #3.

### WEEK 4 — 1–7 Nov · API Packaging, Drift, NL Summaries, Polish
| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] 4.1 | `POST /predict` (single + batch) with ITE per level, best action | endpoint | p95 latency per NFR-4 |
| [x] 4.2 | Drift detector: PSI/KS/chi², residual drift, ATE-shift; Green/Amber/Red | `monitor/drift.py`, `POST /monitor/drift` | simulated shift (e.g. `discount_usage_rate` mean +0.2) flagged Amber/Red; no-shift flagged Green |
| [x] 4.3 | **Monitoring page** | UI | shows per-feature PSI bars + status |
| [x] 4.4 | NL summary engine (template-based; computed numbers only) | `nl/summary.py`, `GET /allocations/{id}/summary-text` | golden-file tests, e.g. "This strategy saves $X compared to blanket targeting." |
| [x] 4.5 | **Summary page** + export (copy / PDF print view) | UI | |
| [x] 4.6 | Docker images, docker-compose, `.env.example`, README quick-start | `docker compose up` works | clean-clone test |
| [x] 4.7 | Error handling, loading/empty states, accessibility pass, caption on every chart | UI polish | Lighthouse a11y ≥ 90 |

| 4.8 | Playwright smoke test of the whole journey | `tests/e2e` | passes in CI |
| 4.9 | Optional: Hillstrom/Criteo validation (stretch) | `reports/real_data.md` | only if all Must items green |

### STRATEGIC INTELLIGENCE & CAUSAL EVALUATION SUITE (Individual Contribution)
| ID | Task | Output | Acceptance |
|---|---|---|---|
| [x] S.1 | Pricing Strategy A/B Testing Engine | `intelligence/ab_testing.py` | Z-test, Welch's t-test, p-value, 95% CIs, statistical power, MDE, Bayesian win prob |
| [x] S.2 | Seasonal Pricing & Demand Elasticity Forecast | `intelligence/seasonality.py` | Calendar events (Black Friday, Diwali, Holidays), demand index vs elasticity shifts |
| [x] S.3 | Competitor Price Comparison & Elasticity Benchmark | `intelligence/competitor.py` | Price Index, cross-price elasticity, vulnerability rating, counter-pricing playbooks |
| [x] S.4 | Fair Pricing & Algorithmic Bias Audit | `intelligence/fairness.py` | 4/5ths rule Disparate Impact Ratio (DIR), parity differences, causal vs discrimination audit |
| [x] S.5 | Sales Drop Causal Counterfactual Decomposition | `intelligence/root_cause.py` | Shapley-style decomposition into competitor, macro, elasticity fatigue, seasonal dip, misallocation |
| [x] S.6 | Customer Pricing Explainability & What-If Simulator | `intelligence/explainability.py` | Feature attributions on ITE heterogeneity, segment decision logic, what-if scenarios |
| [x] S.7 | Automated Executive PDF / HTML Report Generator | `intelligence/report.py` | Standalone publication-ready report, `@media print` support, KPI scorecard |
| [x] S.8 | Fast API Route Registration & Schemas | `api/routes/intelligence.py` | Endpoints `/intelligence/*`, Pydantic v2 schemas, 100% test pass |
| [x] S.9 | React Strategic Intelligence UI Hub | `pages/StrategicIntelligencePage.tsx` | Interactive Plotly views, scenario sliders, live preview, direct PDF print |

### FINAL REVIEW — 8–10 Nov · Submission
| ID | Task | Output |
|---|---|---|
| F.1 | Freeze code; tag `v1.0`; final `make check` + `make demo` on clean clone | tag |
| F.2 | Generate `reports/evaluation_report.md` (auto) + figures | report data |
| F.3 | Write Project Report (doc) | `.docx`/PDF |
| F.4 | Build PPT (12–15 slides) | `.pptx` |
| F.5 | Record 5-minute demo video + live-demo checklist | video + script |
| F.6 | Submit deliverables (source, documentation, report, PPT, evaluation results, demo) | per letter |

## 4. Cross-Cutting Workstreams (continuous)
- **Docs:** update `README`/`PROJECT.md` as modules land. Docstrings on every public function.
- **Version control:** feature branches `feat/<id>-short-name`, Conventional Commits, PR per task, squash merge.
- **Progress updates:** short weekly mentor update (template in `DELIVERABLES.md`).
- **Risk log:** keep a running table in `docs/RISKS.md` (copy PRD §9).

## 5. Quality Gates
| Gate | Command | Must pass before |
|---|---|---|
| Lint/types/tests | `make check` | every PR merge |
| Metrics regression | `make evaluate` compares to `reports/baseline_metrics.json`; fails if √PEHE worsens > 10% | merging model changes |
| Leakage guard | `pytest -k leakage` | always |
| E2E | `make e2e` | release tags |

## 6. Make Targets (contract)
`make setup` · `make data` · `make train` · `make evaluate` · `make audit` · `make optimize BUDGET=5000` · `make api` · `make web` · `make demo` (data→train→evaluate→audit→optimize→report) · `make check` · `make e2e` · `make docker-up`

## 7. Risk-Driven Fallbacks
| If… | Then… |
|---|---|
| CausalForestDML too slow | reduce `n_estimators`, subsample to 40k, cache nuisance predictions; LinearDML as production fallback |
| Multi-valued T unsupported in a refuter | binary slices (0 vs d) |
| Spearman < 0.6 | check overlap, increase signal in simulator *before* freezing test sets (never after seeing test results); report honestly |
| React schedule slips | cut "Should/Could" UI items; keep API + one-page results view |
