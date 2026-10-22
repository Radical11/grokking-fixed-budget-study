# Figure and table map

The base-R follow-up analysis creates eight high-resolution PNG/vector-PDF pairs. The main paper uses selected plots and compact tables to remain eight pages; every standalone figure and numerical output is retained.

| File stem in `output/paper_v2/` | Source and denominator | Interpretation |
| --- | --- | --- |
| `learning_delay` | Representative original-split calibration trace plus three 30-run completion curves | Top panel illustrates delay; bottom panel shows all calibration groups. The full trace remains available. |
| `timing_variation` | 30 calibration runs per split | Capped U; open triangles identify unfinished times at C. C is not an observed completion time. |
| `completion_curves` | Three separate 30-run calibration groups | Empirical first-confirmation curves, retaining unfinished outcomes in the denominator. |
| `policy_validation` | 30 fresh attempts for each of 18 split/budget/policy cells; 30 separate calibration runs per split | Frozen predictions versus observed first success, with exact 95% observed intervals and monotonically transformed exact calibration intervals for predictions. |
| `risk_differences` | Twelve first-confirmation restart-versus-long-run contrasts | Conservative pointwise bounds from exact 97.5% margins; planned bootstrap intervals remain in the CSV. |
| `stability_comparison` | Both endpoints on the same 30 attempts in each cell | Correlated first/500-window outcomes, each completed within its own allocated cap; no permanent-accuracy claim. |
| `distribution_fits` | Expanded original-split calibration sample, n=30 | Three candidate timing CDFs with recording-grid likelihood; ranking is not a true-law claim. |
| `legacy_settings` | The original 120 main runs, 20 per six settings | Exploratory setting context, distinct from new calibration and validation samples. |

## Numerical tables

Calibration figures use 30 observations per split at a 30,000-update limit. Split 1 reuses 20 original baseline runs and adds ten; splits 2 and 3 contain 30 new runs each. Completion-curve denominators retain unfinished observations. Timing plots use the explicitly capped outcome U, not a fabricated unrestricted completion time. The representative trace illustrates one run, not an average trajectory. Prediction intervals for split 1 do not adjust for choosing the two budgets using its reused original traces; fresh policy comparisons use the prospectively fixed design. Validation figures use 30 independent budget attempts per policy/condition, not 30 constituent runs when k exceeds one. Accuracy and probability axes are proportions; time axes count logical optimizer updates.

- `calibration_statistics.csv`: separate split/endpoint counts, capped means/medians/SD and intervals.
- `completion_curves.csv`: complete 25-update grid with pointwise exact probability intervals.
- `calibration_rows.csv`: all 90 calibration records, including explicitly reused observations.
- `validation_attempts.csv`: 540 independent attempt outcomes and budget totals.
- `policy_statistics.csv`: 36 split/budget/policy/endpoint rows, observed/predicted probabilities and bootstrap/conservative prediction-error intervals.
- `risk_differences.csv`: 12 primary and 12 secondary contrasts. Only the primary twelve have Fisher p-values and joint Holm correction.
- `distribution_fits.csv`: parameters, event/censor counts, convergence and AIC.
- `representative_run.csv`: deterministic selection of the illustrative run.
- `study_counts.csv`: fixed sample totals and computational budget.

Intervals are labelled by their method. Bootstrap intervals may collapse in constant observed binary groups; conservative difference bounds avoid implying that their population uncertainty is zero. Neither method gives simultaneous coverage over all curves or contrasts. Holm-adjusted p-values belong to the explicitly stated twelve-test family.
