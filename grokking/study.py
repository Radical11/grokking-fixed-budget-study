"""Run the preregistered pilot, Review 1 study, Review 2 and fresh-seed policies."""
import argparse
import csv
import json
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
import torch
from pathlib import Path
from .train import train_run, atomic_json, device_for
from .protocol import allocate_budget

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'configs/study.json'


def load():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def run_config(base, stage, fraction, wd, seed, cap):
    c = {k:v for k,v in base.items() if k not in ('pilot_seeds','train_fractions','weight_decays','main_seed_start','validation_seed_start','baseline_target','cpu_batch_workers')}
    c.update(stage=stage,train_fraction=fraction,weight_decay=wd,init_seed=seed,max_updates=cap,
             run_id=f'{stage}_f{fraction:g}_w{wd:g}_s{seed}')
    return c


def export():
    rows = [json.loads(p.read_text()) for p in sorted((ROOT/'data').glob('runs/*/*/summary.json'))]
    fields = ['run_id','stage','train_fraction','weight_decay','init_seed','split_seed','split_hash','train_size','test_size',
              'max_updates','completed_updates','memorization_time','generalization_time','event_observed','delayed_generalization',
              'relapsed','final_train_acc','final_test_acc','elapsed_seconds','status','error','device','torch_version','cuda_version']
    target = ROOT/'data/summary.csv'; target.parent.mkdir(exist_ok=True)
    with target.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    return rows


def execute(c, export_summary=True):
    print(f"START {c['run_id']} cap={c['max_updates']}",flush=True)
    try:
        s = train_run(c,ROOT/'data/runs'/c['stage']/c['run_id'])
        print(f"DONE {s['run_id']} T={s['generalization_time']} mem={s['memorization_time']} delayed={s['delayed_generalization']} seconds={s['elapsed_seconds']:.1f}",flush=True)
        return s
    finally:
        if export_summary:export()


def execute_batch(configs):
    base=load()
    lock_path=ROOT/'data/runtime_lock.json'
    if lock_path.exists():
        lock=json.loads(lock_path.read_text())
    else:
        lock=dict(device=device_for(base['device']),torch_version=torch.__version__,cpu_threads=base['cpu_threads'])
        lock_path.parent.mkdir(exist_ok=True);atomic_json(lock_path,lock)
    workers=1 if lock['device']=='cuda' else base.get('cpu_batch_workers',1)
    if workers==1:
        return [execute(c) for c in configs]
    results=[]
    print(f'BATCH {len(configs)} independent runs; {workers} CPU processes, {base["cpu_threads"]} threads per run',flush=True)
    # Separate processes protect global RNG states. Only the parent exports CSV.
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending={pool.submit(train_run,c,ROOT/'data/runs'/c['stage']/c['run_id']):c for c in configs}
        for future in as_completed(pending):
            c=pending[future]
            try:
                s=future.result();results.append(s)
                print(f'DONE {s["run_id"]} T={s["generalization_time"]} mem={s["memorization_time"]} delayed={s["delayed_generalization"]} seconds={s["elapsed_seconds"]:.1f}',flush=True)
            except BaseException:
                for f in pending:f.cancel()
                raise
            finally:
                export()
    return results


def pilot():
    base=load()
    selection_file=ROOT/'data/baseline.json'
    if selection_file.exists():
        return json.loads(selection_file.read_text())
    for cap in (30000,60000):
        candidates=[]
        for wd in base['weight_decays']:
            rows=execute_batch([run_config(base,'pilot',.6,wd,seed,cap) for seed in base['pilot_seeds']])
            delayed=[r['generalization_time'] for r in rows if r['delayed_generalization']]
            if len(delayed)>=2:
                med=statistics.median(delayed)
                candidates.append((abs(med-base['baseline_target']),wd,med))
        if candidates:
            _,wd,median=sorted(candidates)[0]
            chosen=dict(train_fraction=.6,weight_decay=wd,max_updates=cap,pilot_median=median,
                        reason='At least two delayed seeds; median closest to 7500; tie lower decay.',protocol_version=base['protocol_version'])
            atomic_json(selection_file,chosen)
            print('BASELINE '+json.dumps(chosen),flush=True)
            return chosen
    atomic_json(ROOT/'data/feasibility.json',dict(status='failed',reason='No setting produced delayed generalization in at least two pilot seeds at 60000 updates.'))
    raise RuntimeError('Pilot feasibility gate failed. Preserve evidence; do not expand automatically.')


def main_study(stage):
    base=load(); selected=pilot()
    configs=[]
    # Each cell has its own seed range; review-1 seeds are reused in review-2.
    for fi, fraction in enumerate(base['train_fractions']):
        if stage=='review1' and fraction!=.6:
            continue
        for wi, wd in enumerate(base['weight_decays']):
            n = 20 if stage=='review2' else (12 if wd==selected['weight_decay'] else 6)
            for j in range(n):
                seed=base['main_seed_start'] + fi*1000 + wi*100+j
                configs.append(run_config(base,'main',fraction,wd,seed,selected['max_updates']))
    execute_batch(configs)


def validation(export_summary=True):
    base=load(); selected=pilot(); cap=selected['max_updates']
    rows=[]
    target=ROOT/'data/policies.csv'
    for pi,k in enumerate((1,2,4)):
        for attempt in range(10):
            runs=[]
            for j,budget in enumerate(allocate_budget(cap,k)):
                seed=base['validation_seed_start']+pi*1000+attempt*10+j
                runs.append(execute(run_config(base,'validation',.6,selected['weight_decay'],seed,budget),export_summary=export_summary))
            rows.append(dict(k=k,attempt=attempt,total_budget=cap,allocated_updates=sum(r['max_updates'] for r in runs),
                             completed_updates=sum(r['completed_updates'] for r in runs),
                             success=any(r['event_observed'] for r in runs),elapsed_seconds=sum(r['elapsed_seconds'] for r in runs),
                             run_ids=';'.join(r['run_id'] for r in runs)))
            with target.open('w',newline='',encoding='utf-8') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['pilot','review1','review2','validation','export'])
    p.add_argument('--defer-export',action='store_true',help='Validation only: retain per-run files but defer aggregate CSV export until a later export command. Allows one aggregate writer during concurrent main collection.')
    args=p.parse_args()
    if args.defer_export and args.stage!='validation':p.error('--defer-export is only supported for validation')
    {'pilot':pilot,'review1':lambda:main_study('review1'),'review2':lambda:main_study('review2'),
     'validation':lambda:validation(export_summary=not args.defer_export),'export':export}[args.stage]()


if __name__=='__main__':
    main()
