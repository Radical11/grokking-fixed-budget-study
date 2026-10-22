## Slide 1

Our project measures how long a small learning program takes to answer new questions correctly. We then compare one long attempt with two or four independent starts under the same total training budget. This presentation explains the idea, the implementation, the probability methods and the measured results.

## Slide 2

Imagine doing well on familiar practice questions but struggling with new questions. Memorization is strong practice performance. Generalization is good performance on new examples. Grokking means that improvement on new examples appears later, after practice performance is already good. Modulo means the remainder after division. Thirty plus four is thirty four, whose remainder after division by thirty one is three. Every answer is known exactly, which makes this a controlled computer experiment. The analogy does not establish human-like understanding.

## Slide 3

One update is one learning step using all practice examples. A seed fixes the random starting weights, allowing repeatable experiments. Weight decay gently shrinks those weights; the follow-up keeps it at one. The baseline model sees five hundred and seventy six practice pairs, and the remaining three hundred and eighty five measure performance on unseen pairs. Three fixed splits change which questions belong to each group. Calibration measures the waiting-time curve. Validation uses separate seeds to test the policies. Ninety calibration observations include twenty reused original runs. Five hundred and forty fresh budget attempts contain twelve hundred and sixty constituent runs.

## Slide 4

Python generates all number pairs and their correct labels. It selects disjoint datasets and trains the same small transformer each time. The model contains thirty six thousand nine hundred and ninety two adjustable parameters. Python checks accuracy every twenty five updates and records the trace in CSV files. Checkpoints save the weights, optimizer and random state for resumption. R reads the completed records, computes statistics and draws the graphs. Automated checks verify correct labels, dataset separation, independent seed lists, endpoint reconstruction and exact budgets. A technical failure is separate from a completed run that does not learn in time.

## Slide 5

T is the final confirming step after three checks with at least ninety nine percent practice accuracy and ninety five percent new-question accuracy. U is the smaller of T and the cap C, so it is fully observed even when eventual learning time remains unknown. F of t is the proportion of calibration runs confirmed by t. For k independent starts, all fail with probability one minus F of B divided by k, raised to k. Subtract that from one to obtain the chance at least one works. Bernoulli means one yes-or-no outcome; binomial means a count of successes. Exact confidence intervals show sampling uncertainty. We use twelve Fisher comparisons with Holm correction. Supporting correlation, regression and ANOVA analyses remain exploratory because their assumptions are imperfect.

## Slide 6

This recorded calibration run illustrates the delay. Practice accuracy improves first, while new-question accuracy improves later. It is the run closest to the original-split median, not an average or the best run. First confirmation occurs at four thousand three hundred and seventy five updates. Across the thirty original-split calibration observations, the capped mean is about five thousand three hundred and forty seven, the median four thousand three hundred and seventy five and the sample standard deviation about four thousand six hundred and ten updates. One trajectory cannot describe the variation across all starts.

## Slide 7

Every bar uses thirty fresh budget attempts. At eight thousand total updates, one long run succeeds twenty eight times on each split. Four shorter runs succeed twelve, nine and eleven times. All three four-versus-one differences survive Holm correction across the twelve planned tests. Two-run counts are twenty three, twenty four and twenty five, but those comparisons do not reach the corrected threshold. This does not prove equality. Each four-run attempt gives each constituent only two thousand updates, which can be too little time for delayed learning.

## Slide 8

The table includes every split and both budgets. Each entry is successes out of thirty attempts. At twelve thousand updates, one long run succeeds thirty times on every split. Four-run counts are twenty four, twenty and twenty three. Only the second-split four-run comparison survives correction. Four of the twelve planned first-confirmation comparisons are significant in total. The original thirty-thousand-update comparison gave ten successes out of ten for every policy. That earlier ceiling result and these smaller-budget differences can both be true. Budgets were chosen from the older curves and fixed before fresh validation.

## Slide 9

Three good checks do not ensure that accuracy stays high. We separately require twenty one successful checks spanning five hundred updates, with the final check inside the same allocation. On split one at eight thousand total updates, four starts produce twelve first confirmations but only four longer-window confirmations. These endpoints come from the same attempts and are correlated. The stability comparisons are secondary descriptive analyses. Our conclusion applies to one arithmetic task, one small model and three fixed splits. Future work can use other tasks, more splits and longer observation windows.

## Slide 10

The measured answer is that one long run is more reliable than four short starts at eight thousand total updates in these three fixed splits. Smaller differences, including the two-run comparisons, remain unresolved. The complete paper contains all results, uncertainty intervals and limitations. We credit the researchers who introduced grokking and established restart theory. Our contribution is the reproducible empirical comparison. We make no worldwide-first claim and the college similarity review remains separate.