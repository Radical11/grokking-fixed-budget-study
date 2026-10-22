import json
import torch
from grokking.model import make_dataset
from grokking.study import load, run_config
from grokking.train import train_run


def test_dataset_labels_partitions_and_independent_seed():
    x,y,tr,te=make_dataset(31,.6,42)
    assert len(x)==961 and len(tr)==576 and len(te)==385
    assert torch.equal(y,(x[:,0]+x[:,1])%31)
    assert not set(tr.tolist())&set(te.tolist())
    assert len(set(tr.tolist())|set(te.tolist()))==961
    torch.manual_seed(100)
    assert torch.equal(tr,make_dataset(31,.6,42)[2])


def test_resume_matches_uninterrupted(tmp_path):
    c=run_config(load(),'test',.6,1.,123,100)
    c['device']='cuda' if torch.cuda.is_available() else 'cpu'
    c['checkpoint_every']=50
    direct=train_run(c,tmp_path/'direct')
    paused=train_run(c,tmp_path/'resume',stop_after=50)
    assert paused['status']=='paused'
    resumed=train_run(c,tmp_path/'resume')
    assert resumed['status']=='completed'
    assert (tmp_path/'direct/trace.csv').read_bytes()==(tmp_path/'resume/trace.csv').read_bytes()
    state1=torch.load(tmp_path/'direct/checkpoint.pt',weights_only=False)
    state2=torch.load(tmp_path/'resume/checkpoint.pt',weights_only=False)
    assert all(torch.equal(v,state2['model'][k]) for k,v in state1['model'].items())
    assert direct['split_hash']==resumed['split_hash']


def test_collision_and_failure_retention(tmp_path):
    c=run_config(load(),'test',.6,1.,123,25)
    c['device']='not_a_device'
    import pytest
    with pytest.raises(RuntimeError):train_run(c,tmp_path/'failed')
    s=json.loads((tmp_path/'failed/summary.json').read_text())
    assert s['status']=='failed' and s['error']
    c['device']='cpu'
    with pytest.raises(ValueError,match='collision'):train_run(c,tmp_path/'failed')


def test_runtime_lock_blocks_version_change_even_for_new_runs(tmp_path):
    import pytest
    c=run_config(load(),'test',.6,1.,123,25)
    c['device']='cpu'
    (tmp_path/'runtime_lock.json').write_text(json.dumps(dict(device='cpu',torch_version='different-version',cpu_threads=4)))
    with pytest.raises(ValueError,match='original PyTorch version'):
        train_run(c,tmp_path/'runs/main/locked')


def test_cached_run_cannot_hide_smaller_budget(tmp_path):
    import pytest
    c=run_config(load(),'test',.6,1.,123,50);c['device']='cpu'
    train_run(c,tmp_path/'budget')
    c['max_updates']=25
    with pytest.raises(ValueError,match='Cannot shrink'):
        train_run(c,tmp_path/'budget')


def test_validation_deferred_export_has_only_one_aggregate_writer(monkeypatch):
    import grokking.study as study
    exported=[]
    monkeypatch.setattr(study,'train_run',lambda c,p:dict(run_id=c['run_id'],generalization_time=None,
        memorization_time=25,delayed_generalization=False,elapsed_seconds=1))
    monkeypatch.setattr(study,'export',lambda:exported.append(True))
    c=run_config(load(),'test',.6,1.,123,50)
    study.execute(c,export_summary=False)
    assert exported==[]
    study.execute(c)
    assert exported==[True]
