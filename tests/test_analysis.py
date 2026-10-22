"""Temporary synthetic fixtures test analysis correctness; never study evidence."""
import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import pytest

ROOT=Path(__file__).resolve().parents[1]
RSCRIPT=ROOT/'.tools/R/app/bin/Rscript.exe'
if not RSCRIPT.exists():
    found=shutil.which('Rscript');RSCRIPT=Path(found) if found else None
pytestmark=pytest.mark.skipif(RSCRIPT is None,reason='R runtime unavailable')


def fixture(tmp_path,full=False):
    (tmp_path/'data').mkdir()
    (tmp_path/'data/baseline.json').write_text(json.dumps(dict(train_fraction=.6,weight_decay=1.,max_updates=1000)))
    rows=[]
    for fraction in ([.4,.6] if full else [.6]):
        for wi,wd in enumerate([.3,1.,3.]):
            for j in range(20 if full else 6):
                # Both events and censored outcomes, with known U.
                event=j%(5 if full else 6)<(3 if full else 3)
                t=[100,250,500][j%3] if event else ''
                name=f'main_f{fraction}_w{wd}_s{j}'
                row=dict(run_id=name,stage='main',train_fraction=fraction,weight_decay=wd,
                         max_updates=1000,completed_updates=1000,memorization_time=75,
                         generalization_time=t,event_observed=event,delayed_generalization=event and t>=250,
                         elapsed_seconds=1+j/100,status='completed',error='',device='cpu')
                rows.append(row)
                p=tmp_path/'data/runs/main'/name;p.mkdir(parents=True)
                with (p/'trace.csv').open('w',newline='') as f:
                    w=csv.writer(f);w.writerow(['step','train_loss','test_loss','train_acc','test_acc'])
                    for step in [0,25,50,75,100,250,500,1000]:w.writerow([step,1.,1.,1. if step>=25 else .1,.98 if event and step>=t else .1])
    # Technical failures are counted separately rather than imputed at the cap.
    for status in ['failed','paused']:
        rows.append({**rows[0],'run_id':status,'status':status,'event_observed':False,'generalization_time':''})
    with (tmp_path/'data/summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    if full:
        with (tmp_path/'data/policies.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['k','attempt','total_budget','allocated_updates','completed_updates','success','elapsed_seconds'])
            w.writeheader()
            for k in [1,2,4]:
                for j in range(10):w.writerow(dict(k=k,attempt=j,total_budget=1000,allocated_updates=1000,
                    completed_updates=1000,success=j<3,elapsed_seconds=1))


def execute(tmp_path,mode):
    env={**os.environ,'LC_ALL':'C','LANG':'C'}
    result=subprocess.run([str(RSCRIPT),str(ROOT/'analysis/analyze.R'),mode],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    return tmp_path/'output'/mode


def rows(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))


def test_censoring_denominator_and_policy_formula(tmp_path):
    fixture(tmp_path);out=execute(tmp_path,'review1')
    baseline=next(r for r in rows(out/'group_statistics.csv') if float(r['weight_decay'])==1.)
    assert int(baseline['n'])==6 and int(baseline['censored'])==3
    assert float(baseline['success_probability'])==.5
    assert float(baseline['mean_capped_time'])==pytest.approx((100+250+500+3000)/6)
    pred=[r for r in rows(out/'policy_predictions.csv') if int(r['total_budget'])==1000]
    assert [float(r['predicted_success']) for r in pred]==pytest.approx([.5,.75,1-(1-2/6)**4])
    counts=rows(out/'audit_counts.csv')[0]
    assert int(counts['completed'])==18 and int(counts['failed'])==1 and int(counts['paused'])==1
    assert len(list(out.glob('*.png')))==5


def test_full_analysis_distribution_and_validation_paths(tmp_path):
    fixture(tmp_path,full=True);out=execute(tmp_path,'review2')
    assert len(rows(out/'analysis_rows.csv'))==120
    fits=rows(out/'distribution_fits.csv')
    assert {r['distribution'] for r in fits}=={'Exponential','Gamma','Weibull'}
    assert all(float(r['AIC'])>0 for r in fits)
    assert [int(r['attempts']) for r in rows(out/'policy_validation.csv')]==[10,10,10]
    assert (out/'policy_tests.txt').exists() and (out/'model_diagnostics.png').exists()
    terms=rows(out/'two_factor_tests.csv')
    assert len(terms)==3 and all(0<=float(r['permutation_p'])<=1 for r in terms)
    assert len(rows(out/'regression_coefficients.csv'))==3


def test_review1_snapshot_survives_main_study_expansion(tmp_path):
    fixture(tmp_path)
    shutil.copyfile(tmp_path/'data/summary.csv',tmp_path/'data/review1_summary.csv')
    r=rows(tmp_path/'data/summary.csv')
    r += [{**x,'run_id':x['run_id']+'_new'} for x in r if x['status']=='completed']
    with (tmp_path/'data/summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
    out=execute(tmp_path,'review1')
    assert len(rows(out/'analysis_rows.csv'))==18


def test_all_censored_is_not_fabricated_events(tmp_path):
    fixture(tmp_path)
    r=rows(tmp_path/'data/summary.csv')
    for x in r:x.update(event_observed=False,generalization_time='',delayed_generalization=False)
    with (tmp_path/'data/summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
    out=execute(tmp_path,'review1')
    assert all(int(x['successes'])==0 for x in rows(out/'group_statistics.csv'))
    assert all(float(x['variance_capped_time'])==0 and x['skewness_capped_time']=='NA' for x in rows(out/'group_statistics.csv'))
    assert all(float(x['predicted_success'])==0 for x in rows(out/'policy_predictions.csv'))
