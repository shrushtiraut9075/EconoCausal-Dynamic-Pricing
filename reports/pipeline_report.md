# EconoCausal End-to-End Pipeline Report

**Pipeline Execution Date:** 2026-10-10 23:32:52
**Seed:** 42

## Executive Summary
The causal uplift pricing engine trained and verified the Double ML model using EconML CausalForestDML with 5-fold cross-fitting and debiased orthogonal learners.

### Key Highlights
- **Debiasing:** Pre-treatment confounding removed using multi-class propensity cross-fitting.
- **Robustness:** Causal refutation audits confirmed stability under placebo and random common cause shocks.
- **Optimization:** Fixed-budget discount allocation solved using SciPy HiGHS LP relaxation with greedy integer rounding.
- **Zero Leakage:** Strictly validated absence of `gt_*` variables in training and allocation stages.

Pipeline status: **HEALTHY AND OPERATIONAL** ✅
