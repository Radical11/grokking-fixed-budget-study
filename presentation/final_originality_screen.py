"""Screen final prose against the three cited research PDFs; not a plagiarism score."""
from pathlib import Path
import hashlib, html, json, re, urllib.request
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / 'tmp/review1_presentation/source_corpus'
OUT = ROOT / 'output/final_package'
sources = [
    (1, 'Power et al. (2022)', 'https://arxiv.org/pdf/2201.02177'),
    (2, 'Truong et al. (2026) preprint', 'https://arxiv.org/pdf/2605.18845'),
    (3, 'Streeter, Golovin and Smith (2007)', 'https://www.cs.cmu.edu/~dgolovin/papers/aaai07b.pdf'),
]

def tokens(text):
    text = html.unescape(re.sub(r'<[^>]+>', ' ', text))
    return re.findall(r'[a-z0-9]+', text.lower())

def windows(words, n):
    return {tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1))}

content = json.loads((OUT / 'content.json').read_text(encoding='utf-8'))
corpus = []
for idx, label, url in sources:
    pdf = CORPUS / f'source_{idx}.pdf'
    if not pdf.exists():
        pdf = ROOT / 'tmp/final_presentation/source_corpus' / f'source_{idx}.pdf'
        if not pdf.exists():
            pdf.parent.mkdir(parents=True, exist_ok=True)
            request = urllib.request.Request(url, headers={'User-Agent':'BAMAT207 academic source verification'})
            with urllib.request.urlopen(request, timeout=40) as response:
                pdf.write_bytes(response.read())
    reader = PdfReader(pdf)
    source_text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    if len(source_text) < 500:
        raise ValueError(f'Could not extract source text from {pdf}')
    corpus.append({'id': idx, 'label': label, 'url': url,
                   'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
                   'pages': len(reader.pages), 'tokens': tokens(source_text), 'status': 'read'})

submission = re.split(r'\nReferences(?: and reproducibility)?\n', (ROOT / 'output/pdf/review2_report.md').read_text(encoding='utf-8'))[0]
slide_text = '\n'.join(json.loads((ROOT / 'tmp/final_presentation/slide_text.json').read_text(encoding='utf-8')))
spoken_notes = '\n'.join(s['notes'] for s in content['slides'])
for reference in content['references']:
    for term in (reference.get('title', ''), reference.get('label', ''), reference.get('url', '')):
        if term:
            slide_text = slide_text.replace(term, '')
units = {'final_report_body': submission, 'slide_body': slide_text, 'speaker_notes': spoken_notes,
         'paper_abstract': (ROOT / 'paper/ABSTRACT.md').read_text(encoding='utf-8'),
         'methods_supplement': (ROOT / 'docs/PAPER_METHODS.md').read_text(encoding='utf-8').split('\n## Attribution\n')[0]}
matches = []
for unit, text in units.items():
    words = tokens(text)
    for source in corpus:
        shared8 = windows(words, 8) & windows(source['tokens'], 8)
        shared12 = windows(words, 12) & windows(source['tokens'], 12)
        matches.append({'unit': unit, 'source_id': source['id'],
                        'eight_word_windows': len(shared8), 'twelve_word_windows': len(shared12),
                        'examples': [' '.join(x) for x in sorted(shared8)[:3]]})
report = {
    'screen': 'Exact contiguous 8-word and 12-word windows after lowercase alphanumeric normalization',
    'sources': [{k: v for k, v in item.items() if k != 'tokens'} for item in corpus],
    'matches': matches,
    'official_similarity_score': None,
    'limitations': 'Only the three cited PDFs were screened. No college checker, internet-wide corpus, student-submission database, semantic paraphrase detector, source-code comparison or AI-authorship detector was used. Text extraction and normalization can miss overlaps. Bibliographic title, author and URL strings are removed from slide-body comparison; the report bibliography is excluded. An exact phrase match is a review prompt, not proof of plagiarism; citations and standard technical language require context.'
}
(OUT / 'originality_screen.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'screened_units': list(units), 'sources_read': len(corpus),
                   'matches': [{k:v for k,v in row.items() if k != 'examples'} for row in matches],
                   'official_similarity_score': None}, indent=2))
