# Rebuilding the presentation packages

## Final review

The completed-study presentation reads the 120 main runs and separate 30 fresh-seed policy attempts. It contains 13 timed slides (11:35) and two optional question slides. The delivered editable deck is `output/final_package/final_presentation.pptx`; its matching static PDF is `output/pdf/final_presentation.pdf`.

With the Python environment installed and the bundled Codex presentation runtime available, run from the repository root:

```powershell
.\scripts\build_final_presentation.ps1
```

The script prepares actual evidence, authors a new candidate, validates native charts/tables and embedded workbooks, updates the stable deck, reimports and renders it, creates the matching PDF, screens prose against three cited papers, and verifies chart values and PDF pixels. Each candidate gets a unique name because the first-party finalizer does not overwrite a validated candidate. Previous candidates remain under ignored `tmp/final_presentation/` for recovery.

The runtime and skill locations can be supplied through `-RuntimeRoot` and `-PresentationSkill`; their defaults point to this version of the Codex bundled dependencies under the current user's profile. The script does not install another slide library. The phrase screen uses cached public PDFs or downloads the three cited sources if the cache is absent. It does not modify the first-review package. This presentation-authoring dependency is separate from the ordinary Python/base-R reproduction of the statistical report.

`presentation/final_verify.py` compares exported native chart values with raw traces and R outputs, checks 15 note parts, four charts, three tables and four embedded workbooks, and checks that all 15 static PDF pages match the imported final slide renders. Human visual inspection remains necessary after changes to text or layout. Native Microsoft PowerPoint application testing was unavailable; package validation and first-party import/rendering passed.

## Frozen Review 1 package

The package is separate from the preserved research reports. It reads `data/review1_summary.csv` and `output/review1/`, never the expanded main-study aggregate. Main sample 24; baseline sample 12; 13 main slides plus two optional slides.

The scripts use this workspace's Python environment (ReportLab/Pillow/pypdf), extracted base R and Codex's bundled Node/artifact-tool runtime. No network source code or alternate slide library is installed. Editable charts/tables are authored with artifact-tool and validated with the presentation skill's first-party finalizer. Displayed chart values are rounded to eight decimals for Excel portability; original traces are unchanged.

From the repository root, run:

```powershell
& '.\.tools\R\app\bin\Rscript.exe' presentation/figures.R
.\.venv\Scripts\python.exe presentation/prepare.py
New-Item -ItemType Directory -Force tmp/review1_presentation | Out-Null
# Create this junction only if it does not exist:
New-Item -ItemType Junction tmp/review1_presentation/node_modules -Target 'C:/Users/notak/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules'
Copy-Item presentation/build.mjs tmp/review1_presentation/build.mjs
# For a revision, choose a new filename; finalization does not overwrite a deck.
$env:DECK_FILENAME = 'review1_presentation_revision.pptx'
& 'C:/Users/notak/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' tmp/review1_presentation/build.mjs
Copy-Item presentation/render_final.mjs tmp/review1_presentation/render_final.mjs
& 'C:/Users/notak/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' tmp/review1_presentation/render_final.mjs $env:DECK_FILENAME
.\.venv\Scripts\python.exe presentation/export_slide_pdf.py
.\.venv\Scripts\python.exe presentation/check_originality.py
```

The direct bundled PDF exporter had an unresolved standard-font module. The matching slide PDF therefore contains the final rendered pages; use the PPTX for editing. The four-page written PDF retains selectable text.

`presentation/verify.py` checks the stable delivered deck's source numbers, chart caches, notes, manifests and pixel correspondence of the static PDF. It writes `verification.json`. For a revision, update its target filename or validate the revision separately rather than claiming it verifies the original deliverable. Render and inspect all changed slides and submission pages before delivery. The local originality script caches downloaded public source PDFs under ignored `tmp/`; its scope is narrower than an institutional checker.
