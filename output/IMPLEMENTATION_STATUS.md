# Both review stages complete

Completed on 14 October 2026. The frozen Review 1 milestone comprises a five-page report, 24 main runs and approximately 65% of the weighted implementation checklist. Its original completion record is preserved in `output/REVIEW1_STATUS.md`. All planned implementation components are now complete. This percentage describes implementation, not scientific certainty or proven novelty. Review 2's presentation date has not been supplied.

## Actual experimental evidence

- 199 completed training runs: 9 pilot, 120 main and 70 fresh-seed validation constituents. There are no failed or paused final runs.
- Main study: 20 initialization seeds in each of six cells (40%/60% training data; weight decay .3/1/3), including the original 24 runs.
- Main outcomes: 83 observed generalization times and 37 runs unfinished at the 30,000-update cap. Unknown completion times remain blank. Of the 83 events, 81 meet the operational delayed-generalization criterion and two are rapid learning.
- 62 of the 83 generalized main runs later dipped below 95% unseen accuracy. The endpoint is first confirmation at three consecutive evaluations, not permanent accuracy.
- Baseline (60% data, decay 1): 20/20 events; mean capped time U = 5,481.25 updates, median 4,025, SD 5,547.81. The exact 95% success interval is 83.2%-100%; the bootstrap interval for mean U is approximately 3,596-8,224 updates.
- Validation: 10 independent attempts for each policy k=1,2,4, each allocated exactly 30,000 logical updates. All three policies succeeded in 10/10 attempts; each exact 95% interval is 69.2%-100%. This generous budget gives no clear winner and does not establish equivalence. Smaller-budget predictions remain unvalidated.
- The Gamma candidate has the lowest baseline AIC (253.96), among Exponential, Gamma and Weibull. This fit uses 20 baseline events and zero baseline unfinished runs; the likelihood supports unfinished observations. Model ranking is not proof of a true timing distribution.
- Base-R analysis covers capped-time variability and shape statistics, probability and bootstrap intervals, exploratory tests, correlation, simple/multiple regression, one-way/two-factor ANOVA, diagnostics and permutation sensitivity. Assumption violations and the exchangeability requirement are disclosed.

## Verification

- 21 automated tests passed, including deterministic CPU checkpoint resumption, threshold detection, unfinished/failed runs, logical allocation and R integration.
- Raw-trace audit passed: event reconstruction, split disjointness, sample counts/means, predictions and validation seed/budget accounting.
- All 199 traces contain finite losses and accuracies; accuracies lie within [0,1]. Every policy attempt records 30,000 completed logical updates.
- The complete Python -> CSV -> R -> graphs -> PDF flow ran on the real dataset. All seven final-report pages were visually inspected; the five-page first report remains preserved. Input-hash manifests cover 414 final and 63 frozen first-review inputs.

## Execution and interpretation limits

Python 3.13.15, PyTorch 2.11.0+cu128 and base R 4.6.1. CUDA was unavailable in this execution environment. All training used the locked CPU configuration with four threads per run. GPU execution is unverified; this is not a diagnosis of the physical laptop GPU.

Collection resumed from saved checkpoints after an interruption. Budgets count logical trajectory updates. Recovery can repeat unsaved physical work; recorded active runtime excludes downtime and may omit lost work between checkpoints. Concurrent CPU contention also affects runtime. Exact physical-compute or wall-clock equality is not claimed.

U = min(T,C) is fully observed and distinct from unrestricted T. Unfinished runs do not reveal eventual completion times. Constant U in an entirely unfinished cell does not imply zero variability in T. No worldwide-first claim is made: the proposed contribution is this controlled empirical connection between grokking timing and fixed-budget restarts.

## Deliverables

- `output/pdf/review2_report.pdf`: seven-page final report, companion Markdown and input-hash manifest.
- `output/pdf/review1_report.pdf`: preserved five-page first-review report.
- `output/review2/`: eight graphs, numerical results, inference, diagnostics and audit.
- `data/`: real configurations, traces, summaries, validation attempts and runtime lock; local checkpoints are ignored by Git.
- `run_review1.ps1` / `run_review2.ps1`: reproducible stage commands.
