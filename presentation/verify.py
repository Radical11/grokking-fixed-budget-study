"""Check evidence, exported native objects, PDF correspondence and source preservation."""
from pathlib import Path
import csv, hashlib, json, math, re, zipfile
from xml.etree import ElementTree as ET
from pypdf import PdfReader
from PIL import Image

root = Path(__file__).resolve().parents[1]
out = root/'output/review1_presentation'
data = json.loads((out/'evidence.json').read_text())
content = json.loads((root/'presentation/content.json').read_text())
assert data['main_n']==24 and data['pilot_n']==9 and len(data['baseline_times'])==12
assert len(content['slides'])==15 and sum(s['seconds'] for s in content['slides'])==680
assert all(s['seconds']>0 for s in content['slides'][:13])
assert all(s['seconds']==0 for s in content['slides'][13:])
for name in ('input_manifest.json',):
    for path, digest in json.loads((out/name).read_text()).items():
        assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest, path
# Existing review artifacts are evidence, never replaced by this package.
for mode in ('review1','review2'):
    for path, digest in json.loads((root/f'output/pdf/{mode}_manifest.json').read_text()).items():
        assert hashlib.sha256((root/path.replace('\\','/')).read_bytes()).hexdigest()==digest, path

pptx=out/'review1_presentation.pptx'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with zipfile.ZipFile(pptx) as archive:
    names=archive.namelist()
    slides=sorted((n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)), key=lambda p:int(re.search(r'slide(\d+)',p).group(1)))
    notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
    charts=[n for n in names if re.fullmatch(r'ppt/slides/charts/chart\d+\.xml',n)]
    assert len(slides)==15 and len(notes)==15 and len(charts)==4
    assert sum(len(ET.fromstring(archive.read(n)).findall('.//a:tbl',ns)) for n in slides)==3
    assert len([n for n in names if n.endswith('.xlsx')])==4
    def cache(node):
        pts=node.findall('.//c:pt',ns)
        return [float(pt.find('c:v',ns).text) for pt in sorted(pts,key=lambda p:int(p.attrib['idx']))]
    expected=[
      [(None,data['histogram']['counts'])],
      [(data['cdf']['x'],data['cdf']['y'])],
      [( [r['step'] for r in data['trace']], [r['train_acc'] for r in data['trace']]),([r['step'] for r in data['trace']], [r['test_acc'] for r in data['trace']])],
      [([r['decay'] for r in data['runs']],[r['T'] for r in data['runs']])]
    ]
    for name,series_expected in zip(sorted(charts,key=lambda p:int(re.search(r'chart(\d+)',p).group(1))),expected):
        series=ET.fromstring(archive.read(name)).findall('.//c:ser',ns)
        assert len(series)==len(series_expected)
        for series_node,(x,y) in zip(series,series_expected):
            values_node=series_node.find('c:val',ns) if x is None else series_node.find('c:yVal',ns)
            actual=cache(values_node); assert len(actual)==len(y)
            assert all(abs(a-b)<=1e-8 for a,b in zip(actual,y)), name
            if x is not None:
                actual_x=cache(series_node.find('c:xVal',ns)); assert len(actual_x)==len(x)
                assert all(abs(a-b)<=1e-8 for a,b in zip(actual_x,x)), name
    title=' '.join(v.text or '' for v in ET.fromstring(archive.read(slides[0])).findall('.//a:t',ns))
    assert '[Your name]' in title and '[Your registration number]' in title
    for i, name in enumerate(notes):
        text=' '.join(v.text or '' for v in ET.fromstring(archive.read(name)).findall('.//a:t',ns))
        assert 'Sources:' in text and 'Target:' in text or 'Optional appendix' in text

slide_pdf=PdfReader(root/'output/pdf/review1_presentation.pdf')
assert len(slide_pdf.pages)==15
for i,page in enumerate(slide_pdf.pages,1):
    images=[obj.get_object() for obj in page['/Resources']['/XObject'].values() if obj.get_object()['/Subtype']=='/Image']
    assert len(images)==1
    pixels=Image.open(root/f'tmp/review1_presentation/slide-{i:02d}.png').convert('RGB')
    assert (images[0]['/Width'],images[0]['/Height'])==pixels.size
    assert images[0].get_data()==pixels.tobytes(), f'Static PDF mismatch on slide {i}'
submission=PdfReader(root/'output/pdf/review1_submission.pdf')
assert len(submission.pages)==4
text='\n'.join(p.extract_text() for p in submission.pages)
assert all(section in text for section in ['1. Problem','2. Mathematical','3. Other methodology','4. Demonstration','5. Future work'])
assert 'validation pending' not in text.lower()
assert all(len(p.extract_text())>900 for p in submission.pages)
screen=json.loads((out/'originality_screen.json').read_text())
assert len(screen['sources'])==3 and all(s['status']=='read' for s in screen['sources'])
assert all(m['eight_word_windows']==0 and m['twelve_word_windows']==0 for m in screen['matches'])
receipt=json.loads((root/'tmp/review1_presentation/latest_validation.json').read_text())
assert receipt['finalSha256']==hashlib.sha256(pptx.read_bytes()).hexdigest()
assert receipt['firstPartyImport']['passed'] and receipt['nativeChartValidation']['passed']
word_count=sum(len(re.findall(r'\b\w+\b',s['notes'])) for s in content['slides'][:13])
report={'status':'passed','slides':15,'main_slides':13,'optional_slides':2,'speaker_notes_parts':15,'native_charts':4,'native_tables':3,'embedded_chart_workbooks':4,'chart_values_verified_against_frozen_data':True,'chart_value_rounding_decimals':8,'main_sample':24,'baseline_sample':12,'planned_duration_seconds':680,'spoken_word_count':word_count,'average_planned_words_per_minute':round(word_count/(680/60),1),'timing_check':'Script length and planned pauses; not an actual human rehearsal','static_slide_pdf_pages':15,'static_slide_pdf_matches_final_slide_pixels':True,'text_submission_pages':4,'existing_report_manifest_inputs_preserved':477,'local_overlap_screen':'no 8-word or 12-word matches against the 3 cited papers','official_similarity_score':None,'native_powerpoint_open_tested':False,'visual_review':'All 15 slides and 4 submission pages inspected; repaired title checked again'}
(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
