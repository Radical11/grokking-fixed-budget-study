# Prospective follow-up protocol: paper v2.0

Specified on 15 October 2026 before new experiment collection. This is a committed, pre-specified follow-up, not a claim of registration in an external registry. The original delivery is archived at commit d8ffc56dfb0805ee90898220235c09c0f222dcce.

## Purpose and selection disclosure

The existing 120-run study and 30 validation attempts at 30,000 total updates are complete. All three old policies succeeded 10/10, making that budget uninformative about differences. The new budgets (8,000 and 12,000) were selected after inspecting the original 20 baseline calibration traces; this design choice is data-informed. They will not be retuned after observing new results. No policy is required to win.

## Unchanged training

Use the existing modular-addition task, small transformer, AdamW configuration, float32 precision, deterministic algorithms, four CPU threads and 25-update evaluation interval from protocol 1.0. Train every constituent to its full assigned cap, even after a success event. Use no more than three independent processes; concurrency makes runtime descriptive. Keep the original CPU/PyTorch runtime lock. No architecture, threshold, optimizer, decay or device changes are allowed within this study.

## Samples and seed assignment

Fix train fraction 0.6 and weight decay 1 for all new work. Use split seeds 20261013, 20261014 and 20261015. Each split has 30 calibration runs to 30,000 updates. Reuse the original 20 baseline runs for the first split; collect 10 more there and 30 for each new split (70 new calibration runs). Do not drop or retune an unfavourable split.

For each split, each budget B in {8,000,12,000} and each k in {1,2,4}, perform 30 independent budget attempts. Each attempt contains k independent fresh runs at B/k updates. All seeds are disjoint from calibration and previous experiments. This gives 540 attempts and 1,260 validation constituents. Together with calibration, new work is 1,330 training runs and 7,500,000 logical optimizer updates.

The seed manifest is generated in sorted split/replicate order for calibration and split/budget/k/attempt/constituent order for validation. New calibration seeds are consecutive from 100000; validation seeds are consecutive from 200000. The original 20 reused seeds retain their original values and source paths. Commit the complete manifest and protocol before training. Checkpoint resumption uses the same run ID and seed; technical failures retain error records. A failed execution is not coded as a negative learning outcome. Resume/recover the planned run; do not replace seeds based on results.

## Phase ordering

Finish all 90 calibration observations first. Freeze their raw trace hashes and the predicted policy probabilities for both endpoints before any new validation training starts. Verify the freeze when starting or resuming validation. Any unavoidable implementation correction must be documented and committed; scientific choices remain fixed. No significance-based stopping or retrospective selection of budgets, splits or endpoints is allowed.

## Outcomes

Primary T: third consecutive evaluation with training accuracy >=0.99 AND held-out accuracy >=0.95. Step zero never contributes. A failed check resets the streak. Record the final confirmation check, without backdating. This matches the original outcome.

Secondary T_500: 21 consecutive qualifying evaluations, spanning 500 updates. Record its final check; all 21 checks and their learning costs must be inside the constituent budget. This is finite-window stability, not permanent generalization. Derive both endpoints from saved traces without changing the original checkpoint detector.

Unknown event times remain blank. Calibration comparisons may use U=min(T,30000), clearly distinguished from unrestricted T. Validation compares attempt-level success probabilities at equal total budgets; do not pool constituent event times across different per-run caps or treat constituents as independent policy attempts.

## Analysis specified before validation

Estimate each split's completion curve using its 30 calibration runs, with unfinished outcomes retained in the denominator through the common cap. Predict policy success as 1-[1-F(B/k)]^k, separately for each endpoint. Calibration and validation are disjoint. Exact Clopper-Pearson intervals describe observed proportions; transformed calibration intervals describe predicted probabilities. Independently bootstrap calibration runs and validation attempts (5,000 resamples, R seed 20261015) for prediction-minus-observation differences. Bootstrap attempt groups separately for policy risk differences.

The twelve primary tests compare k=2 versus k=1 and k=4 versus k=1, within each split/budget, using two-sided Fisher exact tests. Apply Holm adjustment jointly over all twelve. All-identical outcomes have no evidence of a difference and are retained descriptively. Risk-difference intervals are pointwise, not simultaneous. Small differences may remain unresolved at n=30; no equivalence inference is permitted. Secondary stability analyses are descriptive with intervals, not another unreported family of significance tests. Show every split separately.

Retain the original 120-run setting comparisons, capped-time regression and ANOVA as exploratory context with their recorded assumption violations. Fit the original three candidate timing families only to the expanded 30-run original-split calibration sample, using the original grid/censoring likelihood and a minimum of eight events. Do not infer the unrestricted tail nonparametrically. Neither AIC ranking nor a finite stability window proves a true law or permanent learning.

## Reporting and completion

Deliver an eight-page integrated paper and approximately four-page supplement, editable Markdown, high-resolution PNG/vector-PDF figures, and a 13-main-plus-two-optional-slide presentation. Report all planned conditions, actual counts, missing/failed execution states, numerical assumptions and runtime limits. Preserve original data and reports. New evidence lives under data/paper_v2 and output/paper_v2; original aggregate exports are not rewritten.

Completion requires sample/accounting and trace audits, resumption/failure tests, independent output reproduction, visual inspection and source/contribution records. Negative and inconclusive outcomes count as valid results. College similarity clearance is not inferred from a local phrase screen.
