# Data dictionary

## Run-level results: `data/summary.csv`

One row is one training run. There are 199 completed runs in the final dataset: 9 pilot, 120 main and 70 validation constituents. Stages have different purposes and must not be pooled for main-study estimates.

| Fields | Meaning |
| --- | --- |
| `run_id`, `stage` | Unique run identifier and `pilot`, `main` or `validation`. |
| `train_fraction`, `weight_decay` | Experimental condition. Fraction is a proportion, not a percentage integer. |
| `init_seed`, `split_seed` | Repeatable random initialization and data-partition seeds. |
| `split_hash`, `train_size`, `test_size` | Training-index hash and partition counts. |
| `max_updates`, `completed_updates` | Allocated and completed logical optimizer updates. These do not measure repeated work lost during interruption. |
| `memorization_time` | Third consecutive evaluated training accuracy >=0.99, in updates; blank if unobserved. |
| `generalization_time` | Third consecutive evaluated training >=0.99 and held-out >=0.95, in updates; blank if unobserved. |
| `event_observed` | Whether the generalization event was observed within the run's budget. |
| `delayed_generalization` | Whether the observed event satisfies T>=3M and T-M>=200. |
| `relapsed` | Whether a later evaluated held-out accuracy fell below 0.95 after T. |
| `final_train_acc`, `final_test_acc` | Final checkpoint accuracy proportions, not percentages. They can differ from the first-event threshold. |
| `elapsed_seconds` | Recorded active runtime with the documented interruption and contention limits. |
| `status`, `error` | Execution outcome and recorded error details. Software failure is distinct from no learning event within budget. |
| `device`, `torch_version`, `cuda_version` | Recorded runtime metadata. A CUDA-enabled library build does not establish that training used a GPU. |

## Per-run evidence: `data/runs/<stage>/<run_id>/`

`config.json` records settings; `trace.csv` contains `step`, `train_loss`, `test_loss`, `train_acc`, `test_acc`. Step zero records initial performance and does not count toward threshold streaks. Evaluation points are 25 updates apart thereafter. Summary/progress files record the completed outcome and execution state. Local checkpoint files support resumption and are ignored by Git; the full saved traces remain versioned.

## Policy attempts: `data/policies.csv`

One row is a complete budget attempt with `k` independent constituent runs. `attempt` identifies its repetition, `run_ids` links the constituents, `total_budget` is the intended total, `allocated_updates` is the sum allocated and `completed_updates` is the completed logical total. `success` means at least one constituent confirmed T within its allocation. `elapsed_seconds` is descriptive recorded runtime. There are ten rows for each k=1,2,4 and 30,000 updates per row.

## Analysis and missing values

Python Boolean values are `True`/`False`; base R reads its saved Boolean values as `TRUE`/`FALSE`. Blank event times indicate unobserved times, not zero. R-generated `NA` marks a value that is undefined or not applicable, such as skewness of a constant capped outcome or a policy-test p-value for all-identical outcomes. `U` is a derived analysis column in `output/review2/analysis_rows.csv`, equal to observed T when available and the cap otherwise. The original unknown T is retained.

`data/review1_summary.csv` is a frozen first-review snapshot; `data/baseline.json` stores pilot selection; `data/runtime_lock.json` fixes this study's execution environment. The primary final analysis uses only completed `main` rows from `data/summary.csv`. Policy validation uses its own separate seeds and attempt rows.
