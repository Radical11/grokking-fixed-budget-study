"""Isolated, resumable paper-v2 calibration and fixed-budget validation."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import argparse, csv, hashlib, json, os, subprocess, time
from .train import train_run, atomic_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'configs/paper_study.json'
DATA = ROOT / 'data/paper_v2'
PLAN = DATA / 'seed_manifest.csv'
FROZEN_FILES = ('configs/paper_study.json', 'configs/study.json', 'docs/PAPER_V2_PROTOCOL.md',
                'data/paper_v2/seed_manifest.csv', 'grokking/train.py', 'grokking/model.py', 'grokking/protocol.py', 'grokking/paper_study.py')
FIELDS = ['run_id','cohort','split_seed','replicate','init_seed','max_updates','total_budget','k','attempt','component','reused','source_path']

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(): return json.loads(CONFIG.read_text(encoding='utf-8'))
def read_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
def write_csv(path, rows, fields=None):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    with tmp.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),extrasaction='ignore');w.writeheader();w.writerows(rows)
    tmp.replace(path)

def build_plan():
    c=load(); rows=[]; counter=c['calibration_seed_start']
    for si,split in enumerate(c['split_seeds']):
        for rep in range(c['calibration_per_split']):
            reused=si==0 and rep<c['reuse_original_baseline']
            seed=11100+rep if reused else counter
            if not reused: counter+=1
            run_id=f'main_f0.6_w1_s{seed}' if reused else f'pv2_cal_s{split}_r{rep:02d}_i{seed}'
            source=f'data/runs/main/{run_id}' if reused else f'data/paper_v2/runs/calibration/{run_id}'
            rows.append(dict(run_id=run_id,cohort='calibration',split_seed=split,replicate=rep,init_seed=seed,
                             max_updates=c['calibration_cap'],total_budget='',k='',attempt='',component='',
                             reused=reused,source_path=source))
    counter=c['validation_seed_start']
    for split in c['split_seeds']:
        for budget in c['budgets']:
            for k in c['policies']:
                assert budget%k==0 and (budget//k)%25==0
                for attempt in range(c['attempts_per_cell']):
                    for j in range(k):
                        run_id=f'pv2_val_s{split}_b{budget}_k{k}_a{attempt:02d}_j{j}'
                        rows.append(dict(run_id=run_id,cohort='validation',split_seed=split,replicate='',init_seed=counter,
                                         max_updates=budget//k,total_budget=budget,k=k,attempt=attempt,component=j,reused=False,
                                         source_path=f'data/paper_v2/runs/validation/{run_id}'));counter+=1
    assert len(rows)==1350 and sum(not r['reused'] for r in rows)==1330
    assert len({r['init_seed'] for r in rows})==1350
    assert sum(r['max_updates'] for r in rows if not r['reused'])==7500000
    return rows

def prepare():
    rows=build_plan(); DATA.mkdir(parents=True,exist_ok=True)
    if PLAN.exists():
        assert read_csv(PLAN)==[{k:str(v) for k,v in r.items()} for r in rows], 'Committed seed manifest differs from fixed design'
    else: write_csv(PLAN,rows,FIELDS)
    original=json.loads((ROOT/'data/runtime_lock.json').read_text())
    assert original['device']=='cpu' and original['cpu_threads']==4
    lock=DATA/'runtime_lock.json'
    if lock.exists(): assert json.loads(lock.read_text())==original
    else: atomic_json(lock,original)
    for r in rows[:20]:
        s=json.loads((ROOT/r['source_path']/'summary.json').read_text())
        assert s['status']=='completed' and s['init_seed']==r['init_seed'] and s['split_seed']==r['split_seed']
    print(json.dumps({'planned_calibration':90,'reused':20,'new_calibration':70,'validation_constituents':1260,
                      'policy_attempts':540,'new_updates':7500000}),flush=True)
    return read_csv(PLAN)

def endpoints(trace):
    streak=0; first=None; stable=None
    for point in trace:
        step=int(point['step'])
        if step==0: continue
        streak=streak+1 if float(point['train_acc'])>=.99 and float(point['test_acc'])>=.95 else 0
        if first is None and streak>=3: first=step
        if stable is None and streak>=21: stable=step
    return first,stable

def config_for(row):
    base=json.loads((ROOT/'configs/study.json').read_text())
    for key in ('pilot_seeds','train_fractions','weight_decays','main_seed_start','validation_seed_start','baseline_target','cpu_batch_workers'):
        base.pop(key,None)
    base.update(stage=row['cohort'],run_id=row['run_id'],train_fraction=.6,weight_decay=1.,
                split_seed=int(row['split_seed']),init_seed=int(row['init_seed']),max_updates=int(row['max_updates']),device='cpu')
    return base

def verify_committed_protocol():
    for name in FROZEN_FILES:
        committed=subprocess.check_output(['git','show',f'HEAD:{name}'],cwd=ROOT)
        assert committed==(ROOT/name).read_bytes(), f'Commit the prospective protocol before training: {name}'
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def outcome(row, refresh=False):
    directory=ROOT/row['source_path']; summary=directory/'summary.json'
    if not summary.exists(): return {**row,'status':'pending'}
    s=json.loads(summary.read_text()); result={**row,**s}
    if s['status']!='completed': return result
    assert s['completed_updates']==int(row['max_updates'])
    cache=DATA/'outcomes'/f"{row['run_id']}.json"
    if cache.exists() and not refresh:
        cached=json.loads(cache.read_text())
        assert cached['completed_updates']==s['completed_updates']
        return cached
    trace=read_csv(directory/'trace.csv'); first,stable=endpoints(trace)
    assert first==s['generalization_time'], (row['run_id'],'Detector differs from raw trace')
    result.update(first_time=first,stability_time=stable,first_event=first is not None,stability_event=stable is not None,
                  trace_sha256=sha(directory/'trace.csv'))
    cache.parent.mkdir(exist_ok=True,parents=True);atomic_json(cache,result)
    return result

def aggregate(refresh=False):
    rows=[outcome(r,refresh) for r in read_csv(PLAN)]
    fields=FIELDS+['status','completed_updates','first_time','first_event','stability_time','stability_event',
                   'memorization_time','relapsed','elapsed_seconds','error','trace_sha256']
    write_csv(DATA/'run_summary.csv',rows,fields)
    attempts=[]; groups={}
    for r in rows:
        if r['cohort']=='validation': groups.setdefault((int(r['split_seed']),int(r['total_budget']),int(r['k']),int(r['attempt'])),[]).append(r)
    for (split,budget,k,attempt),g in sorted(groups.items()):
        complete=len(g)==k and all(r['status']=='completed' for r in g)
        done=sum(int(r.get('completed_updates',0)) for r in g)
        if complete: assert done==budget
        attempts.append(dict(split_seed=split,total_budget=budget,k=k,attempt=attempt,status='completed' if complete else ('failed' if any(r['status']=='failed' for r in g) else 'pending'),
                             allocated_updates=sum(int(r['max_updates']) for r in g),completed_updates=done,
                             first_success=any(r.get('first_event',False) for r in g) if complete else '',
                             stability_success=any(r.get('stability_event',False) for r in g) if complete else '',
                             elapsed_seconds=sum(float(r.get('elapsed_seconds',0)) for r in g),run_ids=';'.join(r['run_id'] for r in g)))
    write_csv(DATA/'attempt_summary.csv',attempts)
    counts={cohort:sum(r['cohort']==cohort and r['status']=='completed' for r in rows) for cohort in ('calibration','validation')}
    status=dict(updated_at_utc=datetime.now(timezone.utc).isoformat(),**counts,completed_attempts=sum(r['status']=='completed' for r in attempts),
                failed=sum(r['status']=='failed' for r in rows),planned_calibration=90,planned_validation=1260,planned_attempts=540)
    atomic_json(DATA/'status.json',status)
    return rows,attempts,status

def freeze():
    rows,_,_=aggregate();cal=[r for r in rows if r['cohort']=='calibration']
    assert len(cal)==90 and all(r['status']=='completed' for r in cal), 'Finish all calibration before freezing predictions'
    c=load(); predictions=[]
    for split in c['split_seeds']:
        g=[r for r in cal if int(r['split_seed'])==split]
        for budget in c['budgets']:
            for k in c['policies']:
                for endpoint in ('first','stability'):
                    successes=sum(r[endpoint+'_time'] is not None and r[endpoint+'_time']<=budget//k for r in g)
                    f=successes/len(g)
                    predictions.append(dict(split_seed=split,total_budget=budget,k=k,endpoint=endpoint,calibration_n=len(g),
                                            per_run_budget=budget//k,single_successes=successes,single_probability=f,predicted_success=1-(1-f)**k))
    hashes={r['source_path']+'/trace.csv':r['trace_sha256'] for r in cal}
    hashes.update({name:sha(ROOT/name) for name in FROZEN_FILES})
    record=DATA/'calibration_freeze.json'; csv_path=DATA/'frozen_predictions.csv'
    if record.exists():
        old=json.loads(record.read_text());assert old['input_hashes']==hashes,'Frozen calibration input changed'
        assert sha(csv_path)==old['predictions_sha256'],'Frozen predictions changed'
    else:
        assert not any((ROOT/r['source_path']/'summary.json').exists() for r in read_csv(PLAN) if r['cohort']=='validation'), 'Validation has already started without a prediction freeze'
        write_csv(csv_path,predictions)
        atomic_json(record,dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(),
                               source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                               predictions_sha256=sha(csv_path),input_hashes=hashes))
    return record

def run_phase(cohort, workers=None, max_new=None):
    plan=prepare(); commit=verify_committed_protocol()
    if cohort=='validation': freeze()
    candidates=[r for r in plan if r['cohort']==cohort and r['reused']=='False' and outcome(r)['status']!='completed']
    if max_new is not None: candidates=candidates[:max_new]
    workers=min(workers or load()['workers'],3)
    assert workers>=1
    print(f'PHASE {cohort}: {len(candidates)} pending; {workers} processes; source {commit}',flush=True)
    atomic_json(DATA/'active_phase.json',dict(phase=cohort,pid=os.getpid(),source_commit=commit,started_at_utc=datetime.now(timezone.utc).isoformat()))
    started=time.monotonic();completed=0;updated=0.;completed_updates=0
    pending={}; iterator=iter(candidates)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        def submit_next():
            row=next(iterator,None)
            if row is None:return False
            pending[pool.submit(train_run,config_for(row),ROOT/row['source_path'])]=row
            return True
        for _ in range(workers): submit_next()
        while pending:
            ready,_=wait(pending,timeout=15,return_when=FIRST_COMPLETED)
            for future in ready:
                row=pending.pop(future)
                try: s=future.result()
                except BaseException:
                    aggregate()
                    for p in pending:p.cancel()
                    raise
                result=outcome(row,refresh=True);completed+=1
                completed_updates+=int(row['max_updates'])
                print(f"DONE {row['run_id']} first={result['first_time']} stable={result['stability_time']} seconds={s['elapsed_seconds']:.1f} ({completed}/{len(candidates)})",flush=True)
                submit_next()
            if time.monotonic()-updated>=60 or not pending:
                _,_,status=aggregate();updated=time.monotonic()
                if completed:
                    throughput=completed_updates/(time.monotonic()-started)
                    status.update(phase=cohort,session_completed=completed,session_seconds=time.monotonic()-started,
                                  approximate_updates_per_wall_second=throughput)
                    atomic_json(DATA/'session_progress.json',status)
    aggregate()
    if cohort=='calibration' and max_new is None: freeze()

def status():
    _,_,s=aggregate();print(json.dumps(s,indent=2))
    for p in sorted((DATA/'runs').glob('*/*/progress.json')):
        sfile=p.with_name('summary.json')
        if not sfile.exists() or json.loads(sfile.read_text()).get('status')!='completed':
            print(p.parent.name,p.read_text())

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['prepare','calibrate','freeze','validate','export','status','all'])
    p.add_argument('--workers',type=int,default=None);p.add_argument('--max-new',type=int,default=None)
    args=p.parse_args()
    if args.stage=='prepare':prepare()
    elif args.stage=='calibrate':run_phase('calibration',args.workers,args.max_new)
    elif args.stage=='freeze':freeze()
    elif args.stage=='validate':run_phase('validation',args.workers,args.max_new)
    elif args.stage=='export':aggregate(refresh=True)
    elif args.stage=='status':status()
    else:
        run_phase('calibration',args.workers);freeze();run_phase('validation',args.workers)

if __name__=='__main__':main()
