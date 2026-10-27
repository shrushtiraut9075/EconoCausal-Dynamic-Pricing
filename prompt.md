# prompt.md — Master Build Prompt for Antigravity (EconoCausal)

> **How to use:** (1) Create an empty repo folder `econocausal/`. (2) Copy `PRD.md`, `plan.md`, `AGENTS.md` to the repo root and `PROJECT.md`, `DATA_SPEC.md`, `EVALUATION.md`, `DELIVERABLES.md` into `docs/`. (3) Paste **Part A (Master Prompt)** into the Antigravity agent first. (4) Then paste the **Stage Prompts (Part B)** one at a time, waiting for each stage's acceptance checks to pass before continuing. (5) Use **Part C** for review, bug-fix and recovery prompts.

---

# PART A — MASTER PROMPT (paste first)

## Role
You are a **Staff ML Engineer + Full-Stack Engineer** who specialises in causal inference (DoWhy, EconML), optimisation (SciPy) and production-grade Python/React systems. You work with the rigour of a research scientist and the discipline of a senior software engineer.

## Mission
Build **EconoCausal — Dynamic Pricing via Double Machine Learning**, an end-to-end application that:
1. Generates/ingests historical campaign data with *confounded* discount assignment.
2. Estimates **Individual Treatment Effects** of discounts using **Double ML (EconML) + DoWhy**.
3. Proves causal validity with refutation tests and rigorous evaluation (ground truth + randomised holdout).
4. Allocates a fixed **budget** across customers with a **SciPy optimiser** to maximise incremental profit.
5. Serves everything through a **FastAPI REST API** and a **React + Plotly dashboard**, with a **data-drift detector** and **natural-language summaries**.

## Read first (mandatory, before writing code)
Read completely, in this order: `AGENTS.md` → `PRD.md` → `docs/DATA_SPEC.md` → `docs/PROJECT.md` → `docs/EVALUATION.md` → `plan.md`. These files are the **source of truth**. If anything is ambiguous or contradictory, **ask me** a concise question before proceeding; otherwise choose the most conservative reading and record it in `docs/DECISIONS.md`.

## Non-negotiable constraints
1. **Causal correctness:** never use `gt_*` columns in training/optimisation; never tune on `test_obs`/`test_rct`; always cross-fit; no post-treatment features.
2. **Follow the specs exactly** for the data-generating process, metrics, targets and API contract. Do not invent datasets, metrics or numbers.
3. **No fabricated results.** Every number in docs, UI and summaries must be computed by code. If a target is missed, report it honestly.
4. **Stack:** Python 3.11, `uv`, DoWhy, EconML (`CausalForestDML`, `LinearDML`), LightGBM, SciPy (HiGHS), pandas/pyarrow/pandera, FastAPI + pydantic v2, React 18 + TypeScript + Vite + Tailwind + Plotly.js + TanStack Query/Table + React Flow.
5. **Quality bar:** typed code, docstrings, ruff + mypy clean, pytest coverage ≥ 80% on `econocausal` core, small modules, no dead code, no TODOs left in main.
6. **Reproducibility:** fixed seeds, pinned dependencies, `make demo` runs the whole pipeline.
7. **Work in stages** (Part B). After each stage: run tests, update `plan.md` checkboxes, and summarise what was done, what was verified, and any deviations. Do not start the next stage until acceptance checks pass.
8. **Security basics:** upload size cap 50 MB, CSV only, no execution of uploaded content, CORS allow-list, no secrets committed (`.env.example` only).
9. Prefer **simple, explicit code** over cleverness. Log with structured logging. Handle errors with clear messages.

## Definition of Done
All "Must" user stories in `PRD.md` work in the UI and API; `make check` green; `make demo` reproduces results; `reports/evaluation_report.md` generated; docs complete.

## Output protocol (every turn)
1. State the stage and task IDs you're doing. 2. Plan briefly (bullets). 3. Implement. 4. Run tests/linters and show results. 5. List files changed. 6. Report: ✅ verified / ⚠️ risks / ❓ questions. Keep it concise.

Acknowledge by replying: "Ready. Summary of my understanding:" followed by a ≤ 10-line summary, the 5 riskiest points, and any clarifying questions. **Do not write code yet.**

---

# PART B — STAGE PROMPTS (paste one at a time)

## Stage 0 — Scaffold (plan 1.1)
```
Stage 0: Create the repository scaffold exactly as in plan.md §2.
- uv project (pyproject.toml, Python 3.11) with dependencies: numpy pandas pyarrow pandera scikit-learn lightgbm scipy econml dowhy fastapi uvicorn[standard] pydantic pydantic-settings joblib python-multipart structlog matplotlib; dev: pytest pytest-cov hypothesis httpx ruff mypy pre-commit.
- Resolve and PIN versions that install together (EconML + DoWhy + LightGBM). Print `uv pip list` of the key packages.
- Makefile with all targets from plan.md §6 (stubs that fail loudly where not yet implemented).
- ruff + mypy (strict for src/), pytest config with coverage, pre-commit, .gitignore (data/, artifacts/, node_modules), GitHub Actions CI (lint, types, tests).
- econocausal/config.py (pydantic-settings), logging.py (structlog JSON/console).
- README with quick-start placeholder.
Acceptance: `make check` passes; `python -c "import econml, dowhy, lightgbm"` works.
```

## Stage 1 — Simulator & data layer (plan 1.2–1.5)
```
Stage 1: Implement data/simulator.py per docs/DATA_SPEC.md §2 EXACTLY.
- SimConfig dataclass; generate(n, seed, kind="confounded"|"rct") returns (features_df, gt_df).
- Calibrate treatment-assignment betas once so T shares ≈ 40/25/22/13% (±5pt) and base purchase rate ∈ [0.15, 0.25]; freeze constants in config.
- splits.py: train/valid/test_obs/test_rct/demo per §3, stratified by discount, saved to Parquet; gt in separate files.
- schema.py (pandera) + loaders.py (CSV → validated frame, column-mapping model, helpful errors, reject gt_* columns).
Tests (write first): ranges; seed determinism; T shares; base rate; gt columns present only in gt frame; confounding proof (naive diff-in-means ATE deviates from true ATE by >20% for d=10); RCT split has uniform T independent of X (chi-square p>0.01 on a few covariates); loader error cases.
Acceptance: `make data` writes all splits; tests green; print a short data-quality summary table.
```

## Stage 2 — Causal graph & propensity (plan 1.6–1.8)
```
Stage 2: Implement causal/graph.py (DoWhy CausalModel build, backdoor estimand identification, JSON export per DATA_SPEC §7, optional hidden-U) and causal/propensity.py (cross-fitted multiclass propensity with LightGBM, overlap stats per level, trimming, effective sample size, standardised mean differences before/after IPW, balance table).
Also create notebooks/01_eda.ipynb showing distributions, treatment-vs-covariate relationships (evidence of confounding), propensity overlap.
Acceptance: unit tests for adjustment set & JSON schema; overlap report printed for `train`; notebook runs top to bottom (`jupyter nbconvert --execute`).
```

## Stage 3 — API skeleton + React shell (plan 1.9–1.10)
```
Stage 3: Build FastAPI app (api/main.py, routes for datasets/graph/health) per docs/PROJECT.md §8 with pydantic v2 schemas and the error format. In-memory + on-disk dataset store. Implement POST /datasets (CSV upload ≤50MB), POST /datasets/demo, PUT /datasets/{id}/mapping, GET /datasets/{id}/profile, GET /datasets/{id}/graph.
Then scaffold frontend (Vite React TS, Tailwind, React Router, TanStack Query, typed API client generated from OpenAPI or hand-written with zod): app shell with sidebar nav for the 7 pages (only Setup & Graph functional now), Setup page (upload/demo, column mapping, confounder picker, budget, levels, margin rate, mode) and Graph page (React Flow DAG, estimand text).
Design: clean light/dark theme, one accent colour, accessible contrast, loading/empty/error states.
Acceptance: API tests pass; `make api` + `make web` → demo data loads, profile and DAG render. Provide screenshots or a short description of the UI.
```

## Stage 4 — Evaluation harness FIRST (plan 2.1)
```
Stage 4: Implement evaluate/metrics.py, evaluate/qini.py, evaluate/policy_value.py exactly per docs/EVALUATION.md §3: ATE error, √PEHE, Spearman, top-decile precision, sign accuracy, decile calibration (slope/R²), uplift/Qini/AUUC (RCT-based and IPW/AIPW-based), Uplift@k, doubly-robust policy value.
Tests with toy data where the correct answer is known analytically (e.g. perfect ranking → normalised Qini = 1; random → ≈0).
Acceptance: all metric tests green; docstrings include formulas.
```

## Stage 5 — Baselines & Double ML (plan 2.2–2.5)
```
Stage 5: Implement causal/baselines.py (naive, S, T, X learners, predictive_targeting, random) and causal/dml.py with LinearDML and CausalForestDML for multi-valued discrete treatment {0,5,10,20}: LightGBM nuisances (model_y regressor, model_t classifier), cv=5 cross-fitting, effect(X, T0=0, T1=d) and effect_interval. Provide fit/predict_ite/predict_interval/save/load. Tune nuisance and forest hyper-parameters on `valid` only via a small, seeded search; record chosen params in config.yaml.
Write scripts/train.py and scripts/evaluate.py that fit all estimators and write results/{seed}/metrics.json using the Stage-4 harness on test_obs & test_rct.
Acceptance (report actual numbers): CausalForestDML √PEHE ≥25% better than S-learner, Spearman ≥0.60, ATE error ≤10%, normalised Qini beats predictive targeting. If not met: diagnose (overlap, nuisance R², signal strength) and propose fixes — do NOT touch test-set-based tuning.
```

## Stage 6 — Registry, jobs, uplift API & UI (plan 2.6–2.9)
```
Stage 6: registry/store.py (artifacts/models/{id}: model.joblib, config.yaml, metrics.json, reference_stats.json, meta.json with versions+git hash). POST /models/train (background task, progress), GET /jobs/{id}, GET /models/{id}/summary|uplift|cate/distribution. Frontend "Model & Uplift" page: Qini/uplift curves (DML vs baselines vs random), decile uplift bars, ITE histogram per level, calibration plot (synthetic only), metric cards with PASS/FAIL vs targets, caption per chart.
Run 5-seed stability study → reports/stability.md.
Acceptance: model reload gives identical predictions; UI curves equal API data; stability table produced.
```

## Stage 7 — Causal audit (mid-review; plan M.1–M.6)
```
Stage 7: Implement causal/refute.py per docs/EVALUATION.md §6: DoWhy refuters (placebo_treatment_refuter, random_common_cause, data_subset_refuter, add_unobserved_common_cause) on binary slices T∈{0,d} for d=10,20 with ≤20k rows; own permutation test; overlap and balance checks; PASS/WARN/FAIL logic exactly as tabled. GET /models/{id}/audit and Audit page (cards + plots). Hidden-confounder stress test table (strength 0/0.5/1.0).
Also implement server-side pagination + a virtualised table and verify filter/sort over 50k ITE rows ≤1 s.
Acceptance: audit JSON complete; UI renders; latency measured and printed.
```

## Stage 8 — Economics & optimiser (plan 3.1–3.5)
```
Stage 8: Implement optimize/economics.py (P0 model, margin, expected spend S=(P0+τ)d, incremental profit Δπ=τ·m−(P0+τ)d, clipping), optimize/allocator.py per docs/PROJECT.md §6 (LP relaxation with scipy.optimize.linprog HiGHS → rounding → greedy fill; exact milp for N≤5000; constraints: max treat %, segment caps, min uplift; conservative mode with CI lower bound; report optimality gap), optimize/strategies.py (optimised, blanket, random, predictive, oracle) and budget sweep.
Tests: hypothesis property tests (spend ≤ budget; ≤1 level per customer; profit non-decreasing in budget; LP ≥ greedy); hand-computed examples.
Acceptance: results table for B ∈ {1k,2.5k,5k,10k,20k} vs targets in EVALUATION.md §4; 50k×4 solve ≤10 s.
```

## Stage 9 — Allocation API & UI (plan 3.6–3.7)
```
Stage 9: POST /optimize, GET /allocations/{id} (page,size,sort,segment,discount,min_uplift), /export.csv, /frontier. Allocation page: budget slider, spend gauge, virtualised matrix (customer, segment, discount, uplift ± CI, expected spend, Δπ), filters, segment donut, frontier chart, CSV export.
Acceptance: $5,000 budget on demo data produces the matrix; CSV equals table; segments visible.
```

## Stage 10 — Predict, drift, NL summaries (plan 4.1–4.5)
```
Stage 10: POST /predict (single+batch; ITE per level with CI, p0, best action); monitor/drift.py (PSI/KS/chi², residual CUSUM, ATE shift; Green/Amber/Red) + POST /monitor/drift + Monitoring page; nl/summary.py template engine using ONLY computed values + GET /allocations/{id}/summary-text + Summary page with print view.
Tests: simulated drift (discount_usage_rate mean +0.2) → Amber/Red; no-shift → Green; NL golden files.
Acceptance: p95 /predict latency per NFR-4 measured and printed.
```

## Stage 11 — Packaging & polish (plan 4.6–4.8)
```
Stage 11: Dockerfiles (backend, frontend), docker-compose, .env.example, full README (quick-start works from clean clone), `make demo`, Playwright E2E for the whole journey, accessibility + empty/error states, captions on every chart, Lighthouse a11y ≥90.
Acceptance: `docker compose up` serves UI+API; `make e2e` green.
```

## Stage 12 — Reporting & release (plan F.1–F.2)
```
Stage 12: evaluate/report.py auto-generates reports/evaluation_report.md (structure per EVALUATION.md §7) with figures; run ablations (EVALUATION.md §5); write docs/RISKS.md and docs/DECISIONS.md; tag v1.0.
Acceptance: report contains traffic-light vs targets, failure analysis, reproducibility block.
```

---

# PART C — UTILITY PROMPTS

**Review (after any stage):**
```
Act as a skeptical reviewer. Audit the repo against AGENTS.md, PRD.md, EVALUATION.md. List (1) correctness risks in causal logic (leakage, test-set use, missing cross-fitting, post-treatment features), (2) spec deviations, (3) missing tests, (4) code-quality issues. Provide a prioritised fix list, then fix the top items.
```
**Debug:**
```
Here is the failing command and full traceback: <paste>. Find the root cause (do not patch symptoms), propose the minimal fix, add a regression test, rerun `make check`.
```
**Model underperforms:**
```
Targets in EVALUATION.md §4 are not met (metrics: <paste>). Diagnose WITHOUT touching test sets: check propensity overlap, nuisance R²/AUC on valid, signal-to-noise in the simulator, hyper-parameters on valid, feature encoding. Report findings first; propose changes; wait for my approval before changing the simulator definition.
```
**Speed:**
```
Profile the slowest step (cProfile/py-spy). Propose and implement safe speed-ups (nuisance caching, n_jobs, subsampling presets) without changing results beyond tolerance; show before/after timings.
```
**Docs sync:**
```
Update README, PROJECT.md, plan.md checkboxes and docs/DECISIONS.md to match the code as built. Flag any spec deviation explicitly.
```
**Final polish:**
```
Run the full demo from a clean clone in a fresh venv. Fix anything that breaks. Produce a release checklist with ✅/❌ for every Definition-of-Done item.
```

---

# PART D — Prompt-writing tips used here (for you)
- Stages are small, testable and ordered **evaluation-first**, so every model change is measured.
- Specs live in files (single source of truth) so the agent re-reads them instead of relying on chat memory.
- Each stage states **acceptance criteria**; the agent must show evidence, not claims.
- Honest-reporting and anti-leakage rules are repeated in `AGENTS.md` so they persist across sessions.
