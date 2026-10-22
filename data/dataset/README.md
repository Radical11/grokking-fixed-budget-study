# Dataset source

The [CSV](modular_addition_31.csv) contains all 961 ordered input pairs `a,b` from 0 to 30. `label = (a+b) mod 31`. These are generated arithmetic examples, not records downloaded from an external dataset or measurements of people. The accuracy traces elsewhere in `data/` are actual recorded training results, not invented values.

Each partition column identifies whether that pair was used for training or held-out evaluation in the specified split/fraction:

| Column | Training pairs | Held-out pairs |
|---|---:|---:|
| s20261013_f40 | 384 | 577 |
| s20261013_f60 | 576 | 385 |
| s20261014_f60 | 576 | 385 |
| s20261015_f60 | 576 | 385 |

The original exploratory study used 40%/60% fractions on split 20261013. The follow-up fixed 60% data and used the three listed split seeds. Changing the initialization seed does not alter the partition. Each row appears exactly once, and each partition column assigns it to exactly one of training or held-out evaluation.

Recreate this CSV using `python scripts/export_dataset.py`. It calls the same `grokking.model.make_dataset` function used for training; labels and partitions are verified before writing. No new training is performed.
