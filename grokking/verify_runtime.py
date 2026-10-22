"""Verify CUDA availability and benchmark a short protocol-identical run."""
import json
import platform
import subprocess
import time
import torch
from .study import ROOT,load,run_config
from .train import train_run,atomic_json


def main():
    device='cuda' if torch.cuda.is_available() else 'cpu'
    details=dict(python=platform.python_version(),torch=torch.__version__,cuda_runtime=torch.version.cuda,
                 cuda_available=torch.cuda.is_available(),device=device)
    if device=='cuda':
        details.update(gpu=torch.cuda.get_device_name(0),compute_capability=torch.cuda.get_device_capability(0),
                       gpu_memory_bytes=torch.cuda.get_device_properties(0).total_memory)
        a=torch.randn(256,256,device='cuda');value=(a@a).sum().item()
        details['tensor_test_finite']=bool(torch.isfinite(torch.tensor(value)))
    else:
        try:torch.cuda.init()
        except RuntimeError as exc:details['cuda_initialization_error']=str(exc)
        details['note']='CPU used because CUDA is not accessible in the execution environment; this is not a diagnosis of the physical GPU.'
    config=run_config(load(),'benchmark',.6,1.,8000,500)
    config['device']=device
    summary=train_run(config,ROOT/f'tmp/benchmark_{device}')
    details.update(benchmark_updates=500,benchmark_elapsed_seconds=summary['elapsed_seconds'],
                   seconds_per_update_with_startup=summary['elapsed_seconds']/500)
    atomic_json(ROOT/'output/runtime.json',details)
    print(json.dumps(details,indent=2))


if __name__=='__main__':main()
