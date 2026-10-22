# Assessment 10: Final project explanation and results

Grokking Under a Fixed Budget: One Long Run or Several Restarts?

Name: [Your name] | Registration number: [Your registration number]

## 1. The problem and objective

A learning program can answer its practice questions correctly before it starts answering new questions correctly. Researchers call this delayed improvement grokking [1]. We measured how long that improvement takes across different random starts, then asked whether one long attempt or several shorter attempts is more reliable when both receive the same total training budget.

## 2. What the computer learns

The task is addition modulo 31: add two numbers and keep the remainder after division by 31. For example, (30 + 4) mod 31 = 3. There are 961 ordered input pairs. Each baseline split gives the model 576 practice pairs and holds back 385 pairs for evaluation. Three fixed splits check whether the result changes when the practice questions change.

## 3. How the code works

Python creates the pairs and correct answers, selects disjoint practice/evaluation sets and trains a small transformer with 36,992 adjustable parameters. A seed fixes the random starting weights, so an experiment can be repeated. One update is one learning step using all practice pairs. AdamW adjusts the weights; weight decay gently shrinks them and stays fixed at 1 in the follow-up. The learning rate stays at 0.003.

Every 25 updates, Python records practice and new-question accuracy in CSV traces. It saves checkpoints so interrupted runs can resume. R reads these records, computes the statistical results and creates the graphs. Unknown completion times stay unknown. The code checks labels, dataset separation, seeds and exact update totals.

## 4. What counts as success?

First confirmation T requires at least 99% practice accuracy and 95% new-question accuracy at three consecutive checks. We count the last check. A separate measure needs 21 successful checks spanning 500 updates, all inside the allocated budget. This longer window measures finite stability; later accuracy can still fall. For capped-time statistics, U=min(T,C), where C is the run limit.

## 5. The completed experiment

Calibration uses 30 full-length runs for each split: 90 observations, including 20 reused original runs and 70 new ones. Fresh validation tests budgets of 8,000 and 12,000 total updates with one, two or four runs. Each of the 18 conditions has 30 independent attempts. This gives 540 attempts containing 1,260 runs. The extension adds 1,330 training runs and 7.5 million logical updates. All runs finished without technical failure. A completed run can still miss the success criterion.

---

## 6. The probability and statistics

F(t) is the chance that one run confirms success by step t. We estimate it as the number of calibration runs confirmed by t divided by 30. If k independent starts each receive B/k steps, the probability that all fail is [1-F(B/k)]^k. Therefore, the chance that at least one succeeds is 1-[1-F(B/k)]^k [3]. Calibration predictions were frozen before fresh validation.

Each attempt gives a Bernoulli yes/no outcome; a group gives a binomial success count. Exact 95% confidence intervals describe sampling uncertainty. Twelve planned Fisher exact tests compare each restart policy with one long run. Holm correction accounts for testing twelve comparisons. Probability differences have conservative uncertainty bounds, with bootstrap resampling as a sensitivity analysis. Original setting comparisons, correlation, regression and ANOVA remain exploratory because their usual assumptions are imperfect here.

## 7. Results: successes out of 30 fresh attempts

| Split / total steps | One run | Two runs | Four runs |
| --- | --- | --- | --- |
| S1 / 8,000 | 28/30 | 23/30 | 12/30 |
| S1 / 12,000 | 30/30 | 30/30 | 24/30 |
| S2 / 8,000 | 28/30 | 24/30 | 9/30 |
| S2 / 12,000 | 30/30 | 30/30 | 20/30 |
| S3 / 8,000 | 28/30 | 25/30 | 11/30 |
| S3 / 12,000 | 30/30 | 29/30 | 23/30 |

At 8,000 total updates, one long run succeeds in 28/30 attempts on every split. Four shorter runs succeed in 12/30, 9/30 and 11/30. All three differences survive Holm correction. Their four-minus-one probability differences are -53.3, -63.3 and -56.7 percentage points. At 12,000 updates, only the second-split four-run comparison survives correction. No two-run comparison reaches the corrected threshold. That does not establish that the two policies are equivalent.

Uncertainty matters: 28/30 is 93.3% observed success, with an exact 95% interval of 77.9% to 99.2%. On split 1 at 8,000 updates, four runs give 12/30 first confirmations but only 4/30 confirmations of the 500-update window. The endpoint changes what “worked” means.

## 8. Conclusion, limits and future work

For this small model and these three splits, one long run is more reliable than four short runs at 8,000 total updates. Very short runs can end before delayed learning has enough time to appear. The result is conditional on the task, model and budgets. Thirty attempts cannot settle every small difference, and three splits do not represent every possible dataset. Future work can study other tasks, more splits and longer stability windows. The completed study and all recorded results already support the present conclusion.

References: [1] Power et al., “Grokking,” arXiv:2201.02177, 2022. [3] Streeter, Golovin and Smith, “Restart Schedules for Ensembles of Problem Instances,” 2007. Full references, methods and figures appear in Assessment 9 and the archived technical supplement.
