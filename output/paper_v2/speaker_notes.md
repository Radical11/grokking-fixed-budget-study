# Paper-v2 speaker notes

Main timing: 11:40. Slides 14-15 are optional. Replace name/registration fields before use.

## 1. Grokking Under a Fixed Budget

Target 20 seconds; start 0:00.

This paper asks how much training a small learning program needs before it answers new questions correctly. We measure the variation across random starts and test one long attempt against several fresh starts. The follow-up uses smaller budgets and three fixed dataset splits. We report uncertainty and accept negative or inconclusive results.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 2. What is grokking?

Target 60 seconds; start 0:20.

Think of practising maths questions and then trying questions with different numbers. Memorization means doing well on the practice examples. Generalization means doing well on questions held back from practice. Grokking is the delayed improvement on these new questions after practice performance is already good. Accuracy is the percentage of correct answers. This analogy explains the measured pattern; it does not prove human-like understanding or permanent learning. Our computer task is simple arithmetic, so every correct answer is known exactly. Power and colleagues introduced the phenomenon; our project studies its timing and the chance of success within a budget.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 3. Our question and why we extended the study

Target 50 seconds; start 1:20.

One update means one learning step using the practice data. A budget is the total number of these steps we can afford. A restart begins again from new random starting weights, rather than continuing the old model. We ask whether spending the same total steps on one attempt, two attempts or four attempts changes the chance that at least one learns. In the original validation at thirty thousand updates, every policy worked ten times out of ten. That is a valid result, but the generous budget made differences hard to see. We selected eight thousand and twelve thousand from the original completion curves, and disclosed that choice before the new experiments.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 4. The experiment in plain language

Target 70 seconds; start 2:10.

The rule is addition modulo thirty one: add two numbers and keep the remainder after division by thirty one. Thirty plus four gives remainder three. There are nine hundred and sixty one ordered pairs. In the baseline, five hundred and seventy six are practice questions and three hundred and eighty five are new questions. A dataset split chooses which pairs go into each group. We use three fixed splits. A seed chooses repeatable random starting weights, which are the numbers the model adjusts. Weight decay is a control that gently shrinks these numbers; we keep it at one in the follow-up. Thirty calibration runs per split estimate completion probabilities; twenty old runs are reused once. Separate fresh runs make five hundred and forty budget attempts. The architecture and numerical settings stay fixed.

Sources: [4] Ootani (2026) - https://arxiv.org/abs/2607.05104; [5] Loshchilov and Hutter (2019) - https://arxiv.org/abs/1711.05101; [6] Vaswani et al. (2017) - https://arxiv.org/abs/1706.03762; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 5. How we count first success and longer stability

Target 60 seconds; start 3:20.

This is a representative calibration run selected near the original-split median. Practice accuracy improves before new-question accuracy. An update is one learning step using all practice examples, and we check every twenty five updates. First success T requires at least ninety nine percent practice accuracy and ninety five percent new-question accuracy for three checks in a row. Here the final confirming check is at 4375 updates. The secondary measure needs twenty one checks, spanning five hundred updates. We count the final check, never the start of the streak, and never use observations beyond the run budget. Even the longer window does not mean that accuracy stays high forever.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 6. How much do learning times vary?

Target 55 seconds; start 4:20.

Each completion curve uses thirty calibration runs for one fixed split. At a chosen step, count how many have confirmed success and divide by thirty. Keep every unfinished run in the denominator. The original-split capped mean is about 5347 updates and the median about 4375. Capped means that if a run has not succeeded by thirty thousand, U records the limit; its eventual T is still unknown. Different curves reveal both random-start variation and differences among these fixed partitions. They do not represent all possible models or tasks. The paper includes the complete timing distributions and intervals.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 7. Probability and statistical methods

Target 70 seconds; start 5:15.

A Bernoulli outcome is one yes-or-no result: did this budget attempt succeed? A binomial count is the number of successes among independent attempts with the same setting. Exact confidence intervals show uncertainty from a finite sample. F of t is the single-run completion probability by step t. The restart formula is one minus the probability that every independent start fails. For group comparisons we report differences in success probabilities. The twelve planned Fisher tests compare each restart policy with one long run, and Holm adjustment accounts for considering twelve tests together. Bootstrap resampling provides a sensitivity view. We also use conservative exact bounds because a sample with all successes or all failures can make bootstrap uncertainty look too small.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [7] Official supplied BAMAT207 syllabus, version 1 - sources/; docs/SYLLABUS_MAP.md; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 8. Fresh results at two smaller budgets

Target 60 seconds; start 6:25.

This graph shows the original split at the two fixed budgets, with thirty fresh attempts per policy in each budget. The side table gives the success counts. All policies in one budget spend the same total updates: one gets B, two get B divided by two each, and four get B divided by four each. Every allocated step is executed even if one run succeeds early. The counts come from independent validation seeds, not the calibration sample used for predictions. Read the size and direction of the differences, then explain that finite-sample intervals and the corrected tests determine how much evidence there is. A point estimate alone does not justify a universal winner.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 9. Do the results depend on the dataset split?

Target 55 seconds; start 7:25.

Here we show the eight-thousand-update comparison on all three fixed splits. The practice and new-question assignments change, while the model, optimizer and success rule remain the same. Every displayed policy group has thirty fresh attempts. The full paper also reports twelve-thousand-update results on all three splits; we are not showing only a successful condition. Repetition across splits makes the evidence more informative, but three partitions of one arithmetic task do not establish transfer to large models or natural-language data. Compare the pattern and its variation rather than assuming that matching ranks prove a universal rule.

Sources: [4] Ootani (2026) - https://arxiv.org/abs/2607.05104; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 10. Predicted chance versus fresh observations

Target 65 seconds; start 8:20.

Calibration gives a measured single-run completion curve for each split. Before validation, we freeze the input trace hashes and all predicted policy probabilities. The predictions use one minus one minus F of B divided by k, raised to k. The graph compares these frozen predictions with the fresh original-split observations at both budgets. These are separate samples. Prediction error therefore contains uncertainty from both calibration and validation; the paper resamples them independently and also provides exact bounds. A close match is useful evidence about this setting, not proof of a true distribution or perfect calibration at every possible budget.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 11. Brief confirmation and a 500-update window

Target 65 seconds; start 9:25.

Both outcomes come from the same attempt, so they are correlated. The first rule confirms three successful checks; the longer rule confirms twenty one. The longer window must finish inside the same allocated budget. It receives no extra follow-up time. Its count cannot exceed the first-confirmation count. In the original main study, sixty two of eighty three generalized runs later dipped below ninety five percent held-out accuracy. That is why we distinguish first success from longer stability. The follow-up window is still finite and may be followed by another dip. These stability comparisons are secondary descriptive results, rather than another hidden family of significance tests.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 12. What the paper establishes

Target 50 seconds; start 10:30.

At eight thousand total updates, one long run succeeded twenty eight times out of thirty on every split. Four short runs succeeded twelve, nine and eleven times out of thirty. All three differences survived the correction for twelve planned comparisons. At twelve thousand updates, only the second-split four-run difference survived correction. No two-run comparison was detected, which does not prove equality. Giving each run too few steps can leave too little time for delayed learning. This conclusion applies to our model, task and three fixed splits. We report all intervals and distinguish brief confirmation from a longer window. Future research can test new tasks, more splits and longer accuracy windows.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 13. Sources and contribution

Target 20 seconds; start 11:20.

Grokking, timing prediction, restart schedules and numerical fragility have prior research. The paper credits these sources and the standard transformer and AdamW methods. Our contribution is the controlled experiment and its recorded results. The source record explains the limited local copied-phrase screen; an institutional similarity score still depends on the college checker.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [2] Truong et al. (2026) - https://arxiv.org/abs/2605.18845; [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [4] Ootani (2026) - https://arxiv.org/abs/2607.05104; [5] Loshchilov and Hutter (2019) - https://arxiv.org/abs/1711.05101; [6] Vaswani et al. (2017) - https://arxiv.org/abs/1706.03762; [7] Official supplied BAMAT207 syllabus, version 1 - sources/; docs/SYLLABUS_MAP.md; [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/

## 14. Appendix A: a worked restart probability

Optional question slide.

This is an illustration, not a measured result. If two independent attempts each have sixty percent success, each has forty percent failure. Both fail with probability zero point four times zero point four, or zero point one six. At least one succeeds with probability one minus zero point one six, or eighty four percent. To decide between this and one longer run we still need the longer run probability. Independence refers to random starts conditional on the fixed task and training setting.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [7] Official supplied BAMAT207 syllabus, version 1 - sources/; docs/SYLLABUS_MAP.md

## 15. Appendix B: full validation counts

Optional question slide.

Every entry shows the first-confirmation count and the five-hundred-update count, each out of thirty attempts. The two counts in an entry are paired endpoints from the same attempts, not independent replications. The six rows cover every split and budget. The paper and supplement provide exact probability intervals, the twelve corrected comparisons, candidate timing fits, exploratory syllabus analyses and all limitations.

Sources: [8] Project paper-v2 evidence - data/paper_v2/; output/paper_v2/
