"""Finalize/check the versioned package after actual artifact and visual verification."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from .paper_study import ROOT,DATA,sha

OUT=ROOT/'output/paper_v2'
MANIFEST=OUT/'package_manifest.json'
ARCHIVE='d8ffc56dfb0805ee90898220235c09c0f222dcce'

def finalize():
    proof=json.loads((OUT/'verification.json').read_text());visual=json.loads((OUT/'visual_review.json').read_text())
    assert proof['status']=='passed' and proof['reproduced_manuscript_text']
    assert visual['status']=='passed' and visual['paper_pages']==8 and visual['supplement_pages']==4 and visual['slides']==15
    assert visual['png_figures']==8 and visual['vector_figures']==8
    for name,digest in visual['checked_sha256'].items():assert sha(ROOT/name)==digest,('Changed after visual inspection',name)
    assert len(visual['checked_sha256'])==20
    for name in ('output/pdf/review1_report.pdf','output/pdf/review2_report.pdf'):
        archived=subprocess.check_output(['git','show',f'{ARCHIVE}:{name}'],cwd=ROOT)
        assert hashlib.sha256(archived).hexdigest()==sha(ROOT/name),('Archived report changed',name)
    (OUT/'START_HERE.md').write_text('''# Complete paper and final-review package

The completed follow-up includes an eight-page integrated paper, four-page supplement and editable 15-slide presentation (13 main + two optional slides; 11:40 planned speaker notes). Replace the editable student name and registration fields before submission.

- `paper.pdf` / `paper.md`: complete paper and editable text.
- `supplement.pdf` / `supplement.md`: methods, full validation counts and comparisons.
- `presentation.pptx` / `presentation.pdf`: editable native charts/tables and matching static PDF.
- `speaker_notes.md`: speaking script, timing and citations.
- Eight PNG/vector-PDF graph pairs and nine numerical CSVs: complete scientific outputs.
- `audit.json`, `verification.json`, `visual_review.json` and `package_manifest.json`: raw evidence, reproduction, visual review and byte integrity.
- `sources.json` / `originality_screen.json`: cited-source hashes and limited phrase-overlap screen; not an institutional score.

See `../../paper/v2/README.md`, `FIGURES.md`, `DATA_DICTIONARY.md`, `SOURCE_AND_CONTRIBUTION.md` and the committed follow-up protocol for the full documentation. Reproduce with `run_paper_v2.ps1 -AnalysisOnly` from the repository root. Read progress with `run_paper_v2.ps1 -Status`. The original delivery is archived at Git tag `review2-original` (d8ffc56).

Scientific completion does not require a winning policy. Results remain conditional on this task, architecture and three fixed splits; first confirmation and a finite 500-update window do not establish permanent generalization. Official similarity review depends on the college checker.
''',encoding='utf-8',newline='\n')
    names=set()
    audit=json.loads((OUT/'audit.json').read_text());names.update(audit['input_hashes'])
    freeze=json.loads((DATA/'calibration_freeze.json').read_text());names.update(freeze['input_hashes'])
    for mode in ('review1','review2'):
        name=f'output/pdf/{mode}_manifest.json';names.add(name);names.update(json.loads((ROOT/name).read_text()))
    for pattern in ('grokking/paper_*.py','analysis/paper_v2.R','configs/paper_study.json','docs/PAPER_V2*','tests/test_paper*.py',
                    'presentation/paper_v2*','paper/v2/*','scripts/build_paper_v2_presentation.ps1','output/paper_v2/*'):
        names.update(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pattern) if p.is_file())
    names.update(('.gitattributes','.gitignore','PAPER_V2.md','run_paper_v2.ps1','requirements.lock.txt',
                  'data/paper_v2/runtime_lock.json','data/paper_v2/calibration_freeze.json','data/paper_v2/frozen_predictions.csv',
                  'data/paper_v2/seed_manifest.csv','data/paper_v2/run_summary.csv','data/paper_v2/attempt_summary.csv'))
    names.discard(MANIFEST.relative_to(ROOT).as_posix());names.discard('output/paper_v2/committed_verification.json')
    # Older Windows manifests use backslashes; Git tree paths always use slashes.
    names={name.replace('\\','/') for name in names}
    record=dict(schema_version=1,archive_commit=ARCHIVE,scope='Actual scientific records, source, complete artifacts and verification; execution progress timestamps are excluded',
                files={name:sha(ROOT/name) for name in sorted(names)})
    MANIFEST.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    check()

def check(check_git=False):
    manifest=json.loads(MANIFEST.read_text())
    for name,digest in manifest['files'].items():assert sha(ROOT/name)==digest,('Working bytes differ',name)
    checked_commit=None
    if check_git:
        import io
        checked_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        names=list(manifest['files'])
        raw=subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=('\n'.join(checked_commit+':'+n for n in names)+'\n').encode())
        stream=io.BytesIO(raw)
        for name in names:
            header=stream.readline().decode().strip().split();assert len(header)==3,(name,header)
            data=stream.read(int(header[2]));assert stream.read(1)==b'\n'
            assert hashlib.sha256(data).hexdigest()==manifest['files'][name],('Committed bytes differ',name)
    result=dict(status='passed',hashed_files=len(manifest['files']),committed_bytes_checked=check_git,
                checked_commit=checked_commit,package_manifest_sha256=sha(MANIFEST),archive_commit=ARCHIVE)
    if check_git:(OUT/'committed_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--finalize',action='store_true');p.add_argument('--check-git',action='store_true')
    args=p.parse_args()
    if args.finalize:finalize()
    else:check(args.check_git)
