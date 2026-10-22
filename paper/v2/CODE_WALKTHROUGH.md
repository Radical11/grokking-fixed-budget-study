# How the experiment works behind the scenes

The computer repeatedly trains a small prediction program, saves what happened, and then asks statistical questions about those recorded repetitions. The graphs are calculated from saved measurements; they are not drawn to illustrate an assumed outcome.

## 1. Make a task with known answers

`grokking/model.py::make_dataset` constructs all 961 ordered pairs of integers from 0 to 30. It calculates the correct answer with `(a + b) % 31`. For example, 30 + 4 gives remainder 3. This formula creates the labels; the prediction program is not given the formula or the answer as an input.

Each input contains the two numbers and a fixed query token. A split seed produces a repeatable shuffle. The first 576 pairs become practice data and the remaining 385 are held out. A separate random generator makes this partition independent of the initialization seed.

## 2. Start and train a prediction program

`SmallTransformer` maps the input into 31 scores, one for each possible answer. Its adjustable numbers are called weights. The initialization seed chooses their repeatable random starting values. Every new constituent run starts a separate model; a restart does not inherit another run's weights.

`grokking/train.py::train_run` calculates prediction error on the practice pairs. PyTorch calculates how changing the weights would change that error, and AdamW updates them. Weight decay shrinks weights during learning. One full-batch update uses all practice pairs once for this calculation. Held-out answers never contribute to the training loss or gradient updates. They are monitored to measure the endpoint; this study does not claim an additional untouched test set for every design decision.

Every 25 updates, the code measures practice and held-out accuracy. It records an initial measurement at zero, but that measurement cannot count toward a success streak. Training always executes the allocated number of updates, even after a success.

## 3. Save enough evidence to recover and audit a run

Each directory contains `config.json`, `trace.csv`, execution progress and a final `summary.json`. A completed training status means the allocated training steps finished; it does not mean that generalization occurred. Unknown confirmation times remain blank in the exported CSV.

Local checkpoints save the model, optimizer, random-generator state and recorded history every 500 updates. Resuming restores the same trajectory rather than inventing a new seed. Tests compare a resumed run with an uninterrupted run on the same device. Checkpoints and downloaded software are excluded from Git; configurations, traces and summaries are versioned. Technical errors are retained and distinguished from a completed run that does not learn within its cap.

## 4. Run the fixed follow-up in order

`grokking/paper_study.py` reads the committed configuration and complete seed manifest. It first finishes 30 calibration observations per split, including the explicitly reused 20 original observations. It reconstructs both endpoints from the traces: the third qualifying check for first confirmation, and the 21st for the 500-update window.

Before any fresh validation starts, it saves all predicted probabilities and hashes their calibration inputs. For a policy with k runs, it assigns exactly B/k updates to each constituent. One attempt succeeds if any constituent confirms before its own cap. The statistical unit is the complete budget attempt, not an individual constituent or an evaluation checkpoint.

The runner uses at most three processes, each with four CPU threads, and resumes completed or interrupted work without changing the manifest. The status command reads progress without starting training.

## 5. Turn measurements into statistical results

`analysis/paper_v2.R` reads the Python CSV interface. Base R calculates completion curves, exact binomial intervals, independent bootstrap resamples, the twelve planned Fisher comparisons with Holm adjustment, and the three candidate timing fits. It writes numerical CSV tables and both high-resolution PNG and vector PDF graphs. Original setting comparisons remain exploratory supporting evidence.

`grokking/paper_audit.py` independently reconstructs the endpoints and checks labels, partitions, seeds, frozen predictions, all 540 attempt budgets and the numerical exports. It also verifies preservation of the original scientific inputs.

## 6. Build the submission from those results

`grokking/paper_report.py` prepares the eight-page paper and four-page supplement from the numerical tables. `grokking/paper_typesetting.py` renders their editable Markdown sources into PDFs; it can also render prose edits directly without training. The presentation scripts build 13 main slides and two optional slides with native editable numerical charts, tables and timed notes. Their final-results gates require the complete, audited experiment.

`grokking/paper_verify.py --reproduce` independently reruns R in a separate directory and compares numerical tables, graph pixels, vector content and manuscript text. It checks the exported presentation's chart values and matching PDF. Every final page, slide and figure still receives visual inspection. The package manifest records file hashes, and a committed-byte check verifies that Git contains those exact scientific records.

## Commands to demonstrate

From the repository root in PowerShell:

```powershell
# Read progress; this does not collect data.
.\run_paper_v2.ps1 -Status

# Resume the fixed experiment and build its outputs.
.\run_paper_v2.ps1

# Recreate the analysis and documents from completed saved data.
.\run_paper_v2.ps1 -AnalysisOnly
```

The scientific Python/R path uses the project's documented environments. The editable presentation builder additionally uses the documented bundled artifact runtime. The official college similarity checker remains a separate submission step; the local source-overlap screen is limited to the cited research PDFs.
