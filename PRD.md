# PRD — EconoCausal: Dynamic Pricing via Double Machine Learning

| Field | Value |
|---|---|
| Product | EconoCausal |
| Organisation | Infotact Solutions (Data Science & ML internship) |
| Ref | ITS/DSML/1142 |
| Duration | 1 month — 10 Oct 2026 → 10 Nov 2026 |
| Owner | Intern (Data Associate L1) |
| Status | Draft v1.0 |

---

## 1. Vision

A marketing/finance team should be able to answer one question for every customer:

> "Would this specific customer buy **if and only if** we give them a discount — and how big should that discount be?"

EconoCausal turns historical (observational) campaign data into **individual-level causal effect estimates** and a **budget-constrained discount allocation**, delivered through a REST API and an interactive dashboard. It replaces "who is likely to buy?" with "who will buy *because of* the discount?".

## 2. Problem Statement

Standard predictive ML models learn **correlation**. A churn model may flag a user with 90% churn risk and trigger a $20 discount, but that user might have churned anyway — the $20 is wasted. Others would have bought without any discount ("Sure Things"), and a few buy *less* when discounted ("Sleeping Dogs"). Prediction cannot separate these groups; causal inference can.

**Core technical challenge:** historical discounts were *not* randomly assigned (past campaigns targeted lapsed, valuable users). Naive comparison of treated vs untreated is therefore confounded. We use **Double/Debiased Machine Learning (DML)** to remove confounding from observed variables and estimate the **Individual Treatment Effect (ITE / CATE)**.

## 3. Goals & Non-Goals

### Goals
- G1. Estimate ITE per customer for each discount level ($0 baseline vs $5 / $10 / $20) with confidence intervals.
- G2. Prove causal validity: identification assumptions checked, refutation tests passed, evaluation against ground truth (synthetic) and a randomised holdout.
- G3. Allocate a fixed budget (e.g. $5,000) to maximise expected incremental profit via a constrained optimiser.
- G4. Provide a dashboard: upload/configure → causal graph → uplift curves → audit → allocation matrix → plain-language summary → drift status.
- G5. Package as a documented REST API with a data-drift detector.
- G6. Produce internship deliverables: source code, documentation, report, PPT, model evaluation results, live demo.

### Non-Goals
- Real-time bidding / per-session pricing, multi-period dynamic programming.
- Proprietary customer data (we use synthetic data + public benchmark datasets).
- Production cloud deployment, auth/SSO, multi-tenancy.
- Using an LLM for core numbers (any LLM-generated text is a stretch goal; default summaries are template-based and fully computed).

## 4. Personas

| Persona | Need | Success looks like |
|---|---|---|
| **Marketing Director (primary)** | Plan a promo within budget; maximise ROI | Uploads data, sets budget, gets a per-customer discount table + "saves $X vs blanket targeting" |
| **Data Scientist** | Trust the causal estimates | Sees DAG, nuisance-model quality, refutation results, Qini curves |
| **Finance Analyst** | Verify spend and ROI | Sees budget used ≤ cap, expected incremental profit with intervals |
| **ML Engineer** | Integrate & monitor | Clean API, model registry, drift alerts |

## 5. User Stories (with priority — MoSCoW)

| ID | Story | Priority |
|---|---|---|
| US-1 | As a director I can upload historical campaign CSV (or load demo data) and map columns | Must |
| US-2 | I can set a budget, discount levels, margin rate and objective | Must |
| US-3 | I can see the causal DAG (confounders, treatment, outcome) and edit the confounder list | Must |
| US-4 | I can train the causal model and watch job status | Must |
| US-5 | I can view uplift curves (Qini, uplift-by-decile) proving the model beats random/predictive targeting | Must |
| US-6 | I can view the causal audit (refutation tests with pass/fail) | Must |
| US-7 | I can run the optimiser and get an allocation matrix (customer → discount, expected uplift, cost) | Must |
| US-8 | I can filter/sort/export the matrix and view segments (Persuadable / Sure Thing / Lost Cause / Sleeping Dog) | Must |
| US-9 | I get a natural-language summary ("This strategy saves $4,200 vs blanket targeting") | Must |
| US-10 | I can call `/predict` and `/optimize` via REST | Must |
| US-11 | I get drift warnings when new data differs from training data | Must |
| US-12 | I can switch to conservative mode (treat only if CI lower bound > 0) | Should |
| US-13 | I can compare budget levels on an efficiency-frontier chart | Should |
| US-14 | I can validate on a real public uplift dataset (Hillstrom / Criteo sample) | Could |
| US-15 | I can generate an LLM-written narrative summary | Could |

## 6. Functional Requirements

### 6.1 Data layer
- FR-1. Synthetic data simulator with known ground-truth ITE and **confounded** treatment assignment (spec: `DATA_SPEC.md`).
- FR-2. CSV ingestion with schema validation (pandera), column mapping, missing-value and range checks, clear error messages.
- FR-3. Reproducible splits: `train`, `valid`, `test_obs` (confounded), `test_rct` (small randomised holdout).
- FR-4. Dataset profiling endpoint (row counts, treatment distribution, missingness, propensity overlap).

### 6.2 Causal engine
- FR-5. **Causal graphing (DoWhy):** build the DAG, identify the estimand (backdoor), expose DAG as JSON for the UI.
- FR-6. **Propensity module:** multi-class propensity model, overlap diagnostics, clipping, effective-sample-size, covariate balance (standardised mean differences before/after weighting).
- FR-7. **Double ML (EconML):** `CausalForestDML` (primary) and `LinearDML` (interpretable baseline) with LightGBM nuisance models, K-fold cross-fitting, multi-valued discrete treatment, effect intervals.
- FR-8. **Baselines:** naive difference-in-means, S-learner, T-learner, X-learner, predictive purchase-propensity targeting, random targeting.
- FR-9. **Refutation / audit:** placebo treatment, random common cause, data subset, unobserved common cause (sensitivity), plus own permutation test; results stored with PASS/WARN/FAIL.
- FR-10. Segmentation of customers into 4 behavioural segments using ITE + baseline probability.

### 6.3 Optimisation
- FR-11. Prescriptive optimiser (SciPy HiGHS): choose ≤ 1 discount level per customer maximising expected incremental profit s.t. expected discount spend ≤ budget (formulation in `PROJECT.md §6`).
- FR-12. Conservative mode using ITE confidence-interval lower bound.
- FR-13. Optional constraints: max % of customers treated, per-segment caps, minimum uplift threshold.
- FR-14. Strategy comparison: optimised vs blanket vs random vs predictive-targeting vs oracle (synthetic only).

### 6.4 API (FastAPI)
- FR-15. Endpoints: datasets, graph, train (async job), model summary / uplift / audit, predict, optimize, allocations (paginated + CSV export), summary-text, drift. Full contract in `PROJECT.md §8`.
- FR-16. Model registry on disk with metadata, metrics, config, reference statistics.
- FR-17. OpenAPI docs, typed schemas (pydantic v2), consistent error format.

### 6.5 Monitoring
- FR-18. Drift detector: PSI + KS (numeric), chi-square (categorical), outcome-residual drift, treatment-effect drift (re-estimated ATE vs reference); Green/Amber/Red status with thresholds.

### 6.6 Dashboard (React + Plotly)
- FR-19. Views: **Setup**, **Causal Graph**, **Model & Uplift**, **Audit**, **Allocation Matrix**, **Strategy Summary**, **Monitoring**.
- FR-20. Interactive filtering of 50k+ customer ITE scores (server-side pagination/aggregation; sampled scatter plots).
- FR-21. Natural-language summaries generated from computed numbers (template engine with unit tests).

## 7. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Reproducibility | Same seed → same metrics (±1e-6 for deterministic parts); all runs log versions + git hash |
| NFR-2 | Performance — training | 100k rows, CausalForestDML end-to-end ≤ 15 min on a laptop (4–8 cores); demo preset (20k rows) ≤ 3 min |
| NFR-3 | Performance — optimiser | 50k customers × 4 levels ≤ 10 s |
| NFR-4 | Performance — API | `/predict` p95 ≤ 500 ms for 1 customer; ≤ 2 s for 1,000 |
| NFR-5 | Dashboard | Filter + redraw ≤ 1 s on 50k rows |
| NFR-6 | Quality | ≥ 80% test coverage on core package; ruff + mypy clean; no TODOs in main |
| NFR-7 | Security | Upload size cap (50 MB), CSV-only, no code execution from uploads, CORS allow-list, no secrets in repo |
| NFR-8 | Usability | Every chart has a one-line "what this means" caption; accessible colours; mobile-tolerant layout |
| NFR-9 | Documentation | README quick-start works from clean clone in ≤ 10 min |

## 8. Success Metrics

### 8.1 Causal / ML (measured on synthetic ground truth + RCT holdout)
| Metric | Target | Stretch |
|---|---|---|
| ATE relative error (vs true ATE) | ≤ 10% and 95% CI covers truth | ≤ 5% |
| √PEHE improvement vs S-learner | ≥ 25% lower | ≥ 40% |
| Spearman(ITE_hat, ITE_true) | ≥ 0.60 | ≥ 0.75 |
| Normalised Qini coefficient on RCT holdout | beats random and predictive-targeting | ≥ 1.5× predictive targeting |
| Placebo-treatment refutation | placebo ATE CI contains 0 | — |
| Random-common-cause refutation | ATE change ≤ 5% | ≤ 2% |
| Data-subset refutation | ATE change ≤ 10% | ≤ 5% |
| Overlap | ≥ 90% of rows within [0.02, 0.98] propensity for every level | — |

### 8.2 Business (synthetic, ground-truth value)
| Metric | Target |
|---|---|
| Incremental profit vs blanket targeting at same budget | ≥ +25% |
| Incremental profit vs predictive-propensity targeting at same budget | ≥ +15% |
| Share of oracle-policy value captured | ≥ 80% |
| Budget compliance | 100% of runs: spend ≤ budget |

> If a target is missed, **report it honestly with the diagnosis** — never tune on the test sets to hit a number.

## 9. Assumptions, Risks, Dependencies

| # | Assumption / Risk | Mitigation |
|---|---|---|
| A1 | Unconfoundedness: all confounders are observed | Document; add unobserved-confounder sensitivity test; stress-test with hidden confounder flag |
| A2 | Overlap (positivity) holds | Overlap diagnostics, trimming, report ESS |
| A3 | SUTVA (no interference between customers) | State explicitly in docs/limitations |
| R1 | EconML / DoWhy version conflicts | Pin versions in `pyproject.toml`; lock file; CI smoke test |
| R2 | Forest training too slow | Subsample presets, `n_estimators` knobs, cache nuisance predictions |
| R3 | DoWhy refuters slow or incompatible with multi-valued T | Run on binary slices (0 vs d) with 10–20k subsample |
| R4 | Weak heterogeneity → poor ITE ranking | Tune on validation only; report honestly; add LinearDML fallback |
| R5 | Scope creep in UI | MoSCoW above; "Could" items only after Must items are green |

## 10. Milestones (aligned to assignment letter)

| Milestone | Dates (2026) | Exit criteria |
|---|---|---|
| Week 1 | 10–16 Oct | DAG + simulator + data validation + React scaffold with upload & budget views |
| Week 2 | 17–23 Oct | DML trained, baselines, uplift/Qini API + Plotly curves |
| **Mid-Project Review** | 24 Oct | Refutation audit passing; dashboard filters 50k ITE scores |
| Week 3 | 25–31 Oct | Optimiser + allocation matrix UI |
| Week 4 | 1–7 Nov | REST API packaged, drift detector, NL summaries, polish |
| **Final Review** | 8–10 Nov | Demo, report, PPT, evaluation results, docs, submit |

## 11. Definition of Done (project)
- [ ] All **Must** user stories pass acceptance tests
- [ ] `make check` (lint, types, tests) is green; coverage ≥ 80% on core
- [ ] `make demo` reproduces the full pipeline from a clean clone
- [ ] `reports/evaluation_report.md` generated with all tables/figures and honest target comparison
- [ ] Docs complete (README, PROJECT, DATA_SPEC, EVALUATION, API reference)
- [ ] Deliverables package ready (see `DELIVERABLES.md`)

## 12. Glossary
**ITE/CATE** individual/conditional average treatment effect · **DML** double/debiased ML (residual-on-residual with cross-fitting) · **DAG** directed acyclic graph · **Confounder** variable affecting both treatment and outcome · **Qini/Uplift curve** cumulative incremental gain when ranking by predicted uplift · **PEHE** precision in estimating heterogeneous effects · **Persuadable** buys only if discounted · **Sure Thing** buys regardless · **Lost Cause** doesn't buy regardless · **Sleeping Dog** buys less if discounted.
