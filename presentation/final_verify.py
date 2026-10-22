"""Check final slide data, native chart objects and PDF correspondence."""
from pathlib import Path
import csv, hashlib, json, math, re, statistics, zipfile
from xml.etree import ElementTree as ET
from PIL import Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/final_package'
TMP = ROOT / 'tmp/final_presentation'
data = json.loads((OUT / 'evidence.json').read_text(encoding='utf-8'))
content = json.loads((OUT / 'content.json').read_text(encoding='utf-8'))

def csv_rows(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

raw = csv_rows(ROOT / 'data/summary.csv')
main = [r for r in raw if r['stage'] == 'main']
baseline = [r for r in main if float(r['train_fraction']) == .6 and float(r['weight_decay']) == 1]
assert len(raw) == 199 and len(main) == 120 and len(baseline) == 20
assert data['main'] == main
times = [int(r['generalization_time']) for r in baseline]
assert sorted(times) == sorted(data['baseline_times'])
assert statistics.mean(times) == 5481.25 and statistics.median(times) == 4025
assert sum(r['event_observed'] == 'True' for r in main) == 83
assert sum(data['histogram']['counts']) == 20
assert len(content['slides']) == 15 and sum(s['seconds'] for s in content['slides']) == 695
assert all(s['seconds'] > 0 for s in content['slides'][:13]) and all(s['seconds'] == 0 for s in content['slides'][13:])
trace = [{k: float(v) for k, v in row.items()} for row in csv_rows(ROOT / 'data/runs/main/main_f0.6_w1_s11113/trace.csv') if int(row['step']) <= 6500]
assert trace == data['trace']
predictions = [{k: float(v) for k, v in row.items()} for row in csv_rows(ROOT / 'output/review2/policy_predictions.csv')]
assert predictions == data['predictions']
group_values = []
for fraction in (.4, .6):
    group_values.append([statistics.mean(int(r['generalization_time']) if r['event_observed'] == 'True' else int(r['max_updates']) for r in main if float(r['train_fraction']) == fraction and float(r['weight_decay']) == decay) for decay in (.3, 1, 3)])
policy_series = []
for k in (1, 2, 4):
    points = [(0, 0)]
    for row in sorted((r for r in predictions if r['k'] == k), key=lambda r:r['total_budget']):
        x, y = row['total_budget'], row['predicted_success']
        if x == 0:
            continue
        if points[-1][0] < x:
            points.append((x, points[-1][1]))
        points.append((x, y))
    policy_series.append(([p[0] for p in points], [p[1] for p in points]))

expected = [
    [([r['step'] for r in trace], [r['train_acc'] for r in trace]),
     ([r['step'] for r in trace], [r['test_acc'] for r in trace])],
    [(None, values) for values in group_values],
    [(None, data['histogram']['counts'])],
    policy_series,
]
ns = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main', 'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}

def cache(node):
    return [float(p.find('c:v', ns).text) for p in sorted(node.findall('.//c:pt', ns), key=lambda p:int(p.attrib['idx']))]

def same(actual, expected_values, label):
    assert len(actual) == len(expected_values), (label, 'length')
    assert all(math.isclose(a, b, abs_tol=1e-8, rel_tol=0) for a, b in zip(actual, expected_values)), label

pptx = OUT / 'final_presentation.pptx'
with zipfile.ZipFile(pptx) as archive:
    names = archive.namelist()
    slides = sorted((n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=lambda n:int(re.search(r'slide(\d+)', n).group(1)))
    notes = [n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
    charts = sorted((n for n in names if re.fullmatch(r'ppt/slides/charts/chart\d+\.xml', n)), key=lambda n:int(re.search(r'chart(\d+)', n).group(1)))
    assert len(slides) == len(notes) == 15 and len(charts) == 4
    assert sum(len(ET.fromstring(archive.read(n)).findall('.//a:tbl', ns)) for n in slides) == 3
    assert sum(n.endswith('.xlsx') for n in names) == 4
    for name, expected_series in zip(charts, expected):
        actual_series = ET.fromstring(archive.read(name)).findall('.//c:ser', ns)
        assert len(actual_series) == len(expected_series)
        for series, (x, y) in zip(actual_series, expected_series):
            same(cache(series.find('c:val' if x is None else 'c:yVal', ns)), y, name)
            if x is not None:
                same(cache(series.find('c:xVal', ns)), x, name + ' x values')
    visible = ' '.join(node.text or '' for slide in slides for node in ET.fromstring(archive.read(slide)).findall('.//a:t', ns))
    assert '[Your name]' in visible and '[Your registration number]' in visible
    for name in notes:
        note = ' '.join(node.text or '' for node in ET.fromstring(archive.read(name)).findall('.//a:t', ns))
        assert 'Sources:' in note and ('Target:' in note or 'Optional appendix' in note)

pdf = PdfReader(ROOT / 'output/pdf/final_presentation.pdf')
assert len(pdf.pages) == 15
for i, page in enumerate(pdf.pages, 1):
    embedded = [obj.get_object() for obj in page['/Resources']['/XObject'].values() if obj.get_object()['/Subtype'] == '/Image']
    assert len(embedded) == 1
    pixels = Image.open(TMP / f'slide-{i:02d}.png').convert('RGB')
    assert (embedded[0]['/Width'], embedded[0]['/Height']) == pixels.size
    assert embedded[0].get_data() == pixels.tobytes(), f'Slide PDF mismatch: {i}'
assert len(PdfReader(ROOT / 'output/pdf/review2_report.pdf').pages) == 7
receipt = json.loads((TMP / 'latest_validation.json').read_text(encoding='utf-8'))
assert receipt['finalSha256'] == hashlib.sha256(pptx.read_bytes()).hexdigest()
assert receipt['firstPartyImport']['passed'] and receipt['nativeChartValidation']['passed']
screen = json.loads((OUT / 'originality_screen.json').read_text(encoding='utf-8'))
assert len(screen['sources']) == 3 and all(s['status'] == 'read' for s in screen['sources'])
assert all(row['eight_word_windows'] == row['twelve_word_windows'] == 0 for row in screen['matches'])
words = sum(len(re.findall(r'\b\w+\b', s['notes'])) for s in content['slides'][:13])
verification = {'status':'passed', 'main_runs':120, 'policy_attempts':30, 'slides':15,
                'main_slides':13, 'optional_slides':2, 'notes_parts':15, 'native_charts':4,
                'native_tables':3, 'embedded_chart_workbooks':4,
                'chart_values_verified_against_raw_and_R_data':True, 'chart_rounding_decimals':8,
                'presentation_pdf_pages':15, 'presentation_pdf_matches_final_render_pixels':True,
                'final_report_pages':7, 'planned_seconds':695, 'spoken_word_count':words,
                'planned_words_per_minute':round(words/(695/60),1),
                'timing_scope':'Written script length and planned pauses; not an actual human rehearsal',
                'native_powerpoint_application_open_tested':False,
                'visual_review':'All 15 slides inspected; corrected table and experiment labels reinspected',
                'official_similarity_score':None, 'presentation_sha256':hashlib.sha256(pptx.read_bytes()).hexdigest()}
(OUT / 'presentation_verification.json').write_text(json.dumps(verification, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps(verification, indent=2))
