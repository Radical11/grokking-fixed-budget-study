# Final paper figure guide

The eight paper figures are produced by `analysis/analyze.R review2` from actual saved results. The report caption supplies the sample and interpretation. The R plot files retain their original high-resolution pixels. The editable PowerPoint uses native charts and directly checked numerical values; its explanatory layouts may differ from the report figures.

| Paper figure / file in `output/review2/` | Data and denominator | What it answers | Interpretation limit |
| --- | --- | --- | --- |
| 1. `learning_curve.png` | `data/runs/main/main_f0.6_w1_s11113/trace.csv`; one baseline run | Does practice accuracy improve before new-question accuracy? | Early training window, selected near the median event; the full trace is retained. One run does not represent all timing variation. |
| 2. `time_distribution.png` | 20 baseline observed T values | How spread out are the reference waiting times? | All 20 baseline runs have events. An observed-event histogram in a censored setting would not describe unrestricted T. |
| 3. `setting_comparison.png` | 120 main runs, 20 per cell; U includes all 37 unfinished outcomes at C | How does capped waiting time differ across the six conditions? | A cap marker is not an observed event at the limit. Zero SD of U in the all-unfinished cell does not imply constant T. |
| 4. `budget_probability.png` | 60 main runs at 60% data, 20 per decay; unfinished outcomes stay in each denominator | What fraction succeeds by each update limit? | Conditional on one split and supported only through C. |
| 5. `restart_predictions.png` | 20 main baseline calibration runs | How does predicted policy success vary with total budget? | Estimated, correlated curves under conditional independence; smaller-budget predictions are unvalidated. Report uses a log budget axis. |
| 6. `model_diagnostics.png` | 120 capped outcomes, factorial model | Do residual patterns support the usual model assumptions? | Four panels expose doubtful normality and variance conditions; a permutation check also has exchangeability conditions. |
| 7. `distribution_fits.png` | 20 baseline events and no baseline unfinished observations | Which of three fitted CDF shapes resembles the reference sample? | Candidate fit only; Gamma's lower AIC is not proof of the true law. |
| 8. `policy_validation.png` | 10 fresh attempts per k, 30 total; calibration predictions from separate 20 baseline runs | Do fresh outcomes distinguish the tested restart policies? | All are 10/10 with wide exact intervals. This is inconclusive about superiority and equivalence. |

## Numerical sources

- `group_statistics.csv`: counts, capped means, sample SD/variance, shape statistics, success intervals and bootstrap mean intervals.
- `analysis_rows.csv`: the 120 main rows with the derived U column.
- `policy_predictions.csv`: each budget/k prediction and transformed calibration interval.
- `distribution_fits.csv`: parameter estimates, convergence, likelihood and AIC.
- `model_summary.csv`, `two_factor_tests.csv`, `regression_coefficients.csv`, `welch_tests.csv`: inferential values shown in the report and optional slide details.
- `policy_validation.csv`, `policy_test_summary.csv`: observed policy proportions, exact intervals and the descriptive comparison result.
- `inference.txt`: full R output; `audit.json`: raw-trace audit status.

`scripts/verify_project.py --reproduce` re-runs all eight figures and checks their dimensions and decoded RGB pixels against the saved figures, in addition to the eleven numerical CSV comparisons. The delivered slide PDF is independently checked pixel-for-pixel against renders imported from the final editable PPTX.
