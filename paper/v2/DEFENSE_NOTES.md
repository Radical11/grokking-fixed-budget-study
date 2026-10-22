# Short answers for the final review

## How can learning time be random if the code is repeatable?

A seed chooses the model's random starting weights. With the same seed, device and recorded software settings, the run is repeatable. Across independent starting weights, the measured completion time can differ. That is the source of variation studied here. Full-batch training does not introduce a newly shuffled mini-batch at every step.

## Is the addition rule secretly written into the model?

The rule generates the correct labels for the experiment. The model receives the two input numbers and a query token, not the answer or the addition formula. Gradient updates use only the practice pairs. Held-out answers are used to measure the endpoint, so the study does not claim an additional untouched test set for every design decision.

## What exactly counts as success?

First confirmation requires at least 99% practice accuracy and 95% held-out accuracy at three consecutive checks. We check every 25 updates and count the final check. Update zero cannot start a streak. This measures confirmed performance; a rapid success is not automatically delayed grokking.

## Why does a 500-update window need 21 checks?

Twenty-one measurements have twenty gaps. At 25 updates per gap, those gaps span 500 updates. The final confirming check must fit inside the run's own allocation. This is a finite stability window, not proof that accuracy will stay high forever.

## What happens when a run does not learn in time?

Its eventual completion time T remains unknown. For explicitly capped comparisons, U records the smaller of T and the training limit C. Calling U equal to C does not mean that the run actually generalized at C. A technical error is recorded separately from a completed run that misses the accuracy criterion.

## What is one observation in a restart comparison?

One complete budget attempt. With four starts, all four must finish their allocated B/4 updates; the attempt succeeds if any one confirms. Thirty such attempts are thirty policy observations, even though they contain 120 constituent runs. This policy does not average predictions or vote across models.

## Why is the restart formula valid?

Conditional on the same fixed split and settings, independent starts each fail by B/k with probability 1-F(B/k). All k fail with probability [1-F(B/k)]^k. Subtract from one for at least one success. We must still measure F: splitting the budget may leave each run too short to learn. The identity does not guarantee a restart advantage.

## Why use Fisher tests, confidence intervals and Holm correction?

Success is a yes/no outcome and each group has only 30 attempts. Fisher's two-sided exact test compares the two success probabilities without requiring normally distributed times. Exact binomial intervals show uncertainty in each probability. Holm correction accounts for the twelve pre-specified comparisons as one family. A nonsignificant comparison does not establish equal probabilities.

## Why report bootstrap and conservative intervals?

Bootstrap resampling shows sensitivity to the observed samples. If a group contains only successes or only failures, its bootstrap interval can collapse. The conservative difference bounds retain uncertainty by combining exact binomial margins. These are pointwise intervals, not simultaneous coverage for every graph point or comparison.

## Was the follow-up designed after seeing results?

The two smaller budgets were selected using the old baseline traces, and that choice is disclosed. The complete follow-up protocol and seed manifest were committed before new training. Calibration predictions were frozen before fresh validation. Twenty old runs are reused once in the original-split calibration sample. Its prediction intervals do not adjust for that earlier budget selection; the fresh policy comparisons use the already fixed design.

## What is original about this project?

Grokking, timing prediction, seed variability and restart theory all have prior work. The proposed contribution is this controlled empirical comparison: measured completion curves, frozen predictions, fresh equal-budget attempts, three fixed partitions and a distinct finite stability endpoint. The paper does not claim worldwide priority or a new theorem. See `LITERATURE_COMPARISON.md` for the source-by-source comparison.

## What remains uncertain after a complete experiment?

Thirty attempts can detect substantial differences but may leave close probabilities unresolved. Three partitions of one small arithmetic task do not represent all datasets or networks. Future research can test other tasks, additional partitions and longer accuracy windows. The full planned study is complete only when the actual status/audit records confirm all samples; a winning policy is not a completion requirement. An official similarity score still requires the college's checker.
