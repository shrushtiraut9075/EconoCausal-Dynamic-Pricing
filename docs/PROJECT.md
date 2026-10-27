# PROJECT.md — EconoCausal Project Documentation

## 1. What is EconoCausal?
EconoCausal is a **causal-AI pricing engine**. From historical campaign data it learns *how much each individual customer's purchase probability changes* when offered a specific discount (the **Individual Treatment Effect**), then allocates a fixed marketing budget to the customers and discount levels with the highest *incremental* profit.

**Domain:** Economics & Causal AI. **Method:** Double/Debiased Machine Learning (DML). **Output:** per-customer discount prescriptions, uplift curves, audit evidence, REST API and dashboard.

## 2. Why correlation fails (intuition)
| Customer type | Buys without discount? | Buys with discount? | Discount worth it? |
|---|---|---|---|
| **Persuadable** | No | Yes | ✅ Yes — the only profitable target |
| **Sure Thing** | Yes | Yes | ❌ Wastes money |
| **Lost Cause** | No | No | ❌ Wastes money |
| **Sleeping Dog** | Yes | No | ❌ Hurts revenue |

A predictive model ranks by *P(buy)* and mostly targets Sure Things / high-risk Lost Causes. A causal model ranks by *P(buy | discount) − P(buy | no discount)*.

## 3. System Architecture

```
            ┌────────────────────────── React + Plotly Dashboard ──────────────────────────┐
            │ Setup │ Causal Graph │ Model & Uplift │ Audit │ Allocation │ Summary │ Drift │
            └───────────────────────────────────┬──────────────────────────────────────────┘
                                                │ REST/JSON
                                      ┌─────────▼─────────┐
                                      │   FastAPI layer   │  schemas, jobs, pagination, CSV export
                                      └─────────┬─────────┘
   ┌───────────────┬───────────────┬────────────┼───────────────┬───────────────┬───────────────┐
   │ data/         │ causal/       │ optimize/  │ evaluate/     │ monitor/      │ nl/           │
   │ simulator     │ graph(DoWhy)  │ economics  │ metrics, Qini │ drift PSI/KS  │ templated     │
   │ loaders       │ propensity    │ allocator  │ policy value  │ residual/ATE  │ summaries     │
   │ schema        │ dml(EconML)   │ strategies │ report        │ shift         │               │
   │ splits        │ refute        │ (SciPy)    │               │               │               │
   └───────────────┴───────┬───────┴────────────┴───────────────┴───────────────┴───────────────┘
                           │
                 registry/ (artifacts/models/{id}: model.joblib, config.yaml, metrics.json, reference_stats.json)
```

### Pipeline (batch)
`raw/CSV or simulator → validate → split → propensity+overlap → DML (cross-fit) → ITE + CI → refutation audit → economics → optimise → report + dashboard`

## 4. Methodology

### 4.1 Identification
Assumptions: **(1) Unconfoundedness** given observed X, **(2) Overlap**, **(3) SUTVA**, **(4) Consistency**, **(5) No post-treatment covariates**. DoWhy formalises the DAG and backdoor estimand; the adjustment set = all pre-treatment covariates.

### 4.2 Double Machine Learning (Chernozhukov et al.)
Partial-linear structure with heterogeneity:
`Y = θ(X)·T + g(X) + ε`, `T = m(X) + η`
1. Fit nuisance `ĝ(X)=E[Y|X]` and `m̂(X)=E[T|X]` with LightGBM, using **K-fold cross-fitting** (K=5) → out-of-fold predictions only.
2. Residualise: `Ỹ = Y − ĝ(X)`, `T̃ = T − m̂(X)` (for discrete multi-level T, EconML uses one-hot residuals per level).
3. Final stage estimates `θ(X)`:
   - **`CausalForestDML`** (primary): honest, non-parametric heterogeneity with confidence intervals.
   - **`LinearDML`** (baseline/interpretable): `θ(X)=⟨β, φ(X)⟩`.
4. Effect for level d: `τ_d(x) = θ̂(x; T0=0 → T1=d)` with intervals via `effect_interval`.
Why it works: orthogonalisation makes `θ̂` insensitive to first-stage errors (Neyman orthogonality), so flexible ML can control confounding without bias from regularisation.

> Binary outcome note: Y is 0/1; nuisance `ĝ` is a LightGBM **regressor** on Y (a linear-probability style), which is the standard EconML usage. Clip final probabilities to [0,1] in economics.

### 4.3 Propensity & overlap
Multi-class LightGBM/logistic model for `P(T=k|X)`, cross-fitted. Diagnostics: histograms per level, trimming bounds [0.02, 0.98], ESS, standardised mean differences before/after IPW. Propensities are used for **diagnostics, evaluation (IPW/AIPW Qini)** and the **Propensity Score Matching/weighting module** requested in the brief; DML itself uses `m̂(X)` internally.

### 4.4 Baselines (to prove value)
Naive diff-in-means · S-learner · T-learner · X-learner · "predictive" targeting (rank by `P(buy|X)` or churn-style risk) · random · oracle (synthetic).

### 4.5 Segmentation
From `τ̂` (best level) and baseline `P̂0`: Persuadable (`τ̂>0.05, P̂0<0.5`), Sure Thing (`P̂0≥0.5, |τ̂|≤0.05`), Lost Cause (`P̂0<0.1, τ̂≤0.02`), Sleeping Dog (`τ̂<−0.02`), else "Marginal".

## 5. Economics
Per customer *i*, level *d* ∈ {5,10,20}; margin rate `r` (default 0.40), `AOV_i`, `m_i = r·AOV_i`:
- `P0_i = P̂(buy | x_i, no discount)`; `τ_id = ITE`.
- **Expected spend** `S_id = (P0_i + τ_id)·d`  (discount only paid on purchase).
- **Incremental profit** `Δπ_id = τ_id·m_i − (P0_i + τ_id)·d`.
Persuadable condition: `τ·m > (P0+τ)·d`.
Conservative mode replaces `τ` with its CI lower bound for the benefit term.

## 6. Optimisation Formulation (SciPy)
Decision `x_id ∈ {0,1}` (1 = give customer *i* discount *d*):

```
maximise   Σ_i Σ_d  Δπ_id · x_id
subject to Σ_d x_id ≤ 1                       ∀ i      (≤ 1 discount per customer)
           Σ_i Σ_d S_id · x_id ≤ B                       (budget)
           optional: Σ x_id ≤ ρ·N ; segment caps ; τ_id ≥ τ_min
```
This is a **multiple-choice knapsack**. Solve the LP relaxation with `scipy.optimize.linprog(method="highs")` (at most one fractional customer per binding constraint → round down, then greedy-fill residual budget by best Δπ/S ratio). For N ≤ 5,000 also expose exact `scipy.optimize.milp`. Pre-filter: drop options with `Δπ ≤ 0`. Report LP upper bound vs rounded value (optimality gap).

## 7. Data
See `DATA_SPEC.md` (schema, DGP formulas, splits, validation). Evaluation protocol in `EVALUATION.md`.

## 8. API Contract (FastAPI, JSON)

| Method & Path | Purpose | Key payload / response |
|---|---|---|
| `GET /health` | liveness | `{status, version}` |
| `POST /datasets` | upload CSV (≤ 50 MB) | → `{dataset_id, rows, columns, profile}` |
| `POST /datasets/demo` | generate synthetic demo | body `{n, seed, hidden_confounder_strength}` |
| `GET /datasets/{id}/profile` | counts, treatment mix, missingness, overlap | |
| `PUT /datasets/{id}/mapping` | column roles & confounder list | `{treatment, outcome, id, aov, confounders[]}` |
| `GET /datasets/{id}/graph` | DAG JSON + estimand | see DATA_SPEC §7 |
| `POST /models/train` | start training job | `{dataset_id, estimator:"causal_forest"\|"linear", cv, n_estimators, levels[]}` → `{job_id, model_id}` |
| `GET /jobs/{job_id}` | status | `{state, progress, message}` |
| `GET /models/{id}/summary` | metrics, nuisance quality, config | |
| `GET /models/{id}/uplift` | Qini/uplift curves, decile table | arrays for Plotly |
| `GET /models/{id}/cate/distribution` | ITE histogram per level | |
| `GET /models/{id}/audit` | refutation results | `[{test, status, effect_before, effect_after, p_or_ci, note}]` |
| `POST /predict` | ITE per level for customers | `{model_id, customers:[{…features}]}` → `[{id, ite:{5,10,20}, ci, p0, best_action}]` |
| `POST /optimize` | run allocator | `{model_id, dataset_id, budget, levels, objective, mode:"standard"\|"conservative", margin_rate, constraints}` → `{allocation_id, summary}` |
| `GET /allocations/{id}` | paginated matrix | query: `page,size,sort,segment,discount,min_uplift` |
| `GET /allocations/{id}/export.csv` | CSV | |
| `GET /allocations/{id}/summary-text` | NL summary | `{headline, bullets[]}` |
| `GET /allocations/{id}/frontier` | profit vs budget | |
| `POST /monitor/drift` | compare new data vs reference | → `{status, features:[{name, psi, ks, flag}], residual_drift, ate_shift}` |

Errors: `{error:{code, message, details}}`, proper HTTP codes (400 validation, 404, 409 job state, 422 schema, 500).

## 9. Dashboard Specification
| Page | Content |
|---|---|
| **Setup** | upload / demo, column mapping, confounder picker, budget, discount levels, margin rate, mode toggle |
| **Causal Graph** | React Flow DAG (treatment, outcome, confounders; hidden-U dashed), estimand text, adjustment set |
| **Model & Uplift** | Qini + uplift curves (DML vs baselines vs random), decile uplift bars, ITE histogram, calibration (synthetic), metrics cards |
| **Audit** | 4 refutation cards PASS/WARN/FAIL with plots; overlap & balance charts |
| **Allocation** | budget slider, matrix table (virtualised), filters, segment donut, spend gauge, frontier chart, CSV export |
| **Summary** | NL headline + bullets ("saves $X vs blanket"), key assumptions, print view |
| **Monitoring** | per-feature PSI bars, status badge, ATE-shift sparkline |

Design: clean light theme with dark-mode support; neutral greys + one accent; colour-blind-safe palette for segments; every chart titled with a one-line takeaway caption.

## 10. Drift Detection
- Covariate drift: PSI (10 quantile bins; <0.1 green, 0.1–0.25 amber, >0.25 red), KS test (numeric), chi-square (categorical).
- Outcome-model drift: mean/variance of nuisance residuals `Y−ĝ(X)` on new labelled data; CUSUM alarm.
- Effect drift: re-estimate ATE on recent window (bootstrap CI) vs reference ATE; alert if outside CI.
- Overall status = worst of components. Reference stats saved at train time.

## 11. Natural-Language Summaries
Template engine pulling **only computed values** (spend, incremental profit, lift vs blanket/random/predictive, treated share, segment shares, confidence statement, caveats). Example:
> "Targeting 3,420 of 20,000 customers (17%) with discounts uses $4,962 of your $5,000 budget and is expected to add $18,300 in profit — $4,200 more than giving the same budget to a blanket campaign. 82% of treated customers are Persuadables."
Golden-file unit tests guard wording and numbers.

## 12. Testing Strategy
| Level | Examples |
|---|---|
| Unit | simulator ranges; economics formulas; metrics on toy data; drift on synthetic shifts; NL templates |
| Property-based | allocator never exceeds budget, ≤1 level per customer, monotone in budget |
| Integration | demo pipeline end-to-end; model save/load parity |
| API | schema, pagination, error format |
| Statistical | ATE/PEHE/Spearman targets; refutation outcomes; seed stability |
| Leakage | forbid `gt_*`; assert no test-set use in tuning |
| E2E | Playwright: demo load → train → audit → optimise → summary |

## 13. Limitations & Ethics
Observational causal claims rest on unconfoundedness; the unobserved-confounder test quantifies, not removes, this risk. Discount targeting can create fairness issues (e.g. price discrimination); the tool must not use protected attributes as features by default (age flagged as optional). Synthetic results demonstrate method behaviour, not real-world profit.

## 14. How to Run (target README quick-start)
```bash
uv sync && make setup
make demo              # data → train → evaluate → audit → optimise → reports
make api &             # http://localhost:8000/docs
make web               # http://localhost:5173
```
