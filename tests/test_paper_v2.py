"""Follow-up-specific endpoint, manifest, phase and budget checks."""
import pytest
from grokking import paper_study as study

def points(n, bad=None):
    return [dict(step=i*25,train_acc=1.,test_acc=0. if i==bad else 1.) for i in range(n+1)]

def test_fixed_manifest_is_disjoint_and_exact():
    rows=study.build_plan()
    assert len(rows)==1350
    assert sum(r['reused'] for r in rows)==20
    assert sum(r['cohort']=='calibration' for r in rows)==90
    fresh=[r for r in rows if not r['reused']]
    assert len(fresh)==1330 and sum(r['max_updates'] for r in fresh)==7500000
    assert len({r['run_id'] for r in rows})==len({r['init_seed'] for r in rows})==1350
    for split in (20261013,20261014,20261015):
        for budget in (8000,12000):
            for k in (1,2,4):
                selected=[r for r in rows if r['cohort']=='validation' and r['split_seed']==split and r['total_budget']==budget and r['k']==k]
                assert len(selected)==30*k and sum(r['max_updates'] for r in selected)==30*budget
    assert [r['init_seed'] for r in fresh if r['cohort']=='calibration']==list(range(100000,100070))
    assert [r['init_seed'] for r in fresh if r['cohort']=='validation']==list(range(200000,201260))

def test_confirmation_windows_exclude_zero_and_do_not_backdate():
    assert study.endpoints(points(2))==(None,None)
    assert study.endpoints(points(3))==(75,None)
    assert study.endpoints(points(20))==(75,None)
    assert study.endpoints(points(21))==(75,525)

def test_stability_resets_without_rewriting_first_confirmation():
    assert study.endpoints(points(41,bad=21))==(75,None)
    assert study.endpoints(points(42,bad=21))==(75,1050)

def test_validation_cannot_freeze_partial_calibration(monkeypatch):
    monkeypatch.setattr(study,'aggregate',lambda:([],[],{}))
    with pytest.raises(AssertionError,match='Finish all calibration'):
        study.freeze()

def test_partial_failed_attempt_is_not_a_negative_outcome(tmp_path,monkeypatch):
    rows=[dict(run_id=f'v{j}',cohort='validation',split_seed='20261013',replicate='',init_seed=str(200000+j),
               max_updates='4000',total_budget='8000',k='2',attempt='0',component=str(j),reused='False',source_path='unused') for j in (0,1)]
    plan=tmp_path/'plan.csv';study.write_csv(plan,rows,study.FIELDS)
    monkeypatch.setattr(study,'PLAN',plan);monkeypatch.setattr(study,'DATA',tmp_path)
    def result(row,refresh):
        return {**row,'status':'completed' if row['run_id']=='v0' else 'failed',
                'completed_updates':4000 if row['run_id']=='v0' else 250,'first_event':True}
    monkeypatch.setattr(study,'outcome',result)
    _,attempts,status=study.aggregate()
    assert attempts[0]['status']=='failed' and attempts[0]['first_success']==''
    assert attempts[0]['completed_updates']==4250 and status['completed_attempts']==0

def test_attempt_rejects_inexact_completed_budget(tmp_path,monkeypatch):
    row=dict(run_id='v0',cohort='validation',split_seed='20261013',replicate='',init_seed='200000',
             max_updates='8000',total_budget='8000',k='1',attempt='0',component='0',reused='False',source_path='unused')
    plan=tmp_path/'plan.csv';study.write_csv(plan,[row],study.FIELDS)
    monkeypatch.setattr(study,'PLAN',plan);monkeypatch.setattr(study,'DATA',tmp_path)
    monkeypatch.setattr(study,'outcome',lambda row,refresh:{**row,'status':'completed','completed_updates':7975})
    with pytest.raises(AssertionError):study.aggregate()
