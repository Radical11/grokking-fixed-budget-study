# Visual versions for Assessment 9 and Assessment 10

These are the revised submissions following the request for diagrams, graphs and short pointers. The previous delivery remains intact in `output/assessments/`.

- **Assessment 9:** `Assessment9_IEEE_Visual_Report.pdf` (six pages). Adds the recorded workflow as a vector diagram, uses concise objective pointers and a shorter abstract/method description, and retains the four scientific graphs, five result tables, equations and references.
- **Assessment 10 presentation:** `Assessment10_Visual.pptx` (ten slides, about 9 minutes 20 seconds of notes). Editable dataset-split diagram, workflow with checkpoint loop, common-scale success timelines, budget-allocation bars, four native numerical charts and an editable uncertainty plot.
- **Assessment 10 document:** `Assessment10_Visual_Explanation.pdf` (two pages). Diagram-led summary with the actual learning curve, all policy counts, uncertainty and the measured conclusion. Drawings and plots are vector content in the PDF.
- **Matching slide PDF:** `Assessment10_Visual.pdf` uses the exact reviewed, reimported slide pixels.
- **Editable IEEE source:** `Assessment9_Visual_LaTeX_Source.zip` includes the unchanged IEEE class, manuscript, figure PDFs and reference metadata.
- **Speaking script:** `speaker_notes.md`; fuller source citations are embedded in the PPTX notes.

Replace name, registration number and affiliation placeholders before submitting. Figures show recorded observations or clearly labelled experimental allocations; no illustrative results were invented. The findings and experimental design are unchanged.

## Visual conventions

The 8k/12k bar charts show **success counts out of 30 attempts**, rather than percentages. Every split/budget/policy cell is displayed. The final uncertainty plot shows **four-run probability minus one-run probability**, in percentage points, using the recorded conservative pointwise 95% bounds. Those bounds are separate from Holm-adjusted hypothesis-test decisions.

The two success timelines share the same relative time scale: adjacent checks are 25 updates apart. Three checks span 50 updates; 21 checks span 500. Both start at the first qualifying check, which cannot be update zero. All observation costs remain inside the constituent allocation. A 500-update window does not establish permanent generalization.

Workflow arrows follow Python data generation/training to saved records, R analysis and outputs. The checkpoint connection is bidirectional for saving and resuming. Dataset areas encode exactly 576/961 and 385/961 of the full pair set. Every budget-allocation row totals 8,000 updates.

## Reproduction

Run from the repository root with the existing Python environment:

```powershell
$env:PYTHONPATH=(Get-Location).Path
.venv/Scripts/python.exe scripts/assessments_visual/build_written.py
.tools/tectonic/tectonic.exe --outdir output/assessments_visual/assessment9_ieee --keep-logs output/assessments_visual/assessment9_ieee/main.tex
.venv/Scripts/python.exe scripts/assessments_visual/verify.py
```

The presentation author is `scripts/assessments_visual/presentation.mjs`, run against the live first-party presentation session. A standalone rebuild uses `finalize_presentation.mjs --rebuild` from a private build directory with the bundled artifact runtime available through `node_modules`. Set `ASSESSMENT_PPTX` to a new output path. The finalizer preserves existing output files and emits a separate validation receipt for each filename. Source numerical charts retain complete saved data, with eight decimal places used for portable Office chart workbooks.

`verify.py` checks the four numerical charts, all 18 policy cells, displayed brief-table counts, partition proportions, exact budget sums, 3/21 check counts, common timeline spacing, arrow directions and uncertainty-plot coordinates. It also checks that the four reused paper graphs are byte-identical to the study outputs and all 26 prior-assessment manifest files are unchanged. The slide PDF is checked against imported pixels. These checks complement the separate inspection of every page and slide; a native PowerPoint application-open test has not been performed.

Tectonic 0.17.0 compiles the IEEE source. The compiler and its package cache remain outside Git. Rebuilds may change PDF metadata. Refresh the visual review and file manifest after substantive edits.

## Academic attribution

The source-overlap record screens exact eight-word phrases against six cited public research PDFs and found no matches in this revision. It is a limited local screen, not an official college similarity score, semantic detector or proof of novelty. The paper credits grokking, timing research, restart theory and established model/optimizer methods. The contribution remains the recorded empirical comparison.
