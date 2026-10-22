# Experiment protocol 1.0

Locked before main experiments on 13 October 2026.

## Task and model

Enumerate ordered pairs a,b in {0,...,30}, with class label (a+b) mod 31. Inputs are abstract learned tokens `[a,b,=]`, where `=` is token 31. A split-seeded permutation chooses floor(961*fraction) training pairs; the rest measure unseen accuracy. Data fractions share one permutation, giving nested training sets. Conclusions are conditional on this split.

One causal-attention block: embedding width 64, four heads of width 16, learned positional vectors, residual attention, residual ReLU feed-forward 64 -> 128 -> 64, and output at the final token to 31 classes. There are no biases, dropout or layer normalization. PyTorch standard embedding/linear initializers are used; positional weights use Normal(0,0.02). Model architecture and initialization rule stay fixed in all stages.

Full-batch cross-entropy and AdamW, learning rate .003, betas (.9,.98), epsilon 1e-8, weight decay applied to every model parameter. Float32, deterministic algorithms and TF32 disabled. Explicit causal attention avoids automatically switching attention implementations. CPU threads = 4. CUDA graph replay reduces launch overhead; warmup/capture updates are restored and never counted as training.

Pilot and main batches may use three independent CPU processes, each with four threads. Initialization RNG states are process-local; only the parent writes the aggregate CSV. CUDA batches use one process. Policy-validation attempts remain sequential. Wall-clock timing includes scheduling contention, so updates are the primary fairness measure.

## Outcomes

Evaluate at update 0 for context and every 25 updates thereafter. Update 0 does not contribute to confirmation. Memorization time is the third consecutive evaluation with training accuracy >= .99. Generalization time T is the third consecutive evaluation satisfying BOTH train >= .99 and unseen >= .95. A failed evaluation resets its corresponding streak. Confirmation time, not the start of the streak, is used in every budget calculation.

Operational delayed generalization: T >= 3 * memorization time AND T - memorization time >= 200 updates. This records a timing separation, not proof of a specific grokking mechanism. A later fall below .95 unseen accuracy sets a relapse flag; the original stopping event remains recorded. Thus success means reaching the sustained threshold, not permanent generalization.

Runs are trained to the full allotted cap even after an event, preserving follow-up traces. The event indicator remains distinct from failed/paused/completed execution status. Only completed main runs enter inferential analysis; technical exclusions are counted. An unknown T is blank, never represented by C. Capped time U=min(T,C) is fully observed for completed runs; no unrestricted tail beyond C is inferred nonparametrically.

## Pilot selection

At 60% data, train each weight decay (.3,1,3) with seeds 9000,9001,9002 for 30,000 updates. Eligible cells have >=2 delayed events. Select the cell whose median delayed-event T is closest to 7,500, ties resolved by lower decay. If no eligible cell, extend all pilot runs to 60,000 and apply the same rule. If none qualifies, save failure evidence and stop expansion. The selected cap becomes the common main-study cap. Pilot data never enter main or policy-calibration estimates.

## Main seeds and samples

Review 1: fraction .6, 12 baseline seeds and six seeds for each other weight decay = 24 runs. Review 2: .4/.6 x .3/1/3 with 20 seeds per cell = 120 runs including reused Review 1 data. Cell seed = 10000 + fraction_index*1000 + decay_index*100 + replicate_index (zero-based). This gives independent initializations without pairing seeds between cells.

## Restart experiment

For a fixed baseline setting and total budget B, k=1,2,4 from-scratch runs each get B/k updates. No weights or optimizer state transfer between restarts. This is not an ensemble prediction: an attempt succeeds if at least one constituent run reaches the confirmed threshold by its cap. The split is fixed; seeds are independent. All allotted updates are executed sequentially; wall-clock speedup from parallel hardware is not claimed.

Calibration F(t) = count(main baseline events with T<=t)/all completed baseline runs, only for t<=C. Predicted probability = 1-[1-F(B/k)]^k. Compare total budgets C/4,C/2,C descriptively; validate at B=C on fresh seeds. Validation seed = 50000 + policy_index*1000 + attempt_index*10 + constituent_index. Ten attempts per policy yield wide confidence intervals. All calibration and validation seed sets are disjoint.

## Analysis decisions

- Exact binomial 95% confidence intervals for success probabilities; transform these intervals monotonically for predicted policy probabilities.
- Capped mean/variance and bootstrap percentile mean intervals (1,000 resamples, R seed 20261013).
- Exploratory Welch mean comparisons and Holm correction; bootstrap difference intervals are supporting sensitivity summaries.
- One-way ANOVA at .6 data, plus a 1,000-permutation sensitivity test; Review 2 adds factorial interaction ANOVA and residual diagnostics.
- Pearson/Spearman correlation and simple/multiple regression of U on measured settings. Regression is exploratory, not a validated predictor for unseen tasks.
- Review 2 fits discretized Exponential, Gamma and Weibull baseline time models only with >=8 events. Two extra confirmation checkpoints add 50 updates: model X=T-50 with a positive continuous family, then P(T=t)=F_X(t-50)-F_X(t-75) on the 25-update grid. Unfinished runs contribute 1-F_X(C-50). Recorded T is known exactly; this discretization is a modeling choice, not a claim that events themselves are interval-censored. AIC ranks candidates; no distribution is declared true from a small sample.
- Validation contingency comparison uses chi-square only if expected counts are >=5; otherwise Fisher's exact test. Identical outcomes are reported descriptively. No equivalence conclusion from nonsignificance.

Primary goal is estimation and a prospective budget-policy check. Review 1 analyses remain exploratory; no significant-effect or restart-benefit claim is required for project success.
