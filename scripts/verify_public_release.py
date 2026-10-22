"""Verify a public snapshot and optionally reproduce saved R results without training."""
from pathlib import Path
import argparse, csv, hashlib, json, os, shutil, subprocess, sys
from PIL import Image
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(reproduce=False,rscript=None):
    manifest=json.loads((ROOT/'public_release_manifest.json').read_text(encoding='utf-8'))
    for name,digest in manifest['files'].items():
        assert sha(ROOT/name)==digest,('Release file changed',name)
    out=ROOT/'tmp/public_verification';out.mkdir(parents=True,exist_ok=True)
    from grokking.paper_audit import audit
    evidence=audit(output=out,scientific_only=True)
    from grokking.model import make_dataset
    with (ROOT/'data/dataset/modular_addition_31.csv').open(newline='',encoding='utf-8') as f:pairs=list(csv.DictReader(f))
    assert len(pairs)==len({(r['a'],r['b']) for r in pairs})==961
    for seed,fraction in ((20261013,.4),(20261013,.6),(20261014,.6),(20261015,.6)):
        x,y,tr,te=make_dataset(31,fraction,seed);training=set(tr.tolist());column=f's{seed}_f{int(fraction*100)}'
        for i,r in enumerate(pairs):
            assert (int(r['a']),int(r['b']),int(r['label']))==(int(x[i,0]),int(x[i,1]),int(y[i]))
            assert r[column]==('train' if i in training else 'held_out')
    result={'status':'passed','release_files_checked':len(manifest['files']),
            'dataset_pairs':961,'dataset_partitions_verified':4,
            'calibration':evidence['calibration'],'policy_attempts':evidence['validation_attempts'],
            'raw_endpoints_reconstructed':evidence['primary_and_stability_reconstructed'],
            'exact_budgets_verified':evidence['exact_budgets_verified'],
            'omitted_course_sources':evidence['omitted_course_sources'],
            'reproduction_run':False}
    if reproduce:
        exe=rscript or shutil.which('Rscript')
        if not exe:raise RuntimeError('Rscript not found; install R or pass --rscript')
        rep=out/'reproduced';rep.mkdir(exist_ok=True)
        subprocess.run([str(exe),str(ROOT/'analysis/paper_v2.R'),str(ROOT/'data/paper_v2'),str(rep)],
                       cwd=ROOT,env={**os.environ,'LC_ALL':'C','LANG':'C'},check=True)
        tables=list((ROOT/'output/paper_v2').glob('*.csv'));assert len(tables)==9
        for original in tables:assert original.read_bytes()==(rep/original.name).read_bytes(),original.name
        names=('learning_delay','timing_variation','completion_curves','policy_validation','risk_differences','stability_comparison','distribution_fits','legacy_settings')
        for name in names:
            a=Image.open(ROOT/f'output/paper_v2/{name}.png').convert('RGB');b=Image.open(rep/f'{name}.png').convert('RGB')
            assert a.size==b.size and a.tobytes()==b.tobytes(),name+' PNG'
            p=PdfReader(ROOT/f'output/paper_v2/{name}.pdf');q=PdfReader(rep/f'{name}.pdf')
            assert p.pages[0].get_contents().get_data()==q.pages[0].get_contents().get_data(),name+' PDF'
        result.update(reproduction_run=True,numerical_csvs_reproduced=9,png_figures_reproduced=8,vector_figures_reproduced=8)
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reproduce',action='store_true');p.add_argument('--rscript')
    a=p.parse_args();verify(a.reproduce,a.rscript)
