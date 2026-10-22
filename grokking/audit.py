"""Independent raw-trace and analysis-count audit for a completed review."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from .study import ROOT
from .model import make_dataset


def rows(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def first_confirmation(trace,train_threshold,test_threshold=None,consecutive=3):
    observations=[r for r in trace if int(r['step'])>0]
    for i in range(consecutive-1,len(observations)):
        window=observations[i-consecutive+1:i+1]
        if all(float(r['train_acc'])>=train_threshold and (test_threshold is None or float(r['test_acc'])>=test_threshold) for r in window):
            return int(observations[i]['step'])
    return None


def audit(mode='review1'):
    summaries=[]
    for path in sorted((ROOT/'data/runs').glob('*/*/summary.json')):
        s=json.loads(path.read_text())
        if s['status']!='completed':continue
        c=json.loads((path.parent/'config.json').read_text())
        trace=rows(path.parent/'trace.csv')
        assert [int(r['step']) for r in trace]==list(range(0,c['max_updates']+1,c['eval_every'])),s['run_id']
        mem=first_confirmation(trace,c['train_threshold'],consecutive=c['consecutive'])
        gen=first_confirmation(trace,c['train_threshold'],c['test_threshold'],c['consecutive'])
        assert mem==s['memorization_time'] and gen==s['generalization_time'],s['run_id']
        assert s['event_observed']==(gen is not None)
        relapse=bool(gen is not None and any(int(r['step'])>gen and float(r['test_acc'])<c['test_threshold'] for r in trace))
        assert relapse==s['relapsed'],s['run_id']
        delayed=bool(mem and gen and gen>=c['delayed_ratio']*mem and gen-mem>=c['delayed_min_gap'])
        assert delayed==s['delayed_generalization']
        _,_,tr,te=make_dataset(c['modulus'],c['train_fraction'],c['split_seed'])
        assert not set(tr.tolist())&set(te.tolist())
        assert hashlib.sha256(tr.numpy().tobytes()).hexdigest()==s['split_hash']
        assert len(tr)==s['train_size'] and len(te)==s['test_size']
        summaries.append(s)
    main=[s for s in summaries if s['stage']=='main']
    if mode=='review1' and (ROOT/'data/review1_summary.csv').exists():
        cohort={r['run_id'] for r in rows(ROOT/'data/review1_summary.csv') if r['stage']=='main'}
        main=[s for s in main if s['run_id'] in cohort]
    pilot=[s for s in summaries if s['stage']=='pilot']
    baseline=json.loads((ROOT/'data/baseline.json').read_text())
    expected=24 if mode=='review1' else 120
    assert len(main)==expected,(len(main),expected)
    assert len({s['init_seed'] for s in main})==len(main)
    assert not {s['init_seed'] for s in main}&{s['init_seed'] for s in pilot}
    assert len({s['device'] for s in main})==1
    assert len({s['torch_version'] for s in main})==1
    counts={}
    for s in main:counts[(s['train_fraction'],s['weight_decay'])]=counts.get((s['train_fraction'],s['weight_decay']),0)+1
    if mode=='review1':
        assert all(f==.6 and n==(12 if wd==baseline['weight_decay'] else 6) for (f,wd),n in counts.items())
    else:assert len(counts)==6 and all(n==20 for n in counts.values())
    out=ROOT/'output'/mode
    analyzed=rows(out/'analysis_rows.csv')
    assert {r['run_id'] for r in analyzed}=={s['run_id'] for s in main}
    for r in rows(out/'group_statistics.csv'):
        g=[s for s in main if s['train_fraction']==float(r['train_fraction']) and s['weight_decay']==float(r['weight_decay'])]
        assert len(g)==int(r['n'])
        assert sum(s['event_observed'] for s in g)==int(r['successes'])
        assert sum(not s['event_observed'] for s in g)==int(r['censored'])
        u=[s['generalization_time'] if s['event_observed'] else s['max_updates'] for s in g]
        assert abs(sum(u)/len(u)-float(r['mean_capped_time']))<1e-7
    calibration=[s for s in main if s['train_fraction']==.6 and s['weight_decay']==baseline['weight_decay']]
    for p in rows(out/'policy_predictions.csv'):
        cutoff=int(float(p['per_run_budget']));k=int(p['k'])
        probability=sum(s['event_observed'] and s['generalization_time']<=cutoff for s in calibration)/len(calibration)
        assert abs(1-(1-probability)**k-float(p['predicted_success']))<1e-12
        assert cutoff*k==int(p['total_budget'])
    if mode=='review2':
        validation=[s for s in summaries if s['stage']=='validation']
        assert len(validation)==70
        assert len({s['init_seed'] for s in validation})==70
        assert not {s['init_seed'] for s in validation}&{s['init_seed'] for s in main+pilot}
        pol=rows(ROOT/'data/policies.csv');assert len(pol)==30
        by_id={s['run_id']:s for s in validation}
        for k in (1,2,4):assert sum(int(p['k'])==k for p in pol)==10
        for p in pol:
            members=[by_id[name] for name in p['run_ids'].split(';')]
            assert len(members)==int(p['k'])
            assert sum(s['max_updates'] for s in members)==int(p['total_budget'])
            assert sum(s['completed_updates'] for s in members)==int(p['total_budget'])
            assert any(s['event_observed'] for s in members)==(p['success'].lower()=='true')
            assert all(s['train_fraction']==baseline['train_fraction'] and s['weight_decay']==baseline['weight_decay'] for s in members)
            assert len({s['max_updates'] for s in members})==1
        for r in rows(out/'policy_validation.csv'):
            attempts=[p for p in pol if int(p['k'])==int(r['k'])]
            assert len(attempts)==int(r['attempts'])
            assert sum(p['success'].lower()=='true' for p in attempts)==int(r['successes'])
    result=dict(status='passed',mode=mode,completed_main_runs=len(main),completed_pilot_runs=len(pilot),
                trace_outcomes_recomputed=True,disjoint_partitions_verified=True,R_counts_and_means_verified=True,
                policy_predictions_verified=True,device=main[0]['device'],cuda_training_executed=main[0]['device']=='cuda')
    (out/'audit.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['review1','review2'],nargs='?',default='review1');audit(p.parse_args().mode)
