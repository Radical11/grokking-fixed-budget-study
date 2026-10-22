# Review 1 speaker notes

Main presentation: 11:20 planned, including graph pauses. Slides 14-15 are optional.

Replace the editable name and registration-number fields before presenting. These explanations use the frozen Review 1 results.

## 1. Grokking Under a Fixed Budget

Time: 20 seconds; start at 0:00.

The project asks how long a small learning program takes to do well on new questions. We repeat the training and compare the waiting times. We then ask whether a fixed amount of training is better spent on one long attempt or several fresh starts. These are the Review 1 results.

Sources: [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 2. Our problem and objectives

Time: 50 seconds; start at 0:20.

A neural network is a computer program that improves its answers by adjusting numbers inside it. We give it practice examples, then check questions that it did not practise on. Doing well on these new questions is called generalization. Two training attempts can take different amounts of time because their starting numbers differ. We want to measure how much these times vary, compare three weight-decay settings, and estimate the chance of learning within a limit. Finally, we use those chances to predict whether restarting might help. A training budget here means a fixed number of learning steps.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 3. What is grokking?

Time: 50 seconds; start at 1:10.

Think of a student practising a set of maths questions. The student may remember those answers but struggle when the numbers change. Later, the student can apply the rule to new questions. This is an analogy for the pattern we measure in the computer. Memorization means doing well on the practice examples. Generalization means doing well on questions excluded from practice. Grokking is the delayed improvement on these new questions after the model already does well on the practice set. The delay is the key idea. It does not mean every model will grok or that we have proved human-like understanding. Accuracy means the percentage of answers that are correct. Power and colleagues introduced this research phenomenon; our project studies its timing and budget implications.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 4. How we run the experiment

Time: 65 seconds; start at 2:00.

Our task is modular addition. Mod means keep the remainder after division. For example, 30 plus 4 is 34, and dividing 34 by 31 leaves remainder 3. We generate all 961 pairs of numbers from zero to 30. The computer practises on 576 pairs, and we test it on 385 different pairs. The same split is used in every attempt. A random seed is a number that lets us repeat a random starting point. Changing the seed gives a new set of starting weights; weights are the adjustable numbers inside the model. An update is one learning step using all practice examples. Python runs the experiment and records the answers; R calculates the statistics. The fixed model is a small transformer, a type of neural network. Its detailed architecture is in the report. There are 24 main attempts; nine setup attempts are excluded from the results.

Sources: [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 5. How we measure learning time

Time: 65 seconds; start at 3:05.

We need one clear rule for when to count success. We check the model every 25 updates, where an update is one learning step. It must get at least 99 percent of practice answers and 95 percent of new answers correct at three checks in a row. We record T at the third check. If the qualifying checks are at 2000, 2025 and 2050, T is 2050. A random variable is a measured quantity that can change across repeated attempts; T is our example. Every attempt continues to the limit C of 30000 updates. If it has not succeeded, we do not know its eventual T. For average comparisons, U is the smaller of T and the limit. This is called capped time. Three successful checks give a clear first-success measure, but performance can still fall later.

Sources: [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 6. How much do learning times vary?

Time: 55 seconds; start at 4:10.

The baseline is the setting chosen as our reference: weight decay 1. Its twelve attempts are shown in the histogram, which groups waiting times into intervals. The mean is the average: 6475 updates. The median is the middle of the sorted times, averaging the two middle values here: 4275. Standard deviation, or SD, measures how spread out the times are around the average; it is about 7041 updates. One slow attempt takes much longer than most, so the average is higher than the median. The range runs from 1875 to 27175. Point to the last bar and explain that one attempt can give a very different impression from the whole sample. These are statistics from twelve observed attempts, not a guarantee about future attempts.

Sources: [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 7. What is the chance of learning in time?

Time: 60 seconds; start at 5:05.

The curve answers how likely an attempt is to succeed before a chosen limit. F of t is the chance of success by update t. We estimate it by counting successes and dividing by all twelve baseline attempts. By 2400 updates, three of twelve succeeded: 25 percent. A Bernoulli outcome is one yes-or-no result: did this attempt succeed in time? A binomial count is how many successes occur across independent attempts with the same chance. By 30000, all twelve succeeded. That does not guarantee that the next attempt will succeed. The 95 percent confidence interval is 73.5 to 100 percent. It shows the uncertainty from a small sample. In repeated studies, this interval-making method covers the true probability at least 95 percent of the time; it is not the probability that a particular next run will succeed.

Sources: [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 8. How we compare the results

Time: 55 seconds; start at 6:05.

We choose a statistic to match the question. Welch's t-test compares two group averages. ANOVA means analysis of variance: it compares all three averages together. Correlation measures how two quantities vary together. Regression fits a line describing their relationship. The ANOVA p-value is 0.0077. A p-value measures how surprising this result would be if the underlying group averages were equal, assuming the test's conditions. It is not the probability that our conclusion is correct. Our model's errors do not have the bell-shaped pattern assumed by the usual test, so we treat this as early evidence. Shuffling group labels gives a further check, but that also has assumptions. Detailed results are in the written report.

Sources: [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 9. Grokking in one training attempt

Time: 60 seconds; start at 7:00.

The blue line is the percentage of practice questions answered correctly. The grey line is the percentage of new questions answered correctly. The blue line reaches high accuracy first. The grey line improves later, showing the delay we call grokking. This example reached the practice threshold at 150 updates and the new-question success rule at 3150. We chose a run near the baseline middle, not just the fastest example. The graph shows the first 6000 updates; the full attempt continues to 30000. Across the 24 main attempts, 18 later had a drop below 95 percent on new questions. Our waiting time therefore records the first confirmed success; staying successful is a further question.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 10. What happened when we changed weight decay?

Time: 55 seconds; start at 8:00.

Weight decay is a training control that gently shrinks the adjustable numbers, or weights, inside the model. We vary this control while keeping the model and practice/test split the same. Each dot is one training attempt. The groups have 6, 12 and 6 attempts. Their average waiting times are about 13138, 6475 and 1888 updates. In these results, larger weight decay goes with shorter waiting times. All 24 attempts succeeded within 30000 updates. This is useful early evidence, but the groups are small and use one fixed set of questions. We cannot assume that the same setting is best for every model or task. The baseline was selected through separate setup runs before these comparisons.

Sources: [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 11. One long run or several fresh starts?

Time: 65 seconds; start at 8:55.

A restart means beginning again with fresh starting weights. We do not continue from the previous attempt. Suppose B is the total training budget and k is the number of attempts; each receives B divided by k updates. F of that smaller limit is the chance that one attempt succeeds. The chance that it fails is one minus that chance. If the attempts are independent, multiply their failure chances to find the chance that all fail. Subtracting that from one gives the chance that at least one works. With a total budget of 30000, our predictions are 100 percent, 99.3 percent and 99.6 percent for one, two and four attempts. These are predictions from twelve baseline runs and are unvalidated in this Review 1 cohort. At a smaller budget of 2400, the predictions are 25 percent, zero and zero; zero observed successes does not prove the true chance is zero.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 12. Progress and next questions

Time: 60 seconds; start at 10:00.

The first-review milestone includes code to train the model, record results, continue saved training, run repeat attempts and calculate preliminary statistics. It represents the planned 65 percent of implementation. Review 2 will cover more settings and attempts, fresh-seed restart comparisons, and statistical descriptions of the timing distribution. Candidate distributions are mathematical shapes that may describe how waiting times are spread. Multiple regression considers more than one explanatory factor; two-factor ANOVA compares two experimental controls together. Further questions are whether smaller budgets reveal clearer differences, whether changing the practice/test split changes the findings, and whether success stays high for a longer period. These questions help us judge how widely the initial result applies.

Sources: [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 13. Where the ideas come from

Time: 20 seconds; start at 11:00.

The background ideas have earlier research. Power and colleagues studied grokking; Truong and colleagues studied timing prediction; Streeter and colleagues studied restart schedules. Our proposed contribution is the controlled experiment connecting learning-time variation with budget allocation. The displayed measurements come from this project's recorded attempts. The references also include the official syllabus.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [2] Truong et al. (2026), preprint - https://arxiv.org/abs/2605.18845; [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/

## 14. Appendix A: restart probability, step by step

Optional question slide; outside the main timing.

This example uses invented numbers to explain the calculation, not a measured project result. Suppose the total budget is 12000 and we make two independent attempts of 6000 updates each. Assume each has a 60 percent success chance, so each has a 40 percent failure chance. Both fail with chance 0.4 times 0.4, which is 0.16. At least one succeeds with chance one minus 0.16, which is 0.84 or 84 percent. To compare with one long attempt, we also need its success chance by 12000. Independent means one attempt's outcome does not change the other's chance, conditional on the same settings and split. We use fresh starting weights for each. The estimated policy predictions share the same reference sample, so their estimation errors can still be related.

Sources: [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [4] BAMAT207 supplied official syllabus, version 1 - sources/

## 15. Appendix B: useful terms and questions

Optional question slide; outside the main timing.

A model is the program learning from examples. A seed chooses a repeatable random starting point. An update is one adjustment of the model's internal numbers. Generalization means doing well on questions excluded from practice. Standard deviation measures spread. A confidence interval expresses uncertainty using a method with a stated long-run coverage rate. If asked why this is a statistics project, explain that repeated random starts produce different waiting times and that the sample estimates their spread and success chances. If asked about an unfinished attempt, explain that its eventual time remains unknown. If asked about originality, cite the existing ideas and describe the project's recorded experiment. If asked about permanence, point out the later accuracy drops. An official plagiarism score still requires the college's checker. For detailed statistical questions: Pearson correlation uses a straight-line relationship and Spearman uses ranks. The fitted regression uses log weight decay, which changes the scale of the input. Residuals are observed values minus the fitted values; their normality diagnostic fails. The permutation sensitivity p-value is about 0.013. Shuffling requires observations to be interchangeable under the equal-means assumption. Holm adjustment controls the risk from making several pairwise comparisons.

Sources: [1] Power et al. (2022) - https://arxiv.org/abs/2201.02177; [2] Truong et al. (2026), preprint - https://arxiv.org/abs/2605.18845; [3] Streeter, Golovin and Smith (2007) - https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf; [4] BAMAT207 supplied official syllabus, version 1 - sources/; [5] Project Review 1 evidence - data/review1_summary.csv; output/review1/
