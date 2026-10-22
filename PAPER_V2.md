# Completed paper and final review

The follow-up is complete: 90 calibration observations (20 reused and 70 new), 540 fresh policy attempts and 1,330 new training runs. All 7.5 million planned logical updates were collected without failed runs. The original delivery is retained at the `review2-original` tag (`d8ffc56`).

Start with [the eight-page paper](output/paper_v2/paper.pdf), [four-page technical supplement](output/paper_v2/supplement.pdf), [editable presentation](output/paper_v2/presentation.pptx) and [matching slide PDF](output/paper_v2/presentation.pdf). The presentation has 13 main slides, two optional slides and 11:40 of planned speaker notes. Student identity fields remain editable.

At 8,000 total updates, one long run succeeds in 28/30 fresh attempts on every split; four shorter runs succeed in 12/30, 9/30 and 11/30. All three contrasts survive the pre-specified Holm correction. At 12,000 updates, only the second-split four-run contrast survives correction. No two-run contrast is detected; this does not establish equivalence. See the paper for intervals, all conditions and the separate 500-update stability endpoint.

See [the reproduction guide](paper/v2/README.md), [plain-language code walkthrough](paper/v2/CODE_WALKTHROUGH.md), [defence notes](paper/v2/DEFENSE_NOTES.md) and [source/contribution record](paper/v2/SOURCE_AND_CONTRIBUTION.md). Experimental settings and seeds were committed before training; calibration predictions were frozen before validation. The smaller budgets were selected from earlier results and that choice is disclosed.

Rebuild from saved data with `run_paper_v2.ps1 -AnalysisOnly`; inspect recorded progress with `run_paper_v2.ps1 -Status`. The output folder contains the numerical tables, high-resolution PNG/vector PDF figures, editable manuscript sources and verification records. Results apply to this task, model and three fixed splits. The limited cited-source overlap screen is not the college's official similarity check.
