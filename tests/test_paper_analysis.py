"""Statistical pipeline check with explicit temporary synthetic inputs, never research data."""
from pathlib import Path
import csv, os, shutil, subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]

def write(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def test_base_r_followup_counts_and_boundary_intervals(tmp_path):
    rscript=ROOT/'.tools/R/app/bin/Rscript.exe'
    if not rscript.exists():
        found=shutil.which('Rscript')
        if not found:pytest.skip('R is not installed')
        rscript=Path(found)
    inputs=tmp_path/'synthetic_inputs';outputs=tmp_path/'synthetic_outputs';inputs.mkdir()
    (inputs/'SYNTHETIC_TEST_ONLY.txt').write_text('Synthetic unit-test fixture; not experimental evidence.')
    rows=[];attempts=[];frozen=[]
    for split in (20261013,20261014,20261015):
        for rep in range(30):
            first=2000+100*rep if rep<29 else None
            stable=first+500 if rep<27 else None
            rows.append(dict(run_id=f'fixture_{split}_{rep}',status='completed',cohort='calibration',split_seed=split,
                             first_event=first is not None,first_time=first,stability_event=stable is not None,
                             stability_time=stable,source_path='SYNTHETIC_TEST_ONLY'))
        for B in (8000,12000):
            for k in (1,2,4):
                successes=({1:30,2:30,4:0} if B==8000 else {1:24,2:18,4:9})[k]
                for a in range(30):
                    attempts.append(dict(split_seed=split,total_budget=B,k=k,attempt=a,status='completed',allocated_updates=B,
                                         completed_updates=B,first_success=a<successes,stability_success=a<max(0,successes-3)))
                    for j in range(k):
                        rows.append(dict(run_id=f'fixture_v_{split}_{B}_{k}_{a}_{j}',status='completed',cohort='validation',split_seed=split,
                             first_event=False,first_time=None,stability_event=False,stability_time=None,source_path='SYNTHETIC_TEST_ONLY'))
                for endpoint in ('first','stability'):
                    times=[(2000+100*r if r<29 else None) if endpoint=='first' else (2500+100*r if r<27 else None) for r in range(30)]
                    p=sum(t is not None and t<=B//k for t in times)/30
                    frozen.append(dict(split_seed=split,total_budget=B,k=k,endpoint=endpoint,predicted_success=1-(1-p)**k))
    assert len(rows)==1350 and len(attempts)==540
    write(inputs/'run_summary.csv',rows);write(inputs/'attempt_summary.csv',attempts);write(inputs/'frozen_predictions.csv',frozen)
    result=subprocess.run([str(rscript),str(ROOT/'analysis/paper_v2.R'),str(inputs),str(outputs),'--no-figures'],cwd=ROOT,
                          env={**os.environ,'LC_ALL':'C','LANG':'C'},capture_output=True,text=True,timeout=180)
    assert result.returncode==0,result.stdout+result.stderr
    with (outputs/'risk_differences.csv').open(newline='') as f:comparisons=list(csv.DictReader(f))
    primary=[r for r in comparisons if r['endpoint']=='first']
    assert len(primary)==12 and all(r['p_holm']!='NA' for r in primary)
    boundary=next(r for r in primary if r['total_budget']=='8000' and r['k']=='2')
    assert float(boundary['ci_low'])==float(boundary['ci_high'])==0
    assert float(boundary['conservative_ci_low'])<0<float(boundary['conservative_ci_high'])
    assert float(boundary['p_value'])==1
    with (outputs/'policy_statistics.csv').open(newline='') as f:probabilities=list(csv.DictReader(f))
    assert len(probabilities)==36 and all(int(r['n'])==30 for r in probabilities)
    full=next(r for r in probabilities if r['total_budget']=='8000' and r['k']=='1' and r['endpoint']=='first')
    assert float(full['observed_probability'])==1 and float(full['ci_low'])<1
    assert len(list(outputs.glob('*.csv')))==9
