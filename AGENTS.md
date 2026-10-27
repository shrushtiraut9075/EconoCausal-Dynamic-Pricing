# AGENTS.md — Rules for AI Agents Working on EconoCausal

> Place at the repo root (and, if your IDE supports workspace rules, copy into `.agent/rules/`). Agents must read this file at the start of every session.

## 0. Project in one line
Causal-AI pricing engine: Double ML (EconML + DoWhy) estimates per-customer discount effects; a SciPy optimiser allocates a fixed budget; FastAPI + React/Plotly deliver it. Source of truth: `PRD.md`, `docs/DATA_SPEC.md`, `docs/PROJECT.md`, `docs/EVALUATION.md`, `plan.md`.

## 1. DO ✅

### Causal & ML correctness
- DO use **cross-fitting** (K≥5) for all nuisance models; use out-of-fold predictions only.
- DO adjust only for **pre-treatment** covariates.
- DO keep `gt_*` columns in the evaluation code path only.
- DO tune hyper-parameters on `valid` only; touch `test_obs`/`test_rct` only in the evaluation script.
- DO check overlap (positivity) and balance before trusting estimates; report ESS.
- DO report confidence/uncertainty intervals with every effect estimate.
- DO compute Qini/uplift on the **randomised holdout** (or IPW/AIPW-weighted data), never on raw confounded data.
- DO compare against baselines (naive, S/T/X-learner, predictive targeting, random) every time.
- DO fix random seeds (`numpy.random.default_rng`, LightGBM `random_state`, EconML `random_state`) and log them.
- DO clip probabilities to [0,1] and compute spend as `(P0+τ)·d`.
- DO state assumptions (unconfoundedness, overlap, SUTVA) in docs and the UI.

### Engineering
- DO write tests **first** for new modules; keep coverage ≥ 80% on `econocausal` core.
- DO use type hints everywhere in `src/`; keep functions small and pure where possible.
- DO write docstrings (purpose, args, returns, formulas for metrics).
- DO use pydantic v2 models for all API I/O and config; return the standard error format.
- DO paginate/aggregate server-side for large result sets (50k+ rows).
- DO use structured logging; never `print` in library code.
- DO commit small, with Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`) on `feat/<task-id>-name` branches.
- DO run `make check` before declaring any task done; show the output.
- DO update `plan.md` checkboxes and `docs/DECISIONS.md` when you choose between alternatives.
- DO ask a concise clarifying question when a spec is ambiguous or contradictory.
- DO add a one-line takeaway caption under every chart; label axes and units.
- DO keep the UI accessible (contrast, keyboard focus, aria labels) and handle loading/empty/error states.

### Reporting
- DO report numbers exactly as computed, with seeds, sample sizes and CIs.
- DO include a failure analysis when a target is missed.
- DO summarise each work session: ✅ verified, ⚠️ risks, ❓ open questions.

## 2. DON'T ❌

### Causal & ML correctness
- DON'T train, tune or select models using ground-truth (`gt_*`) columns or test splits.
- DON'T include treatment-derived or post-treatment variables (e.g. `order_value`) as covariates.
- DON'T interpret predictive-model scores as causal effects.
- DON'T report ATE/ITE without checking overlap and refutation results.
- DON'T "improve" metrics by altering the simulator after seeing test results. Changing the DGP requires explicit approval and a note in `DECISIONS.md`; regenerate all splits afterwards.
- DON'T silently fall back to a different estimator or drop rows; log and surface it.
- DON'T hard-code results, thresholds-met flags or numbers in UI/summary text.
- DON'T use protected attributes for targeting by default (age is optional and flagged).

### Engineering
- DON'T add dependencies without justification and pinning; DON'T upgrade EconML/DoWhy casually.
- DON'T commit data, model artifacts, notebooks with huge outputs, secrets, or `.env`.
- DON'T leave TODO/FIXME, commented-out code, or dead code in `main`.
- DON'T use broad `except:`; catch specific exceptions and give actionable messages.
- DON'T run uploaded files or evaluate their content; CSV parsing only, with size limits.
- DON'T block the API event loop with training; use background jobs.
- DON'T make breaking API changes without updating `docs/PROJECT.md §8`, OpenAPI examples and the frontend client.
- DON'T invent datasets, benchmarks or citations. Public datasets must be downloaded via the script and cited with their source/licence.
- DON'T use an LLM to generate numbers; templates only (LLM narrative is an optional stretch and must be labelled).

### Process
- DON'T start the next stage before acceptance checks of the current stage pass.
- DON'T expand scope beyond "Must" items until all Must items are green.
- DON'T rewrite large parts of the codebase without a written plan and approval.

## 3. Code conventions
- Python: ruff (format + lint), mypy strict on `src/`, Google-style docstrings, snake_case, max function length ~50 lines.
- TypeScript: strict mode, ESLint + Prettier, functional components, hooks, no `any`.
- Naming: `ite`/`tau` = individual treatment effect (probability points); `p0` = baseline purchase prob; `d` = discount in USD; `B` = budget.
- Files: one concern per module; public API exported in `__init__.py`.
- Config via `pydantic-settings`; no magic numbers (put in `config.py` or YAML).

## 4. Definition of Done (per task)
1. Behaviour matches spec. 2. Tests added and passing. 3. `make check` green. 4. Docs/plan updated. 5. No leakage (leakage tests pass). 6. Summary posted (✅/⚠️/❓).

## 5. Communication protocol
- Be concise. Lead with the result. Show evidence (command output, metrics table).
- When blocked or unsure: stop and ask one specific question with 2–3 options and a recommendation.
- Never claim something works without running it.

## 6. Escalate / ask before:
- Changing the data-generating process, targets or metric definitions.
- Swapping core libraries (EconML/DoWhy/SciPy/React/Plotly).
- Anything touching security (uploads, CORS, auth).
- Deleting or renaming public API endpoints.

## 7. Useful commands
`make setup` · `make data` · `make train` · `make evaluate` · `make audit` · `make optimize BUDGET=5000` · `make api` · `make web` · `make demo` · `make check` · `make e2e`

## 8. Your additions (project owner)
> Add your own project-specific dos/don'ts below; they override the defaults above if they conflict.

### Additional DOs
- …

### Additional DON'Ts
- …
