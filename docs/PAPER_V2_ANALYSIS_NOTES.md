# Pre-validation analysis implementation note

This note is committed during calibration, before the new validation phase. It changes no seeds, budgets, training settings, endpoints, sample sizes or primary testing decisions.

The planned 5,000-resample bootstrap intervals remain in all numerical outputs. With a constant observed binary group, however, a percentile bootstrap can collapse and omit uncertainty about unobserved outcomes. To make this visible and protect the paper's uncertainty statements, also report conservative pointwise 95% difference bounds formed from two exact 97.5% binomial intervals. If the intervals are [L1,U1] and [L0,U0], the difference bounds are [L1-U0,U1-L0]. The two marginal noncoverage probabilities sum to at most 5%; this is conservative joint coverage for the pair, not simultaneous coverage across all twelve contrasts.

For prediction-minus-observation, transform a 97.5% calibration interval through 1-(1-p)^k, then subtract the independent observed-attempt 97.5% interval using the same bound construction. Calibration bootstrap and observed-attempt bootstrap samples remain independent. Exact 95% success intervals are still displayed for each individual proportion.

The main probability-difference figure uses the conservative bounds; bootstrap intervals remain a sensitivity result in the CSV. Report and supplement explain the distinction. The primary twelve two-sided Fisher tests and their joint Holm correction are unchanged. Secondary stability analyses remain descriptive. This is a documented implementation detail before validation, not a new outcome-selected hypothesis.
