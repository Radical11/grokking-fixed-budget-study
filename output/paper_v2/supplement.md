# Technical Supplement

## S1. Design, samples and independence

The original delivery at commit d8ffc56 contains 9 pilot runs, 120 main runs and 70 validation constituents. Its 20 original baseline main runs are reused once in the 90-run follow-up calibration sample; they are not additional observations. Seventy new calibration runs and 1,260 fresh validation runs add 1,330 unique training runs. The follow-up has 540 independent budget attempts, not 1,260 independent policy observations.

<!-- table-widths: 3.7,2.95 -->

| Quantity | Fixed total |
| --- | --- |
| Splits / calibration per split | 3 / 30 |
| Calibration observations / reused / new | 90 / 20 / 70 |
| Budgets / policies / attempts per cell | 2 / 3 / 30 |
| Validation attempts / constituent runs | 540 / 1,260 |
| Additional logical training updates | 7,500,000 |

New calibration seeds run consecutively from 100000 in split/replicate order; validation seeds start at 200000 in split/budget/k/attempt/component order. The complete manifest precedes new training. Changing the initialization seed does not change the split-seeded permutation. Partitions are regenerated and checked for correct labels and disjointness in the raw audit. The smaller 40% original training sets are nested within the 60% sets; comparisons across those fractions also change the held-out pair set.

## S1.1 Phase gate and execution

All 90 calibration observations finish before predictions and raw-trace hashes are frozen. Validation verifies this freeze before it starts or resumes. Configurations, complete traces, statuses and errors are retained; unknown event times remain blank. No seed is replaced for poor learning performance. A technical failure remains a technical failure and must be resumed or reported, not converted into a negative learning outcome.

CPU runs use four threads, float32 and PyTorch 2.11.0+cu128; the CUDA-enabled library build does not imply GPU training. Up to three independent processes run concurrently. Checkpoints occur every 500 updates, and resumed work restores model, optimizer and RNG state. Lost partial-checkpoint work may repeat physically; logical budget equality remains distinct from wall-clock or recovery cost.

Recorded per-run elapsed times sum to 4.24 run-hours for new calibration and 8.60 for validation. Parallel jobs overlap, so these sums are not wall-clock duration. Unsaved work before interruption is not fully measured.

## S1.2 Endpoint reconstruction

At update zero, record accuracy only. At each later 25-update check, increment a qualifying streak only if both practice >=0.99 and held-out >=0.95, otherwise reset to zero. Primary T is the first check ending a streak of length three. T_500 ends the first length-21 streak. A 500-update span requires 21 observations, not 20. Do not backdate either endpoint, and do not use checks after a run cap. A stability event must be at least 450 updates after first confirmation, but may occur much later if streaks reset.

---

## S2. Statistical calculations and assumptions

For a fixed split, F_hat(t)=count(observed event time <=t)/30, through C=30,000. Unfinished times remain in the denominator and contribute no event. U=min(T,C) is fully observed, but is not an imputation of T. Histograms of observed events alone are conditional summaries. Constant U in an entirely unfinished cell does not imply constant T, and a degenerate bootstrap interval cannot recover uncertainty in an unseen tail.

For each policy attempt, the binary outcome is whether any of its k independent constituents confirms within B/k updates. Conditional on the fixed setting, P(success)=1-[1-F(B/k)]^k. Exact 95% Clopper-Pearson intervals use base R binom.test. Predicted intervals transform the single-run interval monotonically. These intervals are pointwise and correlated across budgets because the same calibration traces are reused. Original-split intervals do not adjust for choosing budgets using 20 reused observations; fresh validation comparisons use the already fixed design.

With R seed 20261015, use 5,000 resamples. Capped mean intervals resample calibration observations. Risk-difference intervals independently resample the two policy-attempt groups. Prediction-minus-observation intervals independently resample the calibration event times and the observed attempt outcomes, transform the bootstrap completion proportion, and subtract the bootstrap observed mean. Do not bootstrap constituent runs as if they were policy attempts. Secondary endpoints are correlated outcomes from the same attempt.

The primary family is twelve two-sided Fisher exact comparisons: k=2 versus k=1 and k=4 versus k=1, for two budgets and three splits. Holm adjustment applies to all twelve together, including identical-outcome cells assigned descriptive p=1. Secondary stability comparisons have intervals and no additional significance family. Pointwise bootstrap intervals must not be treated as simultaneous multiplicity-adjusted inference. At n=30, a small observed difference or nonsignificant result cannot establish equivalence.

A pre-validation implementation note adds conservative difference bounds [L1-U0,U1-L0] using two exact 97.5% marginal binomial intervals. Their noncoverage probabilities sum to at most 5%. These pointwise bounds remain nondegenerate when a binary group is constant; the main difference plot uses them, while the planned bootstrap outputs remain available. The same construction also bounds transformed-prediction minus observation. This changes no primary tests or outcomes.

## S2.1 Candidate timing likelihood

For each candidate CDF G of X=T-50, the recorded event mass is G(t-50)-G(t-75), with G(x)=0 for nonpositive x. An unfinished observation contributes 1-G(C-50). Positive parameters are optimized on a log scale. Exponential has a rate; Gamma and Weibull have shape/scale parameters. AIC=2q-2 log(L). Use only the expanded original-split calibration sample and at least eight events. Model ranking remains conditional on this small sample.

## S2.2 Exploratory syllabus analyses

The archived original study uses Welch comparisons with Holm adjustment, capped-time bootstrap intervals, Pearson/Spearman relationships, simple/multiple regression and one-/two-factor ANOVA. Capping, skew and unequal variance limit normal-error interpretations. The original residual-permutation sensitivity requires exchangeable errors and does not cure unequal variance. These analyses are supporting exploration, distinct from the pre-specified fresh policy tests.

---

## S3. Complete validation counts

<!-- table-widths: 0.55,0.8,0.4,1.3,1.75,1.85 -->

| Split | B | k | First / 30 | Predicted first | 500 window / 30 |
| --- | --- | --- | --- | --- | --- |
| S1 | 8000 | 1 | 28/30 | 93.3% | 28/30 |
| S1 | 8000 | 2 | 23/30 | 67.9% | 21/30 |
| S1 | 8000 | 4 | 12/30 | 24.1% | 4/30 |
| S1 | 12000 | 1 | 30/30 | 96.7% | 30/30 |
| S1 | 12000 | 2 | 30/30 | 92.9% | 30/30 |
| S1 | 12000 | 4 | 24/30 | 71.1% | 13/30 |
| S2 | 8000 | 1 | 28/30 | 96.7% | 27/30 |
| S2 | 8000 | 2 | 24/30 | 78.2% | 18/30 |
| S2 | 8000 | 4 | 9/30 | 34.4% | 4/30 |
| S2 | 12000 | 1 | 30/30 | 100.0% | 30/30 |
| S2 | 12000 | 2 | 30/30 | 98.2% | 30/30 |
| S2 | 12000 | 4 | 20/30 | 71.1% | 16/30 |
| S3 | 8000 | 1 | 28/30 | 96.7% | 26/30 |
| S3 | 8000 | 2 | 25/30 | 71.6% | 21/30 |
| S3 | 8000 | 4 | 11/30 | 12.7% | 1/30 |
| S3 | 12000 | 1 | 30/30 | 100.0% | 30/30 |
| S3 | 12000 | 2 | 29/30 | 98.2% | 29/30 |
| S3 | 12000 | 4 | 23/30 | 65.5% | 19/30 |

Each row represents a different group of 30 fresh attempts. First and stability counts within a row come from the same attempts. Predictions use 30 separate calibration observations for that split and were frozen before validation. The complete exact probability intervals, transformed calibration intervals and bootstrap prediction errors are provided in policy_statistics.csv.

## S3.1 Calibration samples

<!-- table-widths: 0.6,1.0,1.15,1.3,2.6 -->

| Split | Endpoint | Events / 30 | Mean capped time | Mean-time 95% bootstrap CI |
| --- | --- | --- | --- | --- |
| 1 | first | 30/30 | 5,347 | 4,055 to 7,303 |
| 1 | stability | 30/30 | 5,890 | 4,590 to 7,696 |
| 2 | first | 30/30 | 4,251 | 3,649 to 4,901 |
| 2 | stability | 30/30 | 4,774 | 4,170 to 5,398 |
| 3 | first | 30/30 | 4,378 | 3,779 to 5,013 |
| 3 | stability | 30/30 | 4,908 | 4,286 to 5,546 |

Secondary rows cap T_500 at C, giving U_500=min(T_500,C). S1=20261013, S2=20261014, S3=20261015. Twenty observations in S1 are reused from the original main study. All other follow-up seeds are new. New split seeds provide fixed-partition robustness checks rather than a random sample of all possible tasks or models.

---

## S4. Complete primary comparisons

<!-- table-widths: 1.05,0.85,1.25,2.1,1.4 -->

| Split / B | Contrast | Risk difference | Conservative 95% CI | Holm p |
| --- | --- | --- | --- | --- |
| S1 / 8k | 2 vs 1 | -16.7 pp | -44.3 to +15.8 pp | 0.873 |
| S1 / 8k | 4 vs 1 | -53.3 pp | -78.7 to -13.7 pp | 0.000187 |
| S1 / 12k | 2 vs 1 | +0.0 pp | -13.6 to +13.6 pp | 1 |
| S1 / 12k | 4 vs 1 | -20.0 pp | -41.2 to +7.0 pp | 0.166 |
| S2 / 8k | 2 vs 1 | -13.3 pp | -40.6 to +17.8 pp | 1 |
| S2 / 8k | 4 vs 1 | -63.3 pp | -86.3 to -23.6 pp | 6.57e-06 |
| S2 / 12k | 2 vs 1 | +0.0 pp | -13.6 to +13.6 pp | 1 |
| S2 / 12k | 4 vs 1 | -33.3 pp | -55.4 to -2.0 pp | 0.00717 |
| S3 / 8k | 2 vs 1 | -10.0 pp | -36.7 to +19.7 pp | 1 |
| S3 / 8k | 4 vs 1 | -56.7 pp | -81.3 to -16.9 pp | 6.8e-05 |
| S3 / 12k | 2 vs 1 | -3.3 pp | -19.5 to +13.5 pp | 1 |
| S3 / 12k | 4 vs 1 | -23.3 pp | -44.9 to +4.9 pp | 0.0843 |

Risk differences compare success probabilities. Raw Fisher p-values and exact method flags are retained in risk_differences.csv. The intervals are pointwise; the Holm column belongs to the jointly corrected twelve-test family. All twelve comparisons are disclosed, including nonsignificant results.

## S4.1 Reproduction and provenance

The run_paper_v2.ps1 entry point resumes calibration and validation, performs the raw audit, runs base R, builds the paper/supplement/presentation, and writes verification records. Reproduction from saved data uses its analysis-only mode. The original report inputs are hash-checked separately. Source configurations, trace hashes, freeze records and analysis inputs identify the delivered version. Checkpoints and local runtimes remain excluded from Git.

All scientific graphs are exported in high-resolution PNG and vector PDF. Numerical slide charts remain editable. The local exact phrase-overlap screen covers cited public papers only; it is not an institutional similarity score or a semantic/code/AI-authorship detector. Bibliographic titles and attributed standard formulas are distinguished from original experiment data and prose. No worldwide-first claim is made.
