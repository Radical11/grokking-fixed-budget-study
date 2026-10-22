"""Verify saved evidence and optionally reproduce R -> audit -> PDF in an isolated folder."""
from pathlib import Path
import argparse, csv, hashlib, json, math, os, shutil, subprocess, sys
from datetime import datetime, timezone
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
def compare_csv(left,right):
    a,b=read_csv(left),read_csv(right)
    assert len(a)==len(b),(left.name,'row count')
    for x,y in zip(a,b):
        assert x.keys()==y.keys(),(left.name,'columns')
        for key in x:
            if x[key]==y[key]: continue
            try: same=math.isclose(float(x[key]),float(y[key]),rel_tol=1e-12,abs_tol=1e-10)
            except ValueError: same=False
            assert same,(left.name,key,x[key],y[key])

def verify(reproduce=False,run_tests=False):
    output=ROOT/'output/final_package'; output.mkdir(parents=True,exist_ok=True)
    result={'status':'running','completion_review_date':'2026-10-15',
            'verified_at_utc':datetime.now(timezone.utc).isoformat()}
    if run_tests:
        p=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
        (ROOT/'tmp').mkdir(exist_ok=True)
        (ROOT/'tmp/final_tests.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        result['test_result']=p.stdout.strip().splitlines()[-1]
    count=0
    for mode in ('review1','review2'):
        manifest=json.loads((ROOT/f'output/pdf/{mode}_manifest.json').read_text())
        for name,expected in manifest.items():
            assert digest(ROOT/name)==expected,('Changed report input',mode,name)
        count+=len(manifest)
    result['preserved_report_input_hashes']=count
    rows=read_csv(ROOT/'data/summary.csv')
    assert len(rows)==199 and all(r['status']=='completed' for r in rows)
    main=[r for r in rows if r['stage']=='main']; val=[r for r in rows if r['stage']=='validation']
    assert len(main)==120 and len(val)==70
    cells={(r['train_fraction'],r['weight_decay']) for r in main}
    assert len(cells)==6 and all(sum((r['train_fraction'],r['weight_decay'])==cell for r in main)==20 for cell in cells)
    assert sum(r['event_observed']=='True' for r in main)==83
    assert all(bool(r['generalization_time'])==(r['event_observed']=='True') for r in main)
    for r in rows:
        path=ROOT/'data/runs'/r['stage']/r['run_id']/'trace.csv'
        for point in read_csv(path):
            assert all(math.isfinite(float(point[k])) for k in ('train_loss','test_loss','train_acc','test_acc')),path
            assert 0<=float(point['train_acc'])<=1 and 0<=float(point['test_acc'])<=1,path
    policies=read_csv(ROOT/'data/policies.csv')
    assert len(policies)==30 and all(int(p['completed_updates'])==int(p['allocated_updates'])==int(p['total_budget'])==30000 for p in policies)
    for k in (1,2,4): assert sum(int(p['k'])==k for p in policies)==10
    result.update({'completed_experimental_runs':199,'main_runs':120,'unfinished_main_outcomes':37,
                   'validation_constituents':70,'policy_attempts':30,'finite_traces':199})
    if reproduce:
        work=ROOT/'tmp/final_reproduction'; work.mkdir(parents=True,exist_ok=True)
        target=work/'data'
        if target.is_junction() or target.is_symlink():
            assert target.resolve()==(ROOT/'data').resolve(),'Unexpected data link'
        else:
            shutil.copytree(ROOT/'data',target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('checkpoint.pt','checkpoint.tmp'))
        files=['analysis/analyze.R','grokking/report.py','configs/study.json','docs/PROTOCOL.md','output/runtime.json']
        files += [str(p.relative_to(ROOT)) for p in (ROOT/'sources').glob('*.pdf')]
        for name in files:
            dest=work/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/name,dest)
        rscript=ROOT/'.tools/R/app/bin/Rscript.exe'
        if not rscript.exists():
            found=shutil.which('Rscript')
            if not found: raise RuntimeError('Install R or restore the local R runtime before reproducing analysis.')
            rscript=Path(found)
        p=subprocess.run([str(rscript),str(work/'analysis/analyze.R'),'review2'],cwd=work,
                         env={**os.environ,'LC_ALL':'C','LANG':'C'},capture_output=True,text=True)
        (work/'R_execution.log').write_text(p.stdout+p.stderr,encoding='utf-8')
        if p.returncode: raise RuntimeError(p.stdout+p.stderr)
        from grokking import audit, report
        old_audit_root,old_report_root=audit.ROOT,report.ROOT
        try:
            audit.ROOT=work; report.ROOT=work
            audit.audit('review2')
            report.build('review2')
        finally:
            audit.ROOT=old_audit_root; report.ROOT=old_report_root
        originals=sorted((ROOT/'output/review2').glob('*.csv'))
        assert len(originals)>=10
        for original in originals: compare_csv(original,work/'output/review2'/original.name)
        figures=sorted((ROOT/'output/review2').glob('*.png'))
        assert len(figures)==8, ('Expected final-study graphs',len(figures))
        for original in figures:
            expected_image=Image.open(original).convert('RGB')
            reproduced_image=Image.open(work/'output/review2'/original.name).convert('RGB')
            assert expected_image.size==reproduced_image.size and expected_image.tobytes()==reproduced_image.tobytes(), ('Reproduced graph differs',original.name)
        before=PdfReader(ROOT/'output/pdf/review2_report.pdf')
        after=PdfReader(work/'output/pdf/review2_report.pdf')
        assert len(before.pages)==len(after.pages)==7
        assert [p.extract_text() for p in before.pages]==[p.extract_text() for p in after.pages],'Reproduced report text differs'
        result.update({'reproduced_R_csv_files':len(originals),'reproduced_graphs_pixel_identical':len(figures),'raw_trace_audit':'passed',
                       'reproduced_report_pages':7,'reproduced_report_text_matches':True})
    result['status']='passed'
    (output/'core_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reproduce',action='store_true',help='Re-run R analysis, raw audit and report in tmp/final_reproduction.')
    parser.add_argument('--run-tests',action='store_true',help='Also run the automated test suite and retain its actual output.')
    args=parser.parse_args(); verify(args.reproduce,args.run_tests)
