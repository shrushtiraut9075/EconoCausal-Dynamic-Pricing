# EconoCausal Makefile
# Usage: make <target>
# Run `make help` for a list of all targets.

PYTHON := python
PYTEST := pytest
UV := uv
BACKEND_SRC := backend/src
SCRIPTS := backend/scripts

# Default budget for optimise target
BUDGET ?= 5000
SEED   ?= 42
N      ?= 100000
DEMO_N ?= 20000

.PHONY: help setup data train evaluate audit optimize api web demo \
        check lint types test e2e docker-up docker-down clean

##──────────────────────────────────────────────────────────────────────────────
## Help
##──────────────────────────────────────────────────────────────────────────────
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

##──────────────────────────────────────────────────────────────────────────────
## Environment
##──────────────────────────────────────────────────────────────────────────────
setup:  ## Install all dependencies with uv
	$(UV) sync --extra dev
	@echo "✅ Dependencies installed"
	$(PYTHON) -c "import econml, dowhy, lightgbm; print('Core imports OK')"

##──────────────────────────────────────────────────────────────────────────────
## Data
##──────────────────────────────────────────────────────────────────────────────
data:  ## Generate synthetic data splits (100k rows, 5 seeds)
	$(UV) run python $(SCRIPTS)/generate_data.py --n $(N) --seeds 11 22 33 44 55
	@echo "✅ Data splits written to data/processed/"

data-demo:  ## Generate small demo dataset (20k rows, seed 42)
	$(UV) run python $(SCRIPTS)/generate_data.py --n $(DEMO_N) --seeds $(SEED) --splits demo
	@echo "✅ Demo data written"

##──────────────────────────────────────────────────────────────────────────────
## Model
##──────────────────────────────────────────────────────────────────────────────
train:  ## Train all estimators (DML + baselines) on seed 42
	$(UV) run python $(SCRIPTS)/train.py --seed $(SEED)
	@echo "✅ Model trained; see artifacts/models/"

##──────────────────────────────────────────────────────────────────────────────
## Evaluation
##──────────────────────────────────────────────────────────────────────────────
evaluate:  ## Run full evaluation on all 5 seeds → reports/evaluation_report.md
	$(UV) run python $(SCRIPTS)/evaluate.py --seeds 11 22 33 44 55
	@echo "✅ Evaluation report written to reports/evaluation_report.md"

##──────────────────────────────────────────────────────────────────────────────
## Causal audit
##──────────────────────────────────────────────────────────────────────────────
audit:  ## Run causal refutation tests on the latest model
	$(UV) run python $(SCRIPTS)/run_pipeline.py --step audit --seed $(SEED)
	@echo "✅ Audit complete; results in artifacts/models/latest/audit.json"

##──────────────────────────────────────────────────────────────────────────────
## Optimiser
##──────────────────────────────────────────────────────────────────────────────
optimize:  ## Run budget optimiser (set BUDGET=N, default 5000)
	$(UV) run python $(SCRIPTS)/run_pipeline.py --step optimize --budget $(BUDGET) --seed $(SEED)
	@echo "✅ Allocation written to artifacts/allocations/"

##──────────────────────────────────────────────────────────────────────────────
## API & frontend
##──────────────────────────────────────────────────────────────────────────────
api:  ## Start FastAPI backend on localhost:8000
	$(UV) run uvicorn econocausal.api.main:app --host 0.0.0.0 --port 8000 --reload

web:  ## Start React dev server on localhost:5173
	cd frontend && npm run dev

##──────────────────────────────────────────────────────────────────────────────
## Full demo pipeline
##──────────────────────────────────────────────────────────────────────────────
demo:  ## End-to-end demo: data→train→evaluate→audit→optimize→report
	@echo "=== EconoCausal Demo Pipeline ==="
	$(MAKE) data-demo
	$(MAKE) train SEED=$(SEED)
	$(UV) run python $(SCRIPTS)/evaluate.py --seeds $(SEED) --quick
	$(MAKE) audit SEED=$(SEED)
	$(MAKE) optimize BUDGET=$(BUDGET) SEED=$(SEED)
	$(UV) run python $(SCRIPTS)/run_pipeline.py --step report --seed $(SEED)
	@echo "=== Demo complete! ==="
	@echo "API: make api | Frontend: make web"

##──────────────────────────────────────────────────────────────────────────────
## Quality
##──────────────────────────────────────────────────────────────────────────────
lint:  ## Run ruff linter + formatter check
	$(UV) run ruff check backend/src backend/tests backend/scripts
	$(UV) run ruff format --check backend/src backend/tests backend/scripts
	@echo "✅ Lint OK"

lint-fix:  ## Auto-fix lint issues
	$(UV) run ruff check --fix backend/src backend/tests backend/scripts
	$(UV) run ruff format backend/src backend/tests backend/scripts

types:  ## Run mypy type checker
	$(UV) run mypy backend/src/econocausal --config-file pyproject.toml
	@echo "✅ Types OK"

test:  ## Run pytest with coverage
	$(UV) run pytest backend/tests -v
	@echo "✅ Tests OK"

test-unit:  ## Run only unit tests (fast)
	$(UV) run pytest backend/tests/unit -v --no-cov

test-leakage:  ## Run leakage-guard tests
	$(UV) run pytest backend/tests -k leakage -v --no-cov

check:  ## Full quality check: lint + types + tests (must pass before every PR)
	$(MAKE) lint
	$(MAKE) types
	$(MAKE) test
	@echo "✅ All checks passed"

e2e:  ## Run Playwright end-to-end tests
	cd frontend && npx playwright test
	@echo "✅ E2E tests passed"

##──────────────────────────────────────────────────────────────────────────────
## Docker
##──────────────────────────────────────────────────────────────────────────────
docker-up:  ## Build and start Docker services (backend + frontend)
	docker compose up --build -d
	@echo "✅ Services up: API at http://localhost:8000 | UI at http://localhost:5173"

docker-down:  ## Stop Docker services
	docker compose down

##──────────────────────────────────────────────────────────────────────────────
## Cleanup
##──────────────────────────────────────────────────────────────────────────────
clean:  ## Remove generated data, models, reports (keeps .gitkeep)
	find data/processed -name "*.parquet" -delete 2>/dev/null; true
	find artifacts/models -name "*.joblib" -delete 2>/dev/null; true
	find reports -name "*.md" -not -name "README.md" -delete 2>/dev/null; true
	@echo "✅ Clean"
