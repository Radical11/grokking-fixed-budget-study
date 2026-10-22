# Reproduce the public research snapshot

Run commands from the repository root. Python 3.13 and R 4.6.1 were used in the recorded study. Training used PyTorch 2.11.0+cu128 on **CPU**, with four CPU threads per run and at most three training processes. No cross-device bitwise reproducibility is claimed.

## Set up Python and R

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install torch==2.11.0 --index-url https://download.pytorch.org/whl/cu128
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Install R separately and place `Rscript` on PATH, or pass its executable path using `--rscript`. The statistical scripts use base R without contributed packages. `requirements.lock.txt` records the original Python environment; the commands above do not promise identical dependency versions for every package. Data verification can use a compatible PyTorch installation; collecting additional training under the recorded runtime lock requires the exact recorded Torch build and device settings.

## Verify records and submission files

```powershell
.venv/Scripts/python.exe scripts/verify_public_release.py
```

This checks the release hashes, reconstructs both endpoints from all 1,350 follow-up observations (including 20 reused runs), verifies 540 attempt budgets, frozen predictions and preserved scientific inputs, and checks the main reported policy counts. It writes a new verification receipt under ignored `tmp/public_verification/`; it does not retrain or overwrite the delivered artifacts.

## Independently reproduce tables and graphs

```powershell
.venv/Scripts/python.exe scripts/verify_public_release.py --reproduce
# Or specify R explicitly:
.venv/Scripts/python.exe scripts/verify_public_release.py --reproduce --rscript 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe'
```

The verifier runs `analysis/paper_v2.R` against the saved data in a separate output folder. It compares nine numerical CSVs and eight PNG/vector-PDF figure pairs with the delivered results. Exact graph comparisons can depend on the R/graphics environment; the recorded environment is the reference. No statistical outcomes are replaced by synthetic test fixtures.

## Tests

```powershell
.venv/Scripts/python.exe -m pytest -q
```

Tests cover labels and partitions, seed separation, checkpoint resumption, failed/unfinished runs, confirmation windows, budget accounting, statistical boundaries and document rendering. R-specific tests skip when R is absent; inspect the summary rather than describing skipped tests as passed.

## Training implementation and report sources

- `grokking/model.py`: dataset and fixed transformer.
- `grokking/train.py`: optimizer updates, evaluation, saved traces and resumable checkpoints.
- `grokking/paper_study.py`: follow-up design, phases, calibration freeze and independent policy attempts.
- `analysis/paper_v2.R`: statistics and scientific plots.
- `grokking/paper_report.py`, `grokking/paper_typesetting.py`: complete paper and supplement generation.
- `output/assessments_visual/assessment9_ieee/main.tex`: editable IEEE report; compile with a TeX system supporting IEEEtran. Supporting figures/class are included.
- `scripts/assessments_visual/`: visual assessment authoring and validation. Presentation rebuilding uses the documented bundled authoring runtime; the editable PPTX can be opened directly without that runtime.

To inspect completed training progress, run `run_paper_v2.ps1 -Status`. The original end-to-end authoring runner is retained as source, but includes original-environment presentation/source-screen steps; use the portable verifier above for this public copy. Preserve the fixed design and use separate versioned data for any new experiment rather than editing the recorded study.
