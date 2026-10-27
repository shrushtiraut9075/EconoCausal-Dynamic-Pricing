# DELIVERABLES.md — Internship Submission Guide

The assignment letter (Ref ITS/DSML/1142) requires on completion: **Source Code, Project Documentation, Project Report, Presentation (PPT), Model Evaluation Results, Final Project Demonstration.** Evaluation parameters: attendance, technical competency, quality of deliverables, innovation, communication/teamwork, adherence to timelines, documentation standards, final review.

## 1. Deliverables checklist
| # | Deliverable | Source in repo | Format | Done |
|---|---|---|---|---|
| 1 | Source code | whole repo, tag `v1.0` | GitHub repo / zip | ☐ |
| 2 | Project documentation | `README.md`, `docs/*.md` | MD (+PDF export) | ☐ |
| 3 | Project report | written from `reports/evaluation_report.md` | DOCX/PDF, 15–25 pages | ☐ |
| 4 | Presentation | built from figures in `reports/figures/` | PPTX, 12–15 slides | ☐ |
| 5 | Model evaluation results | `reports/evaluation_report.md`, `results.csv`, figures | MD/CSV/PNG | ☐ |
| 6 | Final demonstration | live demo + backup video | 5–7 min | ☐ |

## 2. Project report outline (DOCX/PDF)
1. Title page, certificate/acknowledgement, abstract (150 words)
2. Introduction — problem (correlation vs causation), motivation, objectives
3. Literature/background — potential outcomes, DML, causal forests, uplift modelling, Qini
4. System design — architecture diagram, tech stack, data flow
5. Data — simulator design, confounding, ground truth, splits, public dataset (if done)
6. Methodology — DAG & identification, propensity/overlap, DML, baselines, optimisation formulation
7. Implementation — modules, API, dashboard (screenshots)
8. Evaluation — metrics, results tables, uplift curves, calibration, policy value, ablations
9. Causal audit — refutation results and interpretation
10. Monitoring & NL summaries
11. Limitations, ethics, future work (e.g. real A/B data, continuous discounts, multi-period)
12. Conclusion, references, appendix (config, reproducibility, API reference)

## 3. Presentation outline (12–15 slides)
1. Title · 2. Problem: "Would they have bought anyway?" · 3. Why predictive ML fails (4-segment matrix) · 4. Solution overview · 5. Architecture · 6. Data & confounding (naive vs truth bar chart) · 7. Double ML in one slide · 8. Causal graph & audit · 9. Results: accuracy (ATE/PEHE/Spearman table) · 10. Uplift/Qini vs baselines · 11. Optimisation & budget frontier ("saves $X vs blanket") · 12. Dashboard demo screenshots · 13. API + drift monitoring · 14. Limitations & future work · 15. Q&A

## 4. Demo script (5–7 min)
1. (0:30) State the problem with the four segments.
2. (0:45) Setup page → load demo data → show profile & confounding note.
3. (0:45) Graph page → DAG and assumptions.
4. (1:15) Train (pre-trained model ready) → Uplift page → Qini DML vs predictive vs random.
5. (1:00) Audit page → four refutation cards.
6. (1:30) Allocation page → set budget $5,000 → matrix → filter Persuadables → frontier.
7. (0:45) Summary page → NL headline.
8. (0:30) Monitoring page → inject drift → status turns Amber/Red.
9. (0:30) `/docs` OpenAPI + `curl /predict`.
Backup: recorded video + screenshots in case of live failure. Pre-load a trained model and cached allocation.

## 5. Weekly mentor update template
```
Subject: EconoCausal — Week <n> progress (<dates>)
Done: • <bullet with outcome/metric>
Metrics so far: ATE err …, √PEHE vs S-learner …, Spearman …
Next week: • …
Blockers / help needed: • …
Links: repo/PR, report snippet
```
Send after Week 1 (16 Oct), Week 2 (23 Oct), Mid-review (24 Oct), Week 3 (31 Oct), Week 4 (7 Nov).

## 6. Final review readiness checklist
- [ ] `make demo` works on a clean clone · [ ] `make check` green · [ ] README quick-start verified by someone else
- [ ] Evaluation report generated; targets table honest · [ ] Audit page all tests rendered
- [ ] Report and PPT numbers match `reports/results.csv` (no hand-typed numbers)
- [ ] Originality: all code/text original; libraries and datasets cited (Terms & Conditions require plagiarism-free work)
- [ ] Confidential info: no company-confidential material in public repo
- [ ] Submit by **10 Nov 2026**, keep a copy

## 7. Likely review questions (prep)
1. Why can't a churn model decide who gets a discount? 2. What is the ITE and how does DML estimate it? 3. What is cross-fitting and why needed? 4. What assumptions does your estimate rely on, and how did you test them? 5. How do you know the model works on *real* data (no ground truth)? (RCT holdout / Qini / refuters) 6. Why LightGBM nuisances? 7. How does the optimiser work and why LP relaxation? 8. What happens if a hidden confounder exists? 9. How does drift detection protect the business? 10. What would you do with real A/B data?
