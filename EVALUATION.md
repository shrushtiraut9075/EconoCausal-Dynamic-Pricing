# EVALUATION.md — EconoCausal Evaluation Protocol

Goal: show, with rigorous and honest evidence, that EconoCausal (a) estimates individual causal effects accurately, (b) beats correlation-based targeting, (c) is robust to refutation, and (d) yields more profit per budget dollar.

## 1. Principles
1. **Three layers of evidence:** ground-truth (synthetic), randomised holdout (`test_rct`, unbiased), refutation/sensitivity (DoWhy).
2. **Tune on `valid` only.** `test_obs` and `test_rct` are touched once per experiment run, by the evaluation script. A unit test asserts tuning code never receives them.
3. **Report mean ± SD over 5 seeds** (11, 22, 33, 44, 55) plus bootstrap 95% CIs (500 resamples) for headline metrics.
4. **Pre-registered targets** (PRD §8). Missed targets are reported, diagnosed, not hidden.
5. Every report records: git hash, package versions, seed, config, runtime.

## 2. Estimators compared
| Name | Description |
|---|---|
| `naive` | difference in mean outcome treated vs control (confounded) |
| `s_learner` | LightGBM on [X, T] |
| `t_learner` | separate LightGBM per arm |
| `x_learner` | EconML XLearner |
| `linear_dml` | EconML LinearDML, LightGBM nuisances |
| **`causal_forest_dml`** | **EconML CausalForestDML (primary)** |
| `predictive_targeting` | rank by `P(buy\|X, no discount)` low→high or risk-style; gives *no* causal info (policy baseline) |
| `random` | uniform random targeting |
| `oracle` | uses `gt_ite` (upper bound; synthetic only) |

## 3. Metrics

### 3.1 Effect-estimation accuracy (synthetic, on `test_obs`, per discount level d ∈ {5,10,20})
| Metric | Definition |
|---|---|
| **ATE error** | `|mean(τ̂_d) − mean(τ_d)| / |mean(τ_d)|`; also CI coverage of true ATE (via bootstrap or `ate_interval`) |
| **√PEHE** | `sqrt(mean((τ̂_d(x) − τ_d(x))²))` |
| **Spearman ρ** | rank correlation of `τ̂` vs `τ` |
| **Top-decile precision** | share of the true top-10% responders captured in predicted top-10% |
| **Sign accuracy** | `mean(sign(τ̂)=sign(τ))` among `|τ|>0.02` |
| **Calibration by decile** | bin by `τ̂`; plot mean `τ̂` vs mean true `τ` (slope ≈ 1, intercept ≈ 0); report slope/R² |
| **CI coverage (individual)** | share of rows where true `τ` ∈ `effect_interval` (target 80–95% for 90% CI; report even if lower) |

### 3.2 Ranking / uplift quality (on `test_rct`, unbiased)
| Metric | Definition |
|---|---|
| **Uplift curve** | cumulative incremental purchases vs fraction targeted, ranked by `τ̂` |
| **Qini curve & coefficient** | area between uplift curve and random line; **normalised Qini** = Qini / Qini of oracle (synthetic) |
| **AUUC** | area under uplift curve |
| **Uplift@k** | observed (treated − control purchase rate) in top-k% (k = 10, 20, 30) |
For multi-level T compare each level d vs control using RCT arms; also a combined score using best-level `τ̂`.
On *confounded* data (real uploads) compute **IPW-/AIPW-weighted Qini** instead; label clearly.

### 3.3 Nuisance model quality (train CV / `valid`)
Outcome model: R², log-loss/Brier on binary Y. Treatment model: multiclass AUC (one-vs-rest), log-loss. Report **residual-on-residual R²** (first-stage strength) and propensity overlap.

### 3.4 Policy / business value
Evaluated at budgets `B ∈ {1k, 2.5k, 5k, 10k, 20k}` on `test_obs` customers (scaled to the test population):
| Metric | How (synthetic) |
|---|---|
| **True incremental profit** | using `gt_p*` and economics formulas (DATA_SPEC §2 Step 7) |
| **Doubly-robust policy value** | on `test_rct` for estimator-independent confirmation |
| **Spend ≤ budget** | must be 100% true (using *true* expected spend, report overshoot if any) |
| **% oracle value captured** | `profit(policy)/profit(oracle policy)` |
| **Lift vs blanket** | profit difference vs spending same budget evenly on random customers at $10 |
| **Lift vs predictive** | profit difference vs best predictive-targeting policy at same budget |
| **Efficiency frontier** | profit vs budget curve for each strategy |
| **Segment mix of treated** | % Persuadable/Sure Thing/Lost Cause/Sleeping Dog (true segments) |

## 4. Targets (pass criteria)
Copied from PRD §8, evaluated on mean over 5 seeds:

| Metric | Target | Stretch |
|---|---|---|
| ATE rel. error (each d) | ≤ 10% | ≤ 5% |
| √PEHE vs S-learner | ≥ 25% lower | ≥ 40% |
| Spearman | ≥ 0.60 | ≥ 0.75 |
| Normalised Qini (RCT) | > predictive targeting & > random | ≥ 1.5× predictive |
| Profit vs blanket (B=5k) | ≥ +25% | ≥ +50% |
| Profit vs predictive (B=5k) | ≥ +15% | ≥ +30% |
| % oracle value | ≥ 80% | ≥ 90% |
| Budget compliance | 100% | — |

## 5. Ablations & Sensitivity (each a row in the report)
1. Nuisance learner: LightGBM vs RandomForest vs linear.
2. Cross-fitting folds: 2, 5, 10.
3. Sample size: n ∈ {5k, 10k, 20k, 50k, 70k} learning curve (√PEHE vs n).
4. Confounding strength: scale assignment betas ×{0, 0.5, 1, 2} (naive degrades, DML should not).
5. Overlap trimming: 0.01 / 0.02 / 0.05.
6. Hidden confounder strength ∈ {0, 0.5, 1.0}: show where DML breaks (honest limitation).
7. Feature ablation: remove key confounder (`days_since_last_purchase`) to show bias appears.
8. CausalForest vs LinearDML (interpretability/accuracy trade-off).
9. Conservative vs standard allocation (profit vs risk of treating Sleeping Dogs).

## 6. Causal Audit (refutation) — DoWhy
Run on binary slices (`T∈{0,d}`) for d = 10 and 20; subsample ≤ 20k rows; `num_simulations` 30–50. Estimator: LinearDML via `backdoor.econml.dml.LinearDML` (CausalForest used for ITE; ATE agreement between the two is also reported).

| Test | Procedure | PASS | WARN | FAIL |
|---|---|---|---|---|
| **Placebo treatment** | replace T by random permutation | new ATE CI contains 0 | CI borders 0 (p 0.05–0.10) | CI excludes 0 |
| **Random common cause** | add random confounder | ATE change ≤ 5% | 5–10% | > 10% |
| **Data subset** | 80% random subsets | ATE change ≤ 10% and CI overlaps | 10–20% | > 20% |
| **Unobserved common cause** | simulate confounder with effect strengths grid on T and Y | ATE sign unchanged at moderate strength (partial R² ≈ 0.05) | sign flips at ~0.05 | sign flips at < 0.02 |
| **Own permutation test** | permute T 200× and compare CATE-based Qini to null | observed Qini > 95th pct of null | 90–95 | < 90 |
| **Overlap/positivity** | share outside [0.02, 0.98] | ≤ 10% | 10–25% | > 25% |
| **Covariate balance** | max SMD after weighting | < 0.1 | 0.1–0.2 | > 0.2 |
Audit status is stored in `metrics.json` and rendered in UI.

## 7. Evaluation Pipeline
```
make evaluate
 ├─ load splits (+ gt files) for seed s
 ├─ fit estimators on train; tune on valid
 ├─ predict τ̂ on test_obs, test_rct
 ├─ compute §3 metrics → results/{seed}/metrics.json
 ├─ build allocations at each budget; compute policy values
 ├─ aggregate seeds → reports/evaluation_report.md + figures/*.png + results.csv
 └─ compare to reports/baseline_metrics.json (fail on regression > 10%)
```

### Report structure (auto-generated `reports/evaluation_report.md`)
1. Executive summary (traffic-light table vs targets)
2. Setup (data sizes, seeds, versions)
3. Effect accuracy table (all estimators × metrics, mean ± sd)
4. Calibration plots, ITE scatter
5. Uplift/Qini curves on RCT
6. Policy value & frontier
7. Ablations / sensitivity
8. Causal audit results
9. Failure analysis & limitations (mandatory, even if all pass)
10. Reproducibility block

## 8. Figures (for report & PPT)
Qini curves; uplift-by-decile bars; predicted-vs-true ITE calibration; ITE histograms by level; profit-vs-budget frontier; segment composition of treated customers (optimised vs predictive vs blanket); refutation distributions; propensity overlap; learning curve; confounding-strength sweep. Use a consistent colour-blind-safe palette; label axes; one-sentence caption each.

## 9. Common Pitfalls (checklist)
- [ ] No `gt_*` in features · [ ] No test data in tuning · [ ] Cross-fitting used (out-of-fold nuisances) · [ ] No post-treatment variables · [ ] Qini computed on RCT/IPW (not confounded raw data) · [ ] Probabilities clipped to [0,1] · [ ] Spend uses `(P0+τ)·d`, not `d` for everyone · [ ] Seeds fixed · [ ] Same budget compared across strategies · [ ] Intervals reported, not only point estimates
