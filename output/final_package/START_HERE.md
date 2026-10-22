# Final review package

This folder contains the editable final presentation and its evidence files. The main deck has 13 timed slides (11 minutes 35 seconds) and two optional question slides. Replace the name and registration-number fields on slide 1 before presenting.

## Files for the review

- `final_presentation.pptx` — editable slides, native charts and tables, and speaker notes.
- `../pdf/final_presentation.pdf` — static 15-page copy of the slide deck.
- `../pdf/review2_report.pdf` — seven-page final paper-style report, with the matching Markdown at `../pdf/review2_report.md`.
- `speaker_notes.md` — speaking outline, source notes and timing for each slide.
- `SOURCE_AND_CONTRIBUTION.md` — attribution, originality scope and contribution record.
- `originality_screen.json` — limited phrase-overlap screen; it is not a college similarity score.
- `core_verification.json` and `presentation_verification.json` — evidence for experiment/report reproduction and presentation checks.
- `package_manifest.json` — file hashes for the delivered code, data inputs, paper and presentation; verify with `scripts/final_manifest.py` (add `--check-git` to check committed bytes).
- `../../paper/README.md` — the paper index, abstract, bibliography, methods supplement, figure guide and data dictionary.

## What the results say

The study contains 120 main runs and 30 fresh-seed policy attempts (70 individual training runs). At 30,000 total updates, each restart policy succeeded in 10/10 attempts. The intervals are wide and the result does not identify a winner or prove equivalence. See the final report for the complete interpretation and limitations.

The final report can be reproduced with `.venv\Scripts\python.exe scripts\verify_project.py --reproduce`. The complete Python test suite can be added with `--run-tests`. This reproduces the analysis in an isolated folder and checks the R result tables and report text against the saved outputs; it does not retrain the neural network.

All eight paper graphs are also reproduced and compared pixel-for-pixel. To rebuild the editable presentation, run `scripts/build_final_presentation.ps1` using the documented Codex presentation dependencies; see `presentation/README.md`. Existing research reports are preserved. The presentation source contains editable identity fields; an official college similarity score remains pending its specified checker.
