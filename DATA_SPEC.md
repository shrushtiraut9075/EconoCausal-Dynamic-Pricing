# DATA_SPEC — EconoCausal

Two data sources are used:

1. **Primary — Synthetic retail simulator** with *known ground-truth* individual effects and *confounded* historical discount assignment. This is what lets us measure real causal accuracy (PEHE, ATE error, oracle policy value). The assignment letter asks for a "mock retail dataset".
2. **Secondary (stretch) — Real public uplift data** (Hillstrom MineThatData email dataset, ~64k rows; or a Criteo Uplift sample) for a real-world Qini sanity check. These are randomised, so we can also *inject* confounding by biased subsampling to test DML.

> Hard rule: columns prefixed `gt_` (ground truth) exist **only** for evaluation. They must never enter training, feature lists, nuisance models, or the optimiser.

---

## 1. Entities & Columns (synthetic)

Row = one customer in one campaign window (14-day outcome window).

### 1.1 Identifiers & treatment/outcome
| Column | Type | Description |
|---|---|---|
| `customer_id` | str | Unique ID `C000001…` |
| `discount_usd` | int ∈ {0, 5, 10, 20} | **Treatment T** — discount offered. 0 = control |
| `purchased_14d` | int ∈ {0,1} | **Outcome Y** — purchased within 14 days |
| `order_value` | float ≥ 0 | Realised order value (0 if no purchase) |

### 1.2 Observed covariates X (features & confounders)
| Column | Type | Range / values | Notes |
|---|---|---|---|
| `age` | int | 18–75 | |
| `tenure_months` | int | 1–120 | |
| `loyalty_tier` | cat | bronze, silver, gold, platinum | ordinal-encoded in models |
| `past_purchases_12m` | int | 0–60 | |
| `avg_order_value` | float | 15–400 | used for margin |
| `days_since_last_purchase` | int | 0–365 | key lapse signal |
| `site_visits_30d` | int | 0–80 | engagement proxy |
| `email_open_rate` | float | 0–1 | engagement proxy |
| `discount_usage_rate` | float | 0–1 | price-sensitivity proxy |
| `cart_abandon_rate` | float | 0–1 | |
| `device` | cat | mobile, desktop, tablet | |
| `region` | cat | north, south, east, west, central | near-noise feature |
| `category_affinity` | cat | fashion, electronics, home, beauty, grocery | |

### 1.3 Latent variables (generated, **never exported** to feature files)
`z_engagement ~ N(0,1)`, `z_price ~ N(0,1)`, optional hidden confounder `u ~ N(0,1)`.

### 1.4 Ground-truth columns (evaluation only)
| Column | Description |
|---|---|
| `gt_p0` | true P(purchase \| x, no discount) |
| `gt_p5`, `gt_p10`, `gt_p20` | true P(purchase \| x, discount d) |
| `gt_ite_5`, `gt_ite_10`, `gt_ite_20` | `gt_pd − gt_p0` (true ITE in purchase-probability points) |
| `gt_segment` | persuadable / sure_thing / lost_cause / sleeping_dog (for best level $10) |
| `gt_propensity_{0,5,10,20}` | true assignment probabilities |

---

## 2. Data-Generating Process (spec for the simulator)

Implement in `econocausal/data/simulator.py` with a `SimConfig` dataclass (`n`, `seed`, `margin_rate=0.40`, `hidden_confounder_strength=0.0`, `levels=(0,5,10,20)`). Use `numpy.random.default_rng(seed)`. Let `std(·)` denote z-scoring over the generated population and `σ` the logistic.

**Step 1 — latents**
`z_e ~ N(0,1)`, `z_p ~ N(0,1)`, `u ~ N(0,1)`.

**Step 2 — covariates**
- `age = clip(round(N(36,11)), 18, 75)`
- `tenure_months = clip(round(Gamma(k=2.2, θ=14)), 1, 120)`
- `site_visits_30d = Poisson(exp(1.5 + 0.5·z_e))` capped 80
- `email_open_rate = clip(σ(0.8·z_e − 0.3 + N(0,0.4)), 0, 1)`
- `past_purchases_12m = Poisson(exp(0.8 + 0.5·z_e + 0.004·tenure))` capped 60
- `days_since_last_purchase = clip(Exponential(mean = 30·exp(−0.4·z_e)), 0, 365)` (int)
- `discount_usage_rate = clip(σ(1.0·z_p − 0.5 + N(0,0.5)), 0, 1)`
- `avg_order_value = clip(exp(N(4.2 − 0.25·z_p + 0.1·std(tenure), 0.45)), 15, 400)`
- `cart_abandon_rate = Beta(2, 3)` shifted by `+0.1·σ(z_p)` then clipped to [0,1]
- `loyalty_tier` by quantiles of `0.5·std(tenure) + 0.5·std(past_purchases_12m)` → bronze (<40%), silver (40–70%), gold (70–90%), platinum (≥90%)
- `device ~ Cat(0.6, 0.3, 0.1)`; `region ~ Uniform`; `category_affinity ~ Cat(0.25,0.2,0.2,0.2,0.15)`

**Step 3 — baseline purchase probability**
```
logit_p0 = -1.2 + 0.7*z_e + 0.5*std(past_purchases_12m) - 0.6*std(days_since_last_purchase)
           + 0.2*tier_ord + 0.15*(device=="mobile") + 0.1*(region=="west")
           + hidden_confounder_strength * u
p0 = σ(logit_p0)           # target population mean ≈ 0.15–0.25
```

**Step 4 — true effect of discount d (heterogeneous, diminishing returns, can be negative)**
```
s_price   = σ(4*(discount_usage_rate - 0.5))
s_lapse   = σ(0.04*(days_since_last_purchase - 40))
s_cart    = 0.5 + cart_abandon_rate
premium   = 1[loyalty_tier == "platinum"]
a(x)      = 0.32 * s_price * s_lapse * s_cart  -  0.07 * premium  -  0.05 * 1[p0 > 0.6]
shape(d)  = 1 - exp(-d / 8)                   # diminishing returns; shape(0)=0
tau_d(x)  = a(x) * shape(d)
p_d       = clip(p0 + tau_d, 0.001, 0.999)
```
Resulting segments (best level):
- **Persuadable:** `tau > 0.05` and `p0 < 0.5`
- **Sure Thing:** `p0 ≥ 0.5` and `|tau| ≤ 0.05`
- **Lost Cause:** `p0 < 0.1` and `tau ≤ 0.02`
- **Sleeping Dog:** `tau < −0.02`

**Step 5 — historical (confounded) treatment assignment**
Marketing historically targeted *lapsed but valuable* customers.
```
score_k = beta_k0 + beta_k1*std(days_since_last_purchase) + beta_k2*std(past_purchases_12m)
          + beta_k3*std(avg_order_value) + beta_k4*std(email_open_rate)
          + hidden_confounder_strength * gamma_k * u            # k ∈ {5,10,20}; score_0 = 0
P(T=k | x) = softmax(score)       # then clip each prob to ≥ 0.02 and renormalise
```
Suggested betas: `k=5:  (-1.0, 0.3, 0.2, 0.0, 0.3)`, `k=10: (-1.3, 0.5, 0.3, 0.1, 0.3)`, `k=20: (-2.0, 0.7, 0.4, 0.3, 0.2)`.
Target marginal shares ≈ 40% / 25% / 22% / 13% for $0 / $5 / $10 / $20. Tune betas once so shares land in ±5 pts, then freeze.

**Step 5b — Randomised holdout (`test_rct`)**
Generate a **separate** population (new seed) of size `n_rct` (default 20,000) with `T ~ Uniform{0,5,10,20}` independent of X. Used for unbiased Qini / policy evaluation, mimicking a real A/B holdout.

**Step 6 — outcomes (monotone coupling)**
`v ~ Uniform(0,1)` per customer; `Y_d = 1[v < p_d]`; observed `purchased_14d = Y_{T}`.
`order_value = purchased_14d * avg_order_value * LogNormal(0, 0.25)` (net of discount **not** applied here; discount cost is handled in profit calc).

**Step 7 — derived business quantities** (computed in code, not stored in the CSV)
- Unit margin `m_i = margin_rate * avg_order_value_i`
- Expected profit under discount d: `P_d·(m_i − d)`; baseline `P_0·m_i`
- Incremental profit of d: `τ_d·m_i − (P_0 + τ_d)·d`  ← optimiser objective
- Expected discount spend of d: `(P_0 + τ_d)·d`  ← budget constraint

---

## 3. Splits & Sizes

| Split | Source | Default size | Use |
|---|---|---|---|
| `train` | confounded sim | 70,000 | cross-fit nuisance + final stage |
| `valid` | confounded sim | 10,000 | hyper-parameter selection (nuisance models, forest params) |
| `test_obs` | confounded sim | 20,000 | ITE accuracy vs `gt_*`, calibration, PEHE |
| `test_rct` | randomised sim | 20,000 | unbiased Qini / AUUC, policy value |
| `demo` | confounded sim | 20,000 | fast preset for UI & CI |

Splits are by `customer_id` (no leakage), stratified on `discount_usd`. Seed list for stability study: `[11, 22, 33, 44, 55]`.

Persist as Parquet: `data/processed/{split}.parquet`; ground truth in `data/processed/{split}_gt.parquet` (separate file, joined only in `evaluate/`).

---

## 4. Validation Rules (pandera schema)

- `customer_id` unique, non-null
- `discount_usd` ∈ configured levels; every level has ≥ 500 rows (warn at < 1,000)
- `purchased_14d` ∈ {0,1}
- Numeric features: no inf; missing ≤ 20% per column (impute median + missing flag in pipeline)
- Categorical cardinality ≤ 50
- Propensity overlap check after fit: fraction of rows with any-level propensity < 0.02 must be ≤ 10% else WARN, > 25% FAIL
- Forbidden columns: any starting with `gt_` in the training frame → hard error

## 5. Uploaded (user) data contract
Required mapping: `treatment`, `outcome`, `id`; optional `avg_order_value` (margin); remaining numeric/categorical columns are covariates. The UI lets the user pick **confounders** (default: all covariates) and exclude post-treatment variables. Show a warning banner when treatment is not discrete with ≥ 2 levels.

## 6. Real-data validation (stretch)
- **Hillstrom**: treatment = {no email, men's email, women's email}; outcome = `visit`/`conversion`/`spend`. Map to binary treatment `any_email`. Report Qini on a 30% holdout. Randomised ⇒ also run the biased-subsample experiment (drop treated rows with low `recency` with prob 0.7) and show DML recovers the RCT ATE better than naive.
- **Criteo uplift sample** (≥ 200k rows): binary treatment, `visit`/`conversion` outcomes, 12 anonymised features.
- Datasets are downloaded by `scripts/download_public_data.py` into `data/external/` (git-ignored); cite licence/source in docs.

## 7. Causal DAG (default, exported by `causal/graph.py`)

Nodes: all observed covariates, `discount_usd` (treatment), `purchased_14d` (outcome). Edges:
- Every confounder → `discount_usd`, and every confounder → `purchased_14d`
  (confounders: `days_since_last_purchase`, `past_purchases_12m`, `avg_order_value`, `email_open_rate`, `site_visits_30d`, `discount_usage_rate`, `cart_abandon_rate`, `tenure_months`, `loyalty_tier`, `age`, `device`, `region`, `category_affinity`)
- `discount_usd → purchased_14d`
- Optional edge `U → discount_usd`, `U → purchased_14d` (unobserved) shown dashed when sensitivity analysis is on.
- No variable measured *after* treatment is allowed as a covariate (mediators/colliders).

Export format (JSON): `{"nodes":[{"id","role":"treatment|outcome|confounder|unobserved"}], "edges":[{"source","target"}], "estimand":"backdoor", "adjustment_set":[...]}`.
