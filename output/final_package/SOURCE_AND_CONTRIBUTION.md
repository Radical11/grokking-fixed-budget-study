# Sources and contribution record

## Attributed background

- Power et al. introduced the grokking phenomenon and studied delayed generalization on small algorithmic datasets: https://arxiv.org/abs/2201.02177
- Truong et al. (2026 preprint) study prediction of grokking delay: https://arxiv.org/abs/2605.18845
- Streeter, Golovin and Smith study restart schedules for ensembles of problem instances: https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf
- Probability and statistics methods are mapped to the supplied official BAMAT207 syllabus in `docs/SYLLABUS_MAP.md`.

## This project's work

The project implements modular addition modulo 31, records repeated training attempts under a fixed protocol, measures first confirmed time to generalization and capped time, and compares equal logical update budgets allocated to one, two or four fresh starts. It preserves raw per-run traces and applies the syllabus methods in R. Its proposed empirical contribution is this specific connection between learning-time variability and restart budgets. The prior literature was searched and a close match was not located in that search; a worldwide novelty claim is not established.

The results in the final presentation and report come from 199 completed training runs: nine pilot runs, 120 main-study runs and 70 fresh-seed validation constituents. The restart comparison has ten attempts per policy. These counts are recorded in the repository data and checked by the reproduction script.

## Similarity review

`originality_screen.json` records a local exact contiguous phrase comparison of the final report body, visible slide text, speaker notes, paper abstract and methods supplement against the three cited research PDFs. Bibliographic title, author and URL strings are excluded from slide text; the report bibliography and supplement's attribution section are excluded. Any phrase matches should be reviewed in context, because standard statistical language and properly attributed technical descriptions can overlap.

This screen does not search the college's past submissions or the full internet, and it does not detect paraphrasing, code reuse or AI authorship. The institution's similarity score remains pending until the required checker and its settings are known. No score or percentage is claimed here.
