# Methods and interpretation supplement

This document supports the seven-page final report in `output/pdf/review2_report.pdf`. It describes the implemented analysis and its limits. The experiment protocol is recorded in `docs/PROTOCOL.md`; this is a reproducible lab study, not a claim of a formally registered clinical or confirmatory trial.

## Question and scope

How variable is the number of training updates until a model first meets a generalization rule? Within the same model, dataset setting and total update budget, is success more likely from one long run or several independent restarts?

The population considered is repeated random initialization of this model on the fixed modular-addition split. It does not represent all neural networks, datasets or training procedures. Generalization means correct answers on pairs excluded from training. Grokking denotes the delayed improvement pattern studied by Power et al.; this project additionally uses an explicit timing rule to classify delayed versus rapid learning.

## Experimental unit and controls

The main experimental unit is one independently initialized training run. Inputs are all 961 ordered pairs of integers from 0 through 30; labels are `(a+b) mod 31`. The model sees three tokens (two operands and a separator) and predicts one of 31 possible residues. The same small causal transformer and optimizer are used in all main runs. The detailed architecture, numerical precision and training settings are in `configs/study.json`, `grokking/model.py` and the protocol.

The data permutation uses split seed 20261013. The 40% condition has 384 training and 577 held-out pairs; the 60% condition has 576 training and 385 held-out pairs. The smaller training set is a prefix of the same permutation, so the two conditions also have different held-out pair sets. Initialization seeds vary independently of the split seed. Comparisons across data fractions are conditional on these splits. New split seeds would be a separate replication.

Nine pilot runs (three seeds at each decay, using 60% data) were used only for baseline selection. The pre-set rule selects eligible settings with delayed generalization in at least two pilot seeds, taking the median event time closest to 7,500 updates. It selected weight decay 1. Pilot observations are excluded from the main statistical comparisons.

The main study contains 20 seeds in each of six cells: two fractions (40%, 60%) by three weight decays (0.3, 1, 3), giving 120 runs. The frozen first-review 24 runs are reused in these 120; they are not added as another independent sample. The architecture was held fixed throughout collection.

## Operational endpoints

One update means one full-batch optimizer adjustment. Evaluation occurs every 25 updates, after update zero. Let A_train(j) and A_new(j) be the two accuracies at evaluation j. A qualifying checkpoint requires A_train(j) >= 0.99 and A_new(j) >= 0.95. T is the update at the third consecutive qualifying evaluation. For checks at 2,000, 2,025 and 2,050, T=2,050. This is the confirmation time; it is not backdated to 2,000.

Memorization time M separately confirms three consecutive training accuracies >=0.99. A run is operationally delayed if T >= 3M and T-M >= 200 updates. This separates a delay from ordinary rapid learning without proving an internal learning mechanism. A relapse flag records any later evaluated held-out accuracy below 0.95 after first confirmation. Later dips do not reset T.

Every main run continues to the common limit C=30,000. Let delta=1 if T<=C and delta=0 otherwise. Unfinished observations retain unknown T as a blank field. For a fully observed comparison define U=min(T,C); for delta=0, U=C by definition. This is an outcome with a cap, not an invented completion time. The mean, median, variance and regression/ANOVA results in the report describe U. They do not estimate the unrestricted mean or variance of T.

## Probability and intervals

For 0<=t<=C, the empirical CDF is F_hat(t) = count(delta_i=1 and T_i<=t)/n. All completed main runs in that setting remain in the denominator, including unfinished outcomes. Only a histogram explicitly labelled as observed events omits unfinished times. No empirical completion probability beyond C is inferred.

Each run's success by a fixed budget is a Bernoulli outcome. With independent starting seeds in the same condition, the count among n runs is treated as binomial with a common conditional success probability. Exact 95% Clopper-Pearson intervals are computed by base R `binom.test`. Percentile bootstrap intervals for mean U resample n observations with replacement 1,000 times. The analysis fixes R's random seed to 20261013. These intervals describe uncertainty from the finite sample; none guarantees success on the next run.

In a cell with no events, observed U is identically C, giving SD(U)=0 and a degenerate bootstrap mean interval. This does not show that T is constant or remove uncertainty about unobserved events/tails. The binomial interval is still relevant for success probability by C.

## Exploratory comparisons

At 60% training data, pairwise Welch tests compare mean U across the three decay settings. The three p-values are adjusted together by Holm's method. Bootstrap differences are also recorded. One-way ANOVA tests the joint equal-mean hypothesis for these three groups. Pearson correlation relates log(weight decay) to U, while Spearman correlation uses ranks. Simple regression uses U ~ log(weight decay).

Across all 120 runs, multiple regression uses U ~ train_fraction + log(weight_decay). A separate factorial model uses U ~ factor(train_fraction) * factor(weight_decay), with sum contrasts and 20 runs per cell. Its two main-effect tests compare factor mean patterns; its interaction asks whether one factor's effect changes across the other. The additive multiple-regression coefficients are distinct from the factorial ANOVA contrasts. R-squared measures explained sample variation; it is not a held-out prediction score.

The one-way sensitivity check permutes outcomes across groups 1,000 times. For the factorial terms, a reduced-model residual permutation holds the other terms in the model, adds permuted null residuals to the null fitted values, and refits the full and reduced models. The permutation p-value uses (1 + count(F_perm>=F_observed))/1001. It has resolution 1/1001. This is an exploratory sensitivity analysis, not a remedy for every violation: exchangeable errors are required. Capping, unequal spreads and a completely censored cell make the usual normal, equal-variance model conditions doubtful. Residual plots and Shapiro-Wilk results are supplied. P-values are interpreted with these limits and the number of exploratory comparisons in view.

## Candidate timing distributions

Exponential, Gamma and Weibull candidate families are fitted to the selected baseline only. Define a positive latent grid variable X=T-50 to account for the two extra 25-update checks used in confirmation. For a recorded event at update t, the model probability is G_X(t-50)-G_X(t-75), with G_X(x)=0 for x<=0. An unfinished observation contributes 1-G_X(C-50). The likelihood is the product of these event masses and survival probabilities. Positive parameters are optimized on the log scale. AIC=2q-2*log(L), where q is the number of fitted parameters; a lower AIC ranks candidates more favourably within this comparison.

The actual baseline fit contains 20 events and zero unfinished observations. The implemented likelihood supports unfinished data, but this particular fit does not empirically demonstrate tail recovery under censoring. Gamma has the smallest baseline AIC (253.96), versus Exponential 257.15 and Weibull 256.85. The small sample and close ranking do not establish a universal timing law.

## Restart predictions and independent validation

Let B be the total number of logical training updates and k be 1, 2 or 4. Each fresh run receives B/k updates, in the same baseline setting. Conditional independence gives P(all fail)=[1-F(B/k)]^k, hence P(at least one success)=1-[1-F(B/k)]^k. Predictions substitute the empirical F from the 20 main baseline runs. Prediction intervals in the numerical output transform single-run exact binomial intervals through this monotone formula; they describe calibration uncertainty and are correlated across budgets and policies.

Fresh validation uses seeds separate from pilot and main runs: ten independent budget attempts per policy at B=30,000. An attempt has k constituent training runs, all of which complete their allocated updates, even if success is already observed. This yields 30 attempts and 70 constituent runs with exact equal logical allocation per attempt. The success outcome is whether any constituent confirms the same T rule within its own allocation. All policies succeeded 10/10, with exact 95% intervals 69.2%-100%. This does not identify a winner or prove equivalence. The all-identical outcome table is described without forcing a chi-square or Fisher test. Smaller-budget predictions remain unvalidated.

## Execution, reproduction and limitations

All experimental training used the recorded CPU configuration; CUDA was unavailable in the execution environment. Checkpoint recovery preserves logical trajectories but may repeat unsaved physical work. Recorded runtime excludes downtime, may omit lost partial-checkpoint work, and is affected by concurrent CPU contention. Equal logical updates are the primary budget; no controlled wall-clock or total physical-compute comparison is claimed. Different data fractions also have different work per update.

Run `.venv\Scripts\python.exe scripts\verify_project.py --reproduce --run-tests` from the repository root. The command checks preserved report inputs, runs the tests, reproduces R tables and all eight graphs in an isolated folder, performs the raw-trace audit and rebuilds the seven-page report. It compares numerical tables, graph pixels and report text to the saved deliverables. Checkpoints and local runtimes are not included in version control; the complete raw evaluation histories and training configuration are included.

## Attribution

- Power et al. (2022), *Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets*: https://arxiv.org/abs/2201.02177
- Truong et al. (2026 preprint), *First-Passage Prediction of Grokking Delay*: https://arxiv.org/abs/2605.18845
- Streeter, Golovin and Smith (2007), *Restart Schedules for Ensembles of Problem Instances*: https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf
- Supplied official BAMAT207 syllabus: preserved under `sources/`, mapped in `docs/SYLLABUS_MAP.md`.

The timing/restart connection is a proposed empirical contribution in this controlled setup. No worldwide-first claim or institutional similarity clearance is made. See the final source-and-contribution record for the limited phrase-overlap screen.
