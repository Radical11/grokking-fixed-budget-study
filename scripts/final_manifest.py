"""Record or verify the final package's source/data/artifact hashes."""
from pathlib import Path
import argparse, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'output/final_package/package_manifest.json'

def digest(value):
    return hashlib.sha256(value).hexdigest()

def write_manifest():
    names = set()
    for path in ('output/pdf/review1_manifest.json', 'output/pdf/review2_manifest.json',
                 'output/review1_presentation/input_manifest.json'):
        manifest = json.loads((ROOT / path).read_text(encoding='utf-8'))
        names.add(path)
        for name, expected in manifest.items():
            assert digest((ROOT / name).read_bytes()) == expected, ('Preserved input changed', name)
            names.add(name.replace('\\', '/'))
    names.update(('.gitattributes', '.gitignore', 'README.md', 'PROJECT_GUIDE.md', 'presentation/README.md',
                  'requirements.txt', 'requirements.lock.txt', 'run_review1.ps1', 'run_review2.ps1',
                  'output/pdf/review1_report.pdf', 'output/pdf/review2_report.pdf',
                  'output/pdf/review2_report.md', 'output/pdf/final_presentation.pdf',
                  'output/review1_presentation/review1_presentation.pptx',
                  'output/pdf/review1_presentation.pdf', 'output/pdf/review1_submission.pdf'))
    for pattern in ('grokking/*.py', 'tests/*.py', 'configs/*.json', 'scripts/*.py', 'scripts/*.ps1',
                    'paper/*', 'presentation/final_*', 'docs/*.md', 'output/review2/*',
                    'output/final_package/*'):
        names.update(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pattern) if p.is_file())
    names.discard(MANIFEST.relative_to(ROOT).as_posix())
    # The reproduction command updates this execution log's timestamp/test duration.
    # Its underlying inputs and every delivered scientific artifact are hashed here.
    names.discard('output/final_package/core_verification.json')
    record = {'schema_version':1,
              'scope':'Final presentation/paper artifacts, code, saved analysis and preserved research inputs; excludes this manifest and the variable execution-log timestamp',
              'files':{name:digest((ROOT/name).read_bytes()) for name in sorted(names)}}
    MANIFEST.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
    return record

def verify_manifest(check_git=False):
    record = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for name, expected in record['files'].items():
        assert digest((ROOT/name).read_bytes()) == expected, ('Working file changed', name)
        if check_git:
            blob = subprocess.check_output(['git','show',f'HEAD:{name}'], cwd=ROOT)
            assert digest(blob) == expected, ('Committed bytes differ', name)
    print(json.dumps({'status':'passed', 'hashed_files':len(record['files']), 'committed_bytes_checked':check_git}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Create a new manifest after a reviewed package update.')
    parser.add_argument('--check-git', action='store_true', help='Also check every input/artifact against committed HEAD bytes.')
    args = parser.parse_args()
    if args.write:
        write_manifest()
    verify_manifest(args.check_git)
