# Literature comparison and scope of the contribution

The numbered references match the paper, supplement and presentation. Public PDFs and their hashes/page counts are recorded in `output/paper_v2/sources.json`. This comparison describes the cited work; it does not certify an exhaustive novelty search.

| Prior work | Relevant established contribution | What this project evaluates |
| --- | --- | --- |
| [1] [Power et al. (2022)](https://arxiv.org/abs/2201.02177) | Delayed generalization in small algorithmic learning tasks. | Repeated completion times and the probability of meeting a specified accuracy rule within a fixed update budget. Grokking itself is not our discovery. |
| [2] [Truong et al. (2026), preprint](https://arxiv.org/abs/2605.18845) | A first-passage account and calibrated prediction of grokking delay under AdamW, with mechanistic interventions. | Empirical completion curves and fresh validation of finite budget allocations. We do not introduce the random-time framing or derive a new mechanistic timing law. |
| [3] [Streeter, Golovin and Smith (2007)](https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf) | Selecting restart schedules using run-length distributions, including theoretical guarantees for randomized algorithms. | The fixed choices k=1,2,4 under two total budgets. Our empirical accuracy threshold differs from a provably correct Las Vegas algorithm result, so those guarantees are not transferred to the network. No schedule-optimality claim is made. |
| [4] [Ootani (2026), preprint](https://arxiv.org/abs/2607.05104) | Multi-seed grokking rates in a small modular-arithmetic transformer and sensitivity of individual seeds to the numerical environment. | Fixed CPU/thread/software settings, three fixed dataset partitions, and predicted versus observed policy success on separate seed cohorts. Seed variability and numerical sensitivity are already established concerns. |
| [5] [Loshchilov and Hutter (2019)](https://arxiv.org/abs/1711.05101) | Decoupled weight decay, used by AdamW. | An existing optimizer with fixed settings, not an optimizer contribution. |
| [6] [Vaswani et al. (2017)](https://arxiv.org/abs/1706.03762) | Transformer attention architecture. | A small fixed attention block for a controlled arithmetic experiment, not a new architecture. |

The proposed empirical contribution is the joint experiment: frozen completion-curve predictions, separate smaller-budget policy attempts, fixed-partition replication, exact logical budget accounting, and a second endpoint for a finite 500-update accuracy window. These elements do not establish worldwide priority. A negative or inconclusive policy comparison remains a valid result.

The supplied BAMAT207 syllabus [7] determines the course-method coverage. The original 120-run setting study supplies exploratory context; it is not pooled with the fresh policy attempts. Related preprints are identified as preprints rather than presented as settled peer-reviewed findings.
