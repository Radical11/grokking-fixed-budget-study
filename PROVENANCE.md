# Public snapshot provenance

This repository is a public research snapshot released on 22 October 2026. It has its own Git history. It does not expose the private working repository's complete development history or claim that its first public commit was made before training.

Raw records, frozen predictions, configurations, statistical tables and submitted figures retain their source bytes. `public_release_manifest.json` records their hashes and the original snapshot commit identifier. It also records the small audit-code adaptation described below and Git attributes preserving three archival text files without line-ending normalization. Dates in the experimental records and protocol refer to that earlier study, not the date of public release.

Included: scientific source code, tests, raw recorded experiments, seed manifests, numerical outputs, figures, manuscripts, presentation sources and final assessment files. Historical reports and their original delivery manifests remain available as archives.

Excluded: local Python/R/tool installations, checkpoints, caches, temporary authoring files, personal working files, private checker/browser records, and the two supplied course-syllabus PDFs. The syllabus mapping and PDF hash metadata remain available. Course PDFs are reference documents, not experimental data.

The public version of `grokking.paper_audit` adds an explicit `--scientific-only` option that can skip only the absent syllabus PDFs during archival-document checks. All label, split, seed, endpoint, raw-trace, prediction-freeze and exact-budget checks remain active. Any other missing or changed archived input still fails. The public verifier uses this option and records the omitted document names.

Use `scripts/verify_public_release.py` and the public release manifest to verify this checkout. Historical private-delivery manifests describe older snapshots and should not be mistaken for a manifest of the public repository's changed documentation. Original Git-archive/tag-dependent packaging commands and locally bundled presentation authoring need their documented original environment; they are not the portable verification entry point.

Scientific conclusions remain conditional on one task, one network and three fixed dataset splits. A first threshold confirmation and a 500-update window do not establish permanent generalization. [Assistance and attribution](ACKNOWLEDGEMENTS.md) remain explicit.
