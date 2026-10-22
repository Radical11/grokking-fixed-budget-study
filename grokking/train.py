"""Training with atomic checkpoints, independent seeds and auditable traces."""
import csv
import copy
import hashlib
import json
import os
import random
import time
import traceback
from dataclasses import asdict
from pathlib import Path

# Must precede CUDA initialization for deterministic matrix multiplication.
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import torch
from torch.nn import functional as F
from .model import SmallTransformer, make_dataset
from .protocol import Detector


def configure(seed, cpu_threads=4):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(cpu_threads)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False


def device_for(request):
    if request == 'auto':
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    if request == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA requested but unavailable; no silent device change.')
    return request


def atomic_json(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')
    tmp.replace(path)


def signature(config):
    # Extending a pilot cap is allowed; changing model or protocol is not.
    return hashlib.sha256(json.dumps({k:v for k,v in config.items() if k != 'max_updates'},sort_keys=True).encode()).hexdigest()


def train_run(config, directory, resume=True, stop_after=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    config_file = directory/'config.json'
    if config_file.exists():
        previous=json.loads(config_file.read_text())
        if signature(previous) != signature(config):
            raise ValueError(f'Configuration collision at {directory}')
        if config['max_updates'] < previous['max_updates']:
            raise ValueError('Cannot shrink an existing run budget; use a distinct run ID.')
    old_summary = json.loads((directory/'summary.json').read_text()) if (directory/'summary.json').exists() else {}
    resolved_device = device_for(config['device'])
    # A study must not silently switch devices when run from a different terminal.
    lock_path = directory.parents[2]/'runtime_lock.json'
    if lock_path.exists():
        lock = json.loads(lock_path.read_text())
        if lock['torch_version'] != torch.__version__:
            raise ValueError('Study runtime is locked to its original PyTorch version.')
        if lock['cpu_threads'] != config.get('cpu_threads',4):
            raise ValueError('Study CPU thread count is locked for numerical consistency.')
        if config['device'] != 'auto' and resolved_device != lock['device']:
            raise ValueError('Requested device differs from the locked study device.')
        resolved_device = device_for(lock['device'])
    if resume and old_summary.get('status') == 'completed' and old_summary.get('completed_updates',0) >= config['max_updates']:
        if old_summary['device'] != resolved_device:
            raise ValueError('Cached run uses a different device; use a distinct run directory.')
        return old_summary
    atomic_json(config_file, config)
    started = time.perf_counter()
    trace = []
    elapsed_before = 0.
    completed = 0
    detector = Detector(config['train_threshold'],config['test_threshold'],config['consecutive'])
    try:
        configure(config['init_seed'],config.get('cpu_threads',4))
        device = resolved_device
        model = SmallTransformer(config['modulus'],config['embedding_dim'],config['heads'],config['ff_dim']).to(device)
        optimizer = torch.optim.AdamW(model.parameters(),lr=config['learning_rate'],betas=tuple(config['betas']),
                                     weight_decay=config['weight_decay'],foreach=False,capturable=(device=='cuda'))
        x,y,train_idx,test_idx = make_dataset(config['modulus'],config['train_fraction'],config['split_seed'])
        split_hash = hashlib.sha256(train_idx.numpy().tobytes()).hexdigest()
        x,y,train_idx,test_idx = [t.to(device) for t in (x,y,train_idx,test_idx)]
        ckpt_path = directory/'checkpoint.pt'
        if resume and ckpt_path.exists():
            state = torch.load(ckpt_path,map_location='cpu',weights_only=False)
            if state['signature'] != signature(config) or state['device'] != device:
                raise ValueError('Resume requires the same configuration and device.')
            if state.get('torch_version') != torch.__version__:
                raise ValueError('Resume requires the same PyTorch version.')
            model.load_state_dict(state['model'])
            optimizer.load_state_dict(state['optimizer'])
            completed = state['step']
            detector = Detector(**state['detector'])
            trace = state['trace']
            elapsed_before = state['elapsed_seconds']
            random.setstate(state['python_rng'])
            np.random.set_state(state['numpy_rng'])
            torch.set_rng_state(state['torch_rng'])
            if device == 'cuda':
                torch.cuda.set_rng_state_all(state['cuda_rng'])

        def elapsed():
            if device == 'cuda':
                torch.cuda.synchronize()
            return elapsed_before + time.perf_counter()-started

        def checkpoint():
            state = dict(signature=signature(config),device=device,torch_version=torch.__version__,step=completed,model=model.state_dict(),
                         optimizer=optimizer.state_dict(),detector=asdict(detector),trace=trace,
                         elapsed_seconds=elapsed(),python_rng=random.getstate(),numpy_rng=np.random.get_state(),
                         torch_rng=torch.get_rng_state(),cuda_rng=torch.cuda.get_rng_state_all() if device=='cuda' else None)
            torch.save(state,directory/'checkpoint.tmp')
            (directory/'checkpoint.tmp').replace(ckpt_path)
            with (directory/'trace.csv').open('w',newline='',encoding='utf-8') as f:
                w = csv.DictWriter(f,fieldnames=['step','train_loss','test_loss','train_acc','test_acc'])
                w.writeheader(); w.writerows(trace)
            atomic_json(directory/'progress.json',dict(step=completed,cap=config['max_updates'],
                memorization_time=detector.memorization_time,generalization_time=detector.generalization_time,
                elapsed_seconds=state['elapsed_seconds']))

        def evaluate(step):
            model.eval()
            with torch.no_grad():
                logits = model(x)
                tr_loss = F.cross_entropy(logits[train_idx],y[train_idx]).item()
                te_loss = F.cross_entropy(logits[test_idx],y[test_idx]).item()
                tr_acc = (logits[train_idx].argmax(-1)==y[train_idx]).float().mean().item()
                te_acc = (logits[test_idx].argmax(-1)==y[test_idx]).float().mean().item()
            if not np.isfinite([tr_loss,te_loss]).all():
                raise FloatingPointError('Nonfinite loss')
            trace.append(dict(step=step,train_loss=tr_loss,test_loss=te_loss,train_acc=tr_acc,test_acc=te_acc))
            if step > 0:  # Initial accuracy does not count as a training checkpoint.
                detector.observe(step,tr_acc,te_acc)

        if not trace:
            evaluate(0)
        graph = None
        if device=='cuda' and config.get('cuda_graphs',False):
            # Capture launch overhead only: no mixed precision or altered objective.
            # Warmup/capture updates are restored and do not count as training.
            before_model = {k:v.detach().clone() for k,v in model.state_dict().items()}
            before_opt = copy.deepcopy(optimizer.state_dict())
            train_x,train_y = x[train_idx],y[train_idx]
            def graph_step():
                optimizer.zero_grad(set_to_none=False)
                graph_loss = F.cross_entropy(model(train_x),train_y)
                graph_loss.backward()
                optimizer.step()
            side = torch.cuda.Stream()
            side.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(side):
                for _ in range(3):graph_step()
            torch.cuda.current_stream().wait_stream(side)
            torch.cuda.synchronize()
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):graph_step()
            model.load_state_dict(before_model)
            # Preserve tensor addresses referenced by the graph while restoring values.
            if before_opt['state']:
                for param_id,state_values in before_opt['state'].items():
                    parameter = list(model.parameters())[param_id]
                    for key,value in state_values.items():
                        optimizer.state[parameter][key].copy_(value)
            else:
                for state_values in optimizer.state.values():
                    for value in state_values.values():value.zero_()
            del before_model,before_opt
        limit = min(config['max_updates'],stop_after) if stop_after is not None else config['max_updates']
        for step in range(completed+1,limit+1):
            model.train()
            if graph is not None:
                graph.replay()
            else:
                optimizer.zero_grad(set_to_none=True)
                loss = F.cross_entropy(model(x[train_idx]),y[train_idx])
                loss.backward(); optimizer.step()
            completed = step
            if step % config['eval_every'] == 0:
                evaluate(step)
            if step % config['checkpoint_every'] == 0:
                checkpoint()
        # No off-grid observation is counted; budgets are multiples of eval_every.
        checkpoint()
        summary = dict(run_id=config['run_id'],stage=config['stage'],train_fraction=config['train_fraction'],
                       weight_decay=config['weight_decay'],init_seed=config['init_seed'],split_seed=config['split_seed'],
                       split_hash=split_hash,train_size=len(train_idx),test_size=len(test_idx),device=device,
                       torch_version=torch.__version__,cuda_version=torch.version.cuda,
                       max_updates=config['max_updates'],completed_updates=completed,
                       memorization_time=detector.memorization_time,generalization_time=detector.generalization_time,
                       event_observed=detector.generalization_time is not None,
                       delayed_generalization=detector.delayed(config['delayed_ratio'],config['delayed_min_gap']),
                       relapsed=detector.relapsed,final_train_acc=trace[-1]['train_acc'],final_test_acc=trace[-1]['test_acc'],
                       elapsed_seconds=elapsed(),status='completed' if completed==config['max_updates'] else 'paused',error='')
        atomic_json(directory/'summary.json',summary)
        return summary
    except Exception as exc:
        summary = dict(run_id=config['run_id'],stage=config['stage'],train_fraction=config['train_fraction'],
                       weight_decay=config['weight_decay'],init_seed=config['init_seed'],split_seed=config['split_seed'],
                       max_updates=config['max_updates'],completed_updates=completed,status='failed',error=str(exc),
                       event_observed=detector.generalization_time is not None,generalization_time=detector.generalization_time,
                       memorization_time=detector.memorization_time,elapsed_seconds=time.perf_counter()-started+elapsed_before)
        atomic_json(directory/'summary.json',summary)
        (directory/'error.txt').write_text(traceback.format_exc(),encoding='utf-8')
        raise
