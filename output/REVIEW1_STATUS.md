# Review 1 ready

Prepared for the 15 October 2026 review. The planned approximately 65% milestone is complete: protocol/source mapping, training and resumption, repeated-run export and budget-policy runner, preliminary R analysis, and a visually checked five-page report.

## Actual evidence

- 9 completed pilot runs and 24 completed main runs; 33 real training runs, each observed through 30,000 updates.
- Main-study sample: weight decay .3, n=6; decay 1, n=12; decay 3, n=6; all at 60% training data.
- Baseline selected by the predefined pilot rule: decay 1, pilot median 2,400 updates.
- Fresh baseline event times: 1,875-27,175 updates; mean capped time 6,475, median 4,275, SD 7,041.43 updates.
- All 24 main runs confirmed the generalization threshold within the cap. No failed or paused main runs; no censored main outcomes in this first dataset. Censoring handling is implemented and tested for later studies.
- 18 main runs had at least one later unseen-accuracy dip below 95%. The endpoint is the first three-checkpoint confirmation, not permanent accuracy.
- Actual R analysis generated five figures, exact probability intervals, bootstrap capped-mean intervals, exploratory Welch comparisons/Holm adjustment, one-way ANOVA/permutation sensitivity, correlation and simple regression.
- Raw-trace audit independently reconstructed event times, verified disjoint partitions, matched R sample counts/means, and checked every policy probability and allocated budget.
- 18 automated tests passed, including CPU checkpoint resumption with bitwise-identical parameters and traces, failure retention, fixed-budget safeguards and R integration fixtures.
- Final PDF: five pages, all pages visually inspected; input hashes recorded in its manifest.

## Execution environment

Python 3.13.15, PyTorch 2.11.0+cu128, base R 4.6.1. Training used CPU with four threads per run and up to three independent processes. CUDA initialization reported no available GPU in this execution environment. GPU training and CUDA-graph resumption were not verified. This does not diagnose the physical laptop GPU; the dataset is locked to CPU for consistency.

The R runtime was extracted locally from the official Windows distribution rather than running its installer. Exact Python packages are recorded in requirements.lock.txt; supplied PDFs are preserved with hashes.

## Review 2 remains

- Add 96 main runs to reach 120 across the two data fractions and three weight decays.
- Execute 30 fresh-seed policy attempts (10 each for k=1,2,4), comprising 70 constituent training runs.
- Run the prepared censored/discretized distribution fitting, multiple regression and two-factor ANOVA on the expanded real dataset.
- Compare actual fresh-seed policy outcomes with predictions and produce the final report.

Review 2 code paths were checked with isolated synthetic test fixtures, not claimed as completed real experiments. Restart curves in this report are predictions only. The full 30,000-update validation budget is generous; it may be less informative about policy differences than budgets near the learning transition. Any revised validation budget should be specified before its fresh-seed experiments.

## Deliverables

- output/pdf/review1_report.pdf: minimal paper-style report.
- output/pdf/review1_report.md: companion content.
- output/review1/: R graphs, numerical results, inferential output and audit.
- data/: raw configurations, traces, summaries and runtime lock.
- run_review1.ps1 / run_review2.ps1: reproducible stage commands.

No worldwide-first claim is made. The proposed contribution is the empirical fixed-budget restart comparison in this controlled setting.
