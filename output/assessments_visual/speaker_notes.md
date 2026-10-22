## 1. Grokking Under a Fixed Budget

Target: 30 seconds.

The two bars show the same total update budget. Each short segment is a new independently initialized model. One update is one training step.

## 2. Grokking: practice improves first

Target: 65 seconds.

The learning curve is the actual original-split run closest to the calibration median. The example underneath shows how modulo arithmetic works.

## 3. The task and the dataset

Target: 60 seconds.

The blue and grey areas represent 576 practice and 385 held-out pairs. Ninety calibration observations include twenty reused original runs and seventy new ones. There are five hundred and forty fresh policy attempts, each independent within its condition. We use three fixed dataset partitions. A seed chooses repeatable starting weights. The follow-up holds weight decay at one, which gently shrinks those weights.

## 4. How the experiment works

Target: 60 seconds.

Follow the arrows from Python to CSV records and then R. The model is a small transformer with 36,992 parameters. The saved checkpoint includes the optimizer and random state. There are at most three CPU workers, each with four threads.

## 5. How we confirm success

Target: 65 seconds.

The three checks span 50 updates from the first qualifying check to the last. The 21 checks span 500 updates. These are relative timelines: the first actual evaluation is at update 25, and update zero cannot begin a streak. We record the last required check. Both training and held-out thresholds must pass at every check. If a run does not qualify by its cap, eventual T stays unknown; U=min(T,C) is a separate capped outcome.

## 6. One budget, different allocations

Target: 70 seconds.

Each row spends B=8,000 updates. One run gets 8,000, two get 4,000 each, and four get 2,000 each. For independent starts, the chance all fail is [1-F(B/k)] to the power k. Subtracting from one gives the chance at least one succeeds. F comes from 30 calibration runs for that split. A Bernoulli variable records one attempt as success or failure; a binomial variable counts successes among independent attempts. Exact intervals describe sampling uncertainty. Calibration predictions were frozen before validation.

## 7. Results at 8,000 total updates

Target: 65 seconds.

Bar heights are counts out of 30 fresh attempts, not percentages or constituent-run counts. One run gives 28 on each split, while four give 12, 9 and 11. Each of these three four-versus-one differences survives the joint Holm correction across twelve planned Fisher tests. No two-run comparison passes the corrected threshold.

## 8. All splits and both budgets

Target: 55 seconds.

All eighteen policy cells are visible. At 12,000 updates, one run gives 30 on each split, two give 30, 30 and 29, and four give 24, 20 and 23. Only the split-2 four-versus-one difference survives correction at this budget. In total four of twelve planned primary tests are detected. This does not establish equality in the other cases. For scale, the exact 95% interval for 28 successes in 30 attempts is 77.9% to 99.2%.

## 9. First confirmation and a longer window

Target: 50 seconds.

Both outcomes use the same attempts. On split 1 at 8,000 updates, four starts produce 12 first confirmations but only 4 confirmations of the 500-update window. The longer window must finish inside the same constituent budget. These secondary outcomes are descriptive and do not prove permanent generalization. Future research can study other tasks, more splits and longer windows.

## 10. One long run was more reliable at 8k

Target: 40 seconds.

The lines are conservative pointwise 95% uncertainty bounds for four-run probability minus one-run probability, expressed in percentage points. All three intervals at 8,000 updates lie below zero. The separately Holm-adjusted tests also detect all three contrasts. The intervals themselves are not simultaneous multiplicity-adjusted intervals. The conclusion is conditional on this task, small model and three fixed splits. Two-run comparisons remain unresolved. Established grokking and restart ideas are credited; this project contributes the recorded empirical comparison.