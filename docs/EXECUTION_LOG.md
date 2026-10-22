# Execution record

## Review 1, 13-14 October 2026

Nine pilot and 24 main runs completed on the CPU. The five-page first-review report was generated, audited and visually checked. CUDA was unavailable in this execution environment; the dataset remains locked to the verified CPU/PyTorch/thread configuration.

## Review 2 resumed, 14 October 2026

The first-review aggregate CSV and original R source were frozen before collecting additional data. Its existing PDF remains separate. All 63 manifest inputs match working files and committed Git blobs.

The expansion adds 96 main runs. Sequential fresh-seed validation runs alongside the three-process main expansion, with aggregate CSV export deferred in the validation process to retain one writer. This affects measured runtime through CPU contention; the primary update budgets, model, optimizer, split and numerical configuration remain unchanged.

During implementation, the final analysis gained structured coefficient tables, residual diagnostics, and exploratory reduced-model residual-permutation sensitivity checks for factorial terms. They are supporting checks, not newly preregistered confirmatory claims. Permutation tests require exchangeable errors and do not remove unequal-variance concerns. The report gate requires a completed raw-trace audit and all intended samples before final PDF generation.

Completion counts and final conclusions will be recorded in the implementation status after collection and analysis finish.

At resumption on 14 October, 79 main runs and 16 policy attempts were complete. The earlier processes were no longer running; three main runs and one validation constituent retained resumable checkpoints. Collection resumed with the same device, seeds, caps and numerical settings. Background processes now write persistent logs; a one-shot finalization process runs export, R analysis, audit and report generation after collection ends. Visual PDF inspection remains a separate required completion check.

Budget counts refer to logical trajectory updates. Checkpoint recovery can repeat unsaved work, so exact physical compute equality is not claimed. Recorded active elapsed time excludes downtime and may omit work lost between checkpoints.

## Final completion, 14 October 2026

All 199 experimental training runs completed: 9 pilot, 120 main and 70 validation constituents. The 30 fresh policy attempts each recorded exactly 30,000 logical updates. Main data contain 83 events and 37 unfinished outcomes. All policies succeeded in 10/10 attempts; the final report describes the resulting ceiling and uncertainty without claiming equivalence.

The 21-test suite passed. Final export, actual base-R analysis, raw-trace audit and PDF generation completed successfully. A numeric check found finite losses and accuracies in all 199 traces, with accuracies within [0,1]. All seven final report pages were rendered and visually inspected, including the repaired diagnostic-axis layout. The five-page Review 1 artifact remains unchanged.

All 414 final and 63 frozen first-review manifest inputs matched their working-file hashes before the final result commit. Committed-blob verification follows that commit so line-ending normalization cannot silently invalidate the reproducibility record.

Post-commit verification at `58201ae` passed for all 477 manifest inputs against both working files and Git blobs. Three generated R text files required explicit byte preservation in `.gitattributes` after Git normalized their line endings. Their exact original bytes are now committed; report manifests and PDF content were unchanged. Both page counts (five and seven), all 199 finite traces, completed statuses and all 30 exact logical allocations were checked again successfully. See `output/DELIVERY_VERIFICATION.json`.

## Review 1 presentation package, 14 October 2026

Added a separate 15-slide editable PowerPoint (13 main plus two optional question slides), a matching static PDF, a four-page text-based submission, timed speaker notes and a source/contribution record. Only the frozen 24-run first-review cohort is presented. Review 2 is described as presentation coverage; completed experiments are not described as still unrun. The existing research reports and all 477 manifest inputs remain unchanged.

Four native charts, three native tables, 15 notes parts and four embedded chart workbooks passed first-party package, geometry, font and data-reference checks. Exported chart caches were independently compared against the frozen data. The final PPTX was reimported and all slides rendered. All 15 slides and four submission pages were visually inspected; the static slide PDF matches the final rendered pixels. Main notes contain 1,377 words with an 11:20 planned schedule; this is a timing estimate rather than a human rehearsal. Native PowerPoint application testing was unavailable.

The source screen downloaded the full three cited public PDFs and found no exact eight-word or twelve-word overlaps in submission body, visible slide body and spoken notes, after bibliography exclusions. Its scope and source hashes are recorded; no institutional similarity percentage or clearance is claimed. The official checker remains unspecified. The new submission's restart graph was redrawn from the archived CSV to use a cohort-specific title, preserving the old report's figure.

The presentation was subsequently revised for a beginner audience. Slide 3 explicitly defines grokking using practice-versus-new questions, and all slides/notes explain needed terms in plain language. Technical statistical details moved to optional notes; the main script has 1,498 words for the same 11:20 planned slot. All 15 revised slides were rendered and inspected. Native chart data and the matching PDF pixel check passed; the limited cited-source overlap screen remains clear. The four-page written submission and research reports were preserved. The presentation input manifest now covers 41 files, including the notes-only refresh helper.

## Final review and paper documentation, 15 October 2026

Added a separate completed-study presentation with 13 main slides, two optional appendix slides and an 11:35 planned schedule. It reports the 120 main runs and 30 fresh policy attempts, with plain explanations, four native editable charts, three tables, 15 speaker-note parts and four embedded chart workbooks. All 15 slides were rendered and visually inspected; the table spacing and the explicit 40%/60% dataset counts were corrected and reinspected. The matching static PDF was checked against the final PPTX render pixels. Package validation, chart portability and first-party reimport passed. Native Microsoft PowerPoint application testing was unavailable.

The complete verification command passed with 21 tests (25.05 seconds for the tests). An isolated reconstruction reproduced all 11 R numerical CSVs, all eight graph images with identical decoded RGB pixels, and the text of the seven-page final report. The raw-trace audit passed. All 477 original report-input hashes remain unchanged. Verification records are under `output/final_package/`.

Added a paper index, original abstract, full reference records, statistical-methods supplement, figure guide, data dictionary and reproducible presentation command. A limited exact eight-word/twelve-word screen of report body, visible slide text and notes against the three cited PDFs found no matches after bibliography exclusions. This is not an institutional similarity score. The final package does not claim a winning restart policy, worldwide novelty or sustained accuracy from first confirmation.

The local phrase screen was expanded to include the abstract and methods supplement; it again found no exact eight-word or twelve-word matches against those three PDFs. The private GitHub repository `Radical11/probandstatsproj` was created at the user's request. The final package manifest records sources and artifacts for working-file and committed-blob verification; the variable reproduction execution timestamp is excluded from its hash set.
