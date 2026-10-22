"""Independent raw-trace and fixed-design audit for paper v2."""
from pathlib import Path
from collections import Counter
import argparse, csv, hashlib, json, math, statistics
from .protocol import Detector
from .model import make_dataset
from .paper_study import ROOT, DATA, PLAN, build_plan, read_csv, sha
from .train import atomic_json

def audit(output=None, scientific_only=False):
    out=Path(output) if output else ROOT/'output/paper_v2';out.mkdir(parents=True,exist_ok=True)
    plan=read_csv(PLAN)
    assert plan==[{k:str(v) for k,v in row.items()} for row in build_plan()]
    original=read_csv(ROOT/'data/summary.csv');assert len(original)==199
    original_seeds={int(r['init_seed']) for r in original}
    fresh=[r for r in plan if r['reused']=='False']
    assert not original_seeds & {int(r['init_seed']) for r in fresh}
    assert len({r['init_seed'] for r in plan})==1350
    assert sum(int(r['max_updates']) for r in fresh)==7500000
    freeze=json.loads((DATA/'calibration_freeze.json').read_text())
    for name,digest in freeze['input_hashes'].items():assert sha(ROOT/name)==digest, ('Frozen input changed',name)
    assert sha(DATA/'frozen_predictions.csv')==freeze['predictions_sha256']
    partition_hashes={}
    for split in (20261013,20261014,20261015):
        x,y,tr,te=make_dataset(31,.6,split)
        assert len(x)==961 and len(tr)==576 and len(te)==385
        assert set(tr.tolist()).isdisjoint(te.tolist()) and len(set(tr.tolist())|set(te.tolist()))==961
        assert all(int(label)==(int(tokens[0])+int(tokens[1]))%31 for tokens,label in zip(x,y))
        partition_hashes[split]=hashlib.sha256(tr.numpy().tobytes()).hexdigest()
    summaries=read_csv(DATA/'run_summary.csv');assert len(summaries)==1350
    by_id={r['run_id']:r for r in summaries}; endpoints={};input_hashes={};error_history=0
    fixed=json.loads((ROOT/'configs/study.json').read_text())
    fixed_keys=('modulus','embedding_dim','heads','ff_dim','learning_rate','betas','eval_every',
                'checkpoint_every','train_threshold','test_threshold','consecutive','cpu_threads','precision')
    for row in plan:
        directory=ROOT/row['source_path'];s=json.loads((directory/'summary.json').read_text())
        c=json.loads((directory/'config.json').read_text());trace=read_csv(directory/'trace.csv')
        cap=int(row['max_updates'])
        assert s['status']=='completed' and s['completed_updates']==s['max_updates']==cap
        assert c['init_seed']==int(row['init_seed']) and c['split_seed']==int(row['split_seed'])
        assert s['init_seed']==int(row['init_seed']) and s['split_seed']==int(row['split_seed'])
        assert all(c[key]==fixed[key] for key in fixed_keys),('Fixed configuration changed',row['run_id'])
        assert s['train_size']==576 and s['test_size']==385
        assert c['train_fraction']==.6 and c['weight_decay']==1 and c['max_updates']==cap
        assert s['device']=='cpu' and s['torch_version']=='2.11.0+cu128' and c['cpu_threads']==4
        assert s['split_hash']==partition_hashes[int(row['split_seed'])]
        assert [int(p['step']) for p in trace]==list(range(0,cap+1,25))
        a,b=Detector(),Detector(consecutive=21)
        for p in trace:
            assert all(math.isfinite(float(p[k])) for k in ('train_loss','test_loss','train_acc','test_acc'))
            assert 0<=float(p['train_acc'])<=1 and 0<=float(p['test_acc'])<=1
            if int(p['step'])>0:
                a.observe(int(p['step']),float(p['train_acc']),float(p['test_acc']))
                b.observe(int(p['step']),float(p['train_acc']),float(p['test_acc']))
        t,u=a.generalization_time,b.generalization_time
        assert t==s['generalization_time']
        assert a.memorization_time==s['memorization_time'] and a.relapsed==s['relapsed']
        assert s['event_observed']==(t is not None)
        exported=by_id[row['run_id']]
        assert (int(exported['first_time']) if exported['first_time'] else None)==t
        assert (int(exported['stability_time']) if exported['stability_time'] else None)==u
        assert (exported['first_event']=='True')==(t is not None)
        assert (exported['stability_event']=='True')==(u is not None)
        if u is not None:assert t is not None and u-t>=450 and u<=cap
        endpoints[row['run_id']]=(t,u)
        for name in ('config.json','summary.json','trace.csv'):
            p=directory/name;input_hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        if (directory/'error.txt').exists():
            error_history+=1;p=directory/'error.txt';input_hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    attempts=read_csv(DATA/'attempt_summary.csv');assert len(attempts)==540
    cell_counts=Counter()
    for attempt in attempts:
        assert attempt['status']=='completed'
        budget=int(attempt['total_budget']);k=int(attempt['k'])
        ids=attempt['run_ids'].split(';');assert len(ids)==k
        rows=[by_id[i] for i in ids]
        assert all(int(r['max_updates'])==budget//k for r in rows)
        assert sum(int(r['completed_updates']) for r in rows)==budget==int(attempt['completed_updates'])==int(attempt['allocated_updates'])
        for ep,index in (('first',0),('stability',1)):
            assert (attempt[ep+'_success']=='True')==any(endpoints[i][index] is not None for i in ids)
        cell_counts[(attempt['split_seed'],budget,k)]+=1
    assert len(cell_counts)==18 and set(cell_counts.values())=={30}
    predictions=read_csv(DATA/'frozen_predictions.csv');assert len(predictions)==36
    for p in predictions:
        cal=[r for r in plan if r['cohort']=='calibration' and r['split_seed']==p['split_seed']]
        assert len(cal)==30;index=0 if p['endpoint']=='first' else 1
        per=int(p['per_run_budget']);f=sum(endpoints[r['run_id']][index] is not None and endpoints[r['run_id']][index]<=per for r in cal)/30
        assert math.isclose(float(p['predicted_success']),1-(1-f)**int(p['k']),abs_tol=1e-12)
    preserved=0
    omitted_course_sources=[]
    course_sources=set(json.loads((ROOT/'sources/source_hashes.json').read_text())['sha256'])
    for mode in ('review1','review2'):
        m=json.loads((ROOT/f'output/pdf/{mode}_manifest.json').read_text())
        for name,digest in m.items():
            name=name.replace('\\','/')
            if scientific_only and name.replace('\\','/').startswith('sources/') and name.lower().endswith('.pdf') and not (ROOT/name).exists():
                # An explicit allowlist: no experimental or source-code input may be skipped.
                assert Path(name).name in {Path(p).name for p in course_sources}, name
                omitted_course_sources.append(name)
                continue
            assert sha(ROOT/name)==digest, ('Original report input changed',name)
            preserved+=1
    if (out/'calibration_statistics.csv').exists():
        for stat in read_csv(out/'calibration_statistics.csv'):
            index=0 if stat['endpoint']=='first' else 1
            values=[endpoints[r['run_id']][index] for r in plan if r['cohort']=='calibration' and r['split_seed']==stat['split_seed']]
            capped=[v if v is not None else 30000 for v in values]
            assert int(stat['n'])==30 and int(stat['events'])==sum(v is not None for v in values)
            assert math.isclose(float(stat['mean_U']),statistics.mean(capped),rel_tol=1e-12)
        for stat in read_csv(out/'policy_statistics.csv'):
            sample=[a for a in attempts if a['split_seed']==stat['split_seed'] and int(a['total_budget'])==int(stat['total_budget']) and int(a['k'])==int(stat['k'])]
            success=sum(a[stat['endpoint']+'_success']=='True' for a in sample)
            assert len(sample)==int(stat['n'])==30 and success==int(stat['successes'])
            assert math.isclose(success/30,float(stat['observed_probability']),abs_tol=1e-12)
        tests=read_csv(out/'risk_differences.csv');primary=[r for r in tests if r['endpoint']=='first']
        assert len(primary)==12 and all(r['p_holm']!='NA' for r in primary)
    result=dict(status='passed',calibration=90,reused_calibration=20,new_calibration=70,validation_constituents=1260,
                validation_attempts=540,new_training_runs=1330,new_logical_updates=7500000,
                primary_and_stability_reconstructed=True,exact_budgets_verified=True,split_partitions_verified=True,
                source_freeze_verified=True,original_report_inputs_preserved=preserved,
                omitted_course_sources=sorted(set(omitted_course_sources)),
                runs_with_preserved_error_history=error_history,
                per_split_calibration_counts={str(s):30 for s in partition_hashes},input_hashes=input_hashes)
    atomic_json(out/'audit.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',default=None)
    p.add_argument('--scientific-only',action='store_true',help='Exclude only undistributed course PDFs from archival-document checks')
    args=p.parse_args();audit(args.output,scientific_only=args.scientific_only)
