"""Limited local phrase-overlap screen; never an institutional similarity score."""
from pathlib import Path
import hashlib, html, json, re, urllib.request
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp/review1_presentation/source_corpus'
TMP.mkdir(parents=True, exist_ok=True)
OUT = ROOT/'output/review1_presentation'
content = json.loads((ROOT/'presentation/content.json').read_text(encoding='utf-8'))
sources = [
    (1, 'Power et al. (2022)', 'https://arxiv.org/pdf/2201.02177'),
    (2, 'Truong et al. (2026)', 'https://arxiv.org/pdf/2605.18845'),
    (3, 'Streeter et al. (2007)', 'https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf')
]
def tokens(text):
    text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
    return re.findall(r"[a-z0-9]+", text.lower())
def windows(items, n):
    return {tuple(items[i:i+n]) for i in range(max(0,len(items)-n+1))}

corpus = []
for idx,label,url in sources:
    target = TMP/f'source_{idx}.pdf'
    try:
        if not target.exists():
            req = urllib.request.Request(url, headers={'User-Agent':'BAMAT207 academic source verification'})
            with urllib.request.urlopen(req, timeout=40) as response:
                target.write_bytes(response.read())
        reader = PdfReader(target)
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        assert len(text)>500
        corpus.append({'id':idx,'label':label,'url':url,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pages':len(reader.pages),'tokens':tokens(text),'status':'read'})
    except Exception as exc:
        corpus.append({'id':idx,'label':label,'url':url,'status':'unavailable','error':str(exc)})
        print(f'Source {idx} unavailable: {exc}', flush=True)

submission = (OUT/'submission_text.md').read_text(encoding='utf-8').split('\n\nReferences\n\n')[0]
visible = '\n'.join(json.loads((OUT/'slide_text.json').read_text(encoding='utf-8')))
# Bibliographic titles, labels and URLs are deliberately reproduced with attribution.
for ref in content['references']:
    for term in (ref['title'],ref['label'],ref['url']):
        visible = visible.replace(term, '')
units = {'submission_body':submission, 'slide_body':visible,
         'spoken_notes':'\n'.join(s['notes'] for s in content['slides'])}
matches = []
for unit,text in units.items():
    words=tokens(text)
    for source in corpus:
        if source['status'] != 'read': continue
        shared=windows(words,8) & windows(source['tokens'],8)
        long=windows(words,12) & windows(source['tokens'],12)
        matches.append({'unit':unit,'source_id':source['id'],'eight_word_windows':len(shared),'twelve_word_windows':len(long),'examples':[' '.join(v) for v in sorted(shared)[:2]]})
report = {'screen':'Exact contiguous 8-word and 12-word windows after lowercase/alphanumeric normalization',
          'sources':[{k:v for k,v in s.items() if k!='tokens'} for s in corpus],
          'matches':matches,'official_similarity_score':None,
          'limitations':'Only the three cited PDFs were screened. No internet-wide, student-submission database, semantic paraphrase, source-code plagiarism or AI-authorship detector was used. Text extraction and normalization can miss overlaps. Bibliographic titles/URLs were excluded from slide-body comparison; the submission bibliography was excluded. Mathematical notation is not a prose originality claim.'}
(OUT/'originality_screen.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('sources','limitations')},indent=2))
