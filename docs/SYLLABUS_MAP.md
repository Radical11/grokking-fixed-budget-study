# Mapping to the supplied BAMAT207 syllabus

The two source PDFs in `sources/` match the user's ZIP byte for byte and contain the same syllabus. Theory pages 1-2 list Modules 1-6; the embedded-lab list on page 2 covers EDA, distribution fitting, inference, regression and experimental design.

| Syllabus topic | Project use | Review |
|---|---|---|
| Random variables, expectation, variance | T, event indicator and capped outcome U; repeated-seed variability | 1 |
| Independence and conditional probability | At-least-one-success formula, conditional on task/settings/fixed split | 1 |
| Discrete distributions | Bernoulli event and binomial count of independent successes | 1 |
| EDA and descriptive statistics | Tables, event histogram, boxplot, learning curves and empirical F(t) | 1 |
| Lab EDA: skewness and kurtosis | Moment descriptors of U; undefined when capped outcomes are constant | 2 |
| Exponential/Gamma/Weibull | Candidate baseline time distributions retaining unfinished runs | 2 |
| Confidence intervals and hypothesis tests | Exact probability intervals, Welch comparisons, bootstrap sensitivity | 1-2 |
| Pearson/Spearman | Associations between setting and capped time | 1-2 |
| Simple/multiple regression | U vs log(weight decay), then data fraction plus decay | 1-2 |
| One-way ANOVA / CRD | Independent initializations across three decay settings | 1 |
| Two-factor ANOVA | 2 data fractions x 3 decay settings with replicated cells | 2 |
| Chi-square independence | Observed policy success vs k when counts justify it; Fisher otherwise | 2 |
| Module 6: contemporary topics | Grokking as a current machine-learning application; no additional specific topic is prescribed in the PDF | 1-2 |

We do not force Poisson, negative-binomial, paired t, F variance tests, RBD or Latin-square designs onto a study that does not supply their required sampling structure. Normality is a diagnostic assumption to assess, not a distribution to assume for grokking time. Bayesian inference and advanced survival theory are outside the core lab presentation.
