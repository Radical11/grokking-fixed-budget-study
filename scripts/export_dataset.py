"""Export actual generated pairs and the recorded deterministic data partitions."""
from pathlib import Path
import csv, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from grokking.model import make_dataset


def export():
    out=ROOT/'data/dataset';out.mkdir(parents=True,exist_ok=True)
    settings=((20261013,.4),(20261013,.6),(20261014,.6),(20261015,.6))
    partitions={}
    for seed,fraction in settings:
        x,y,tr,te=make_dataset(31,fraction,seed)
        assert len(x)==len(y)==961
        assert set(tr.tolist()).isdisjoint(te.tolist())
        assert len(tr)==int(961*fraction) and len(tr)+len(te)==961
        partitions[f's{seed}_f{int(fraction*100)}']=set(tr.tolist())
    with (out/'modular_addition_31.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['a','b','label',*partitions])
        for i,(tokens,label) in enumerate(zip(x,y)):
            a,b=int(tokens[0]),int(tokens[1]);assert int(label)==(a+b)%31
            writer.writerow([a,b,int(label),*['train' if i in tr else 'held_out' for tr in partitions.values()]])
    print('Exported 961 labelled pairs and four recorded partition settings.')


if __name__=='__main__':export()
