# Paper and reproducibility materials

The submission report is [the seven-page final report](../output/pdf/review2_report.pdf), with its editable text in [review2_report.md](../output/pdf/review2_report.md). It contains the question, methods, measured results, eight figures, limitations and references. The first-review report is an archived milestone and is not an additional independent dataset.

## Supporting documentation

- [Abstract](ABSTRACT.md): a concise description of the completed work.
- [References](references.bib): BibTeX records for the three research sources and supplied syllabus.
- [Methods supplement](../docs/PAPER_METHODS.md): endpoints, estimands, likelihood, censoring, statistical comparisons, assumptions and restart validation.
- [Figure guide](../docs/FIGURE_GUIDE.md): each graph's source data, denominator and interpretation.
- [Data dictionary](../docs/DATA_DICTIONARY.md): the fields and missing values in the saved data.
- [Protocol](../docs/PROTOCOL.md) and [syllabus map](../docs/SYLLABUS_MAP.md): experimental choices and course coverage.
- [Source/contribution record](../output/final_package/SOURCE_AND_CONTRIBUTION.md): established background, the proposed empirical contribution and similarity-screen limits.

## Reproduce the evidence

From the repository root in PowerShell, run:

```powershell
.\.venv\Scripts\python.exe scripts\verify_project.py --reproduce --run-tests
```

The command checks the preserved inputs, tests, raw-data audit, eleven R CSV outputs, all eight graph images and the final report text. It creates its reconstruction under ignored `tmp/final_reproduction/`; it does not retrain the network or replace the published report inputs. Its results are saved in `output/final_package/core_verification.json`.

## Claims supported by this paper

Learning time varies across initialization seeds and measured training conditions. At the tested 30,000-update validation budget, each policy succeeded in 10/10 attempts, leaving no clear winner with this sample and budget. The result is a valid inconclusive comparison. It does not establish equivalence or a universal optimum. First threshold confirmation is distinct from sustained generalization, unrestricted event times beyond the cap remain unknown, and runtime is not a controlled speed comparison.

No institutional paper template, official similarity checker or similarity limit has been supplied. The delivered report uses a plain paper-style layout. The editable source and full bibliography support a later formatting change if the college supplies a specific template.
