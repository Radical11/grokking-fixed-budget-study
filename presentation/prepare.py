"""Build presentation evidence and a four-page submission from frozen Review 1 inputs."""
from pathlib import Path
import csv, hashlib, json, math, statistics
from html import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/review1_presentation'
OUT.mkdir(parents=True, exist_ok=True)
PDF = ROOT / 'output/pdf'
CONTENT = json.loads((ROOT / 'presentation/content.json').read_text(encoding='utf-8'))

def rows(path):
    with (ROOT / path).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

frozen = rows('data/review1_summary.csv')
main = [r for r in frozen if r['stage'] == 'main' and r['status'] == 'completed']
assert len(main) == 24 and len(frozen) == 33
assert all(float(r['train_fraction']) == .6 for r in main)
groups = rows('output/review1/group_statistics.csv')
assert [int(g['n']) for g in groups] == [6, 12, 6]
baseline = [r for r in main if float(r['weight_decay']) == 1]
times = [int(r['generalization_time']) for r in baseline]
assert len(times) == 12 and statistics.mean(times) == 6475
assert math.isclose(statistics.stdev(times), float(groups[1]['sd_capped_time']))
assert sum(t <= 2400 for t in times) == 3
assert sum(r['relapsed'] == 'True' for r in main) == 18
representative = next(r for r in main if r['run_id'] == 'main_f0.6_w1_s11105')
trace = rows(f"data/runs/main/{representative['run_id']}/trace.csv")
trace = [{k: float(v) for k, v in r.items()} for r in trace if int(r['step']) <= 6000]
predictions = rows('output/review1/policy_predictions.csv')
predictions = [{k: float(v) for k, v in r.items()} for r in predictions]
full = [r for r in predictions if r['total_budget'] == 30000]
assert len(full) == 3
for r in predictions:
    k = int(r['k']); b = r['total_budget'] / k
    f = sum(t <= b for t in times) / len(times)
    assert math.isclose(r['predicted_success'], 1 - (1 - f) ** k, abs_tol=1e-12)

bins = list(range(0, 30001, 5000))
hist = [sum(bins[i] <= t < bins[i+1] for t in times) for i in range(6)]
assert sum(hist) == 12
events = sorted(set(times))
step_x, step_y = [0], [0]
for t in events:
    step_x.extend([t, t]); step_y.extend([step_y[-1], sum(v <= t for v in times) / 12])
step_x.append(30000); step_y.append(1)
evidence = {
    'scope': 'Frozen Review 1 cohort only', 'main_n': 24, 'pilot_n': 9,
    'groups': groups, 'baseline_times': times, 'histogram': {'counts': hist, 'labels': ['0-5k', '5-10k', '10-15k', '15-20k', '20-25k', '25-30k']},
    'trace': trace, 'representative': representative, 'cdf': {'x': step_x, 'y': step_y},
    'predictions': predictions, 'full_budget_predictions': full,
    'runs': [{'decay': float(r['weight_decay']), 'T': int(r['generalization_time'])} for r in main]
}
(OUT / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')

total = sum(s['seconds'] for s in CONTENT['slides'])
assert 600 <= total <= 720 and len(CONTENT['slides']) == 15
notes = ['# Review 1 speaker notes', '', f'Main presentation: {total//60}:{total%60:02d} planned, including graph pauses. Slides 14-15 are optional.', '', 'Replace the editable name and registration-number fields before presenting. Numbers below use only the frozen Review 1 cohort.', '']
elapsed = 0
for i, slide in enumerate(CONTENT['slides'], 1):
    duration = slide['seconds']
    notes += [f"## {i}. {slide['title']}", '', f"Time: {duration} seconds; start at {elapsed//60}:{elapsed%60:02d}." if duration else 'Optional question slide; outside the main timing.', '', slide['notes'], '', 'Sources: ' + '; '.join(f"[{ref['id']}] {ref['label']} - {ref['url']}" for ref in CONTENT['references'] if ref['id'] in slide['sources']), '']
    elapsed += duration
(OUT / 'speaker_notes.md').write_text('\n'.join(notes), encoding='utf-8')

for name, file in [('Arial', 'arial.ttf'), ('Arial-Bold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + file))
body = ParagraphStyle('body', fontName='Arial', fontSize=10.4, leading=15, textColor=colors.HexColor('#172B3A'), spaceAfter=8)
small = ParagraphStyle('small', parent=body, fontSize=8.6, leading=12)
heading = ParagraphStyle('heading', parent=body, fontName='Arial-Bold', fontSize=14, leading=19)
BLUE = colors.HexColor('#175F96')
c = canvas.Canvas(str(PDF / 'review1_submission.pdf'), pagesize=(595.28, 841.89))
c.setTitle('Grokking Under a Fixed Budget - Review 1 Submission')
c.setAuthor('BAMAT207 Lab Project')
plain = []
y = 0

def start(page, label):
    global y
    c.setFont('Arial-Bold', 10); c.setFillColor(BLUE)
    c.drawString(44, 803, 'BAMAT207  |  REVIEW 1  |  15 OCTOBER 2026')
    c.setFillColor(colors.HexColor('#172B3A')); c.setFont('Arial-Bold', 18)
    c.drawString(44, 772, label)
    c.setFont('Arial', 9); c.setFillColor(colors.HexColor('#667784'))
    c.drawString(44, 25, 'Frozen Review 1 evidence: 24 main runs; 9 pilot runs excluded from inference')
    c.drawRightString(551, 25, f'{page} / 4')
    y = 746

def para(text, style=body):
    global y
    p = Paragraph(text, style); _, h = p.wrap(507, 1000)
    if y - h < 48:
        raise ValueError(f'Page overflow: {text[:80]} at y={y}, h={h}')
    p.drawOn(c, 44, y-h); y -= h + style.spaceAfter
    plain.append(text)

def image(name, caption, width=500, height=220):
    global y
    if y-height < 65: raise ValueError('Image page overflow')
    directory = 'output/review1_presentation' if name == 'restart_predictions.png' else 'output/review1'
    c.drawImage(ImageReader(str(ROOT / directory / name)), 44, y-height, width=width, height=height, preserveAspectRatio=True, anchor='c')
    y -= height + 7; para(caption, small)

start(1, 'Grokking Under a Fixed Budget')
para('One Long Run or Several Restarts?', heading)
para('Name: ____________________ &nbsp;&nbsp; Registration number: ____________________', small)
para('1. Problem and clear objectives', heading)
para('A small neural network can fit its training examples before it performs reliably on unseen examples. Delayed improvement of this kind is called grokking [1]. Repeating a training experiment with different starting weights can produce different waiting times. The problem is therefore to measure that variability and ask how a limited training budget should be allocated.')
para('<b>Research question:</b> With the same total number of training updates, is one long run or several shorter runs from independent initializations more likely to reach a generalization threshold?')
para('<b>Objectives:</b> (i) measure time to generalization across repeated runs; (ii) compare capped learning times across weight-decay settings; (iii) estimate success probability by a budget; and (iv) use these estimates to predict fixed-budget restart outcomes.')
para('Timing prediction already has related research [2], and restart schedules have established foundations [3]. The proposed contribution is a controlled empirical comparison in this small task. Neither grokking nor the restart probability identity is claimed as a new discovery.')
para('2. Mathematical and statistical methods', heading)
para('<b>Endpoint:</b> T is the update at the third consecutive evaluation where training accuracy is at least 99% and unseen accuracy is at least 95%. Evaluations occur every 25 updates. Qualifying evaluations at 2,000, 2,025 and 2,050 therefore give T = 2,050. Memorization time is recorded separately from the training threshold.')
para('<b>Observation window:</b> C = 30,000 updates. A run unfinished by C keeps an unknown T. Define U = min(T,C) for fully observed capped-time comparisons. Assigning U = C to an unfinished run does not imply it completed at C. A first confirmed event is also distinct from permanently high accuracy.')
c.showPage()

start(2, 'Statistical methods and implementation')
para('2. Mathematical and statistical methods (continued)', heading)
para('<b>Descriptive statistics:</b> For n runs, the sample mean is sum(U<sub>i</sub>)/n and sample variance is sum((U<sub>i</sub> - mean U)<super>2</super>)/(n-1). The median and standard deviation help describe typical waiting time and spread. Histograms reveal skewness that an average alone can hide.')
para('<b>Probability:</b> Estimate F(t) = P(T ≤ t) by the fraction of all observed runs with a confirmed event by t. A success indicator is Bernoulli; independent equal-probability indicators give a binomial success count. Exact binomial confidence intervals quantify probability uncertainty. A 1,000-resample percentile bootstrap estimates uncertainty in mean U.')
para('<b>Comparisons:</b> Welch tests compare pairs of group means, with Holm adjustment for multiple comparisons. One-way ANOVA tests H<sub>0</sub>: the three population mean capped times are equal. Pearson/Spearman correlations describe associations; simple regression uses U = β<sub>0</sub> + β<sub>1</sub> log(weight decay) + error. Small samples and non-normal residuals require caution. Permutation sensitivity checks still require exchangeable errors.')
para('<b>Restarts:</b> Give each of k independent runs B/k updates. If a single run succeeds with probability F(B/k), all fail with probability [1 - F(B/k)]<super>k</super>. Hence P(at least one success) = 1 - [1 - F(B/k)]<super>k</super>. This uses elementary independent-event probability; it is not a new theorem. Predictions estimated from the same cohort are correlated.')
para('The supplied syllabus [4] supports random variables and moments (Module 1), Bernoulli/binomial outcomes (Module 2), inference (Module 3), correlation/regression (Module 4) and ANOVA (Module 5). Review 2 will cover candidate time distributions and expanded factorial analysis. Unsuitable syllabus tests are not forced onto this dataset.')
para('3. Other methodology used', heading)
para('Python generates y = (a+b) mod 31 for all 961 ordered pairs, for example (30+4) mod 31 = 3. In this review, 576 pairs train the model and 385 disjoint pairs evaluate it. The split seed stays fixed; independent initialization seeds control starting weights. One full-batch update adjusts weights using the whole training subset.')
para('A fixed small transformer uses embedding width 64, four attention heads and a 128-unit feed-forward layer. AdamW uses learning rate 0.003. Weight decay, which shrinks weights during optimization, takes values 0.3, 1 and 3. Nine separate pilot runs select decay 1 by the predefined rule; main group sizes are 6, 12 and 6. Python preserves traces, configuration, statuses and resumable checkpoints. Base R reads CSVs and performs analysis. CUDA was unavailable; this cohort used CPU.')
c.showPage()

start(3, 'Initial results from the frozen cohort')
para('4. Demonstration of initial results', heading)
image('learning_curve.png', 'Figure 1. Training and unseen accuracy for a representative baseline run near its median event time. The early window shows a delay; the complete trace extends to 30,000 updates.', height=213)
values = [['Weight decay', 'Runs / events', 'Mean U', 'SD U'], ['0.3', '6 / 6', '13,137.5', '4,593.4'], ['1', '12 / 12', '6,475.0', '7,041.4'], ['3', '6 / 6', '1,887.5', '889.8']]
t = Table(values, colWidths=[110, 130, 130, 130], rowHeights=25)
t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Arial'),('FONTNAME',(0,0),(-1,0),'Arial-Bold'),('FONTSIZE',(0,0),(-1,-1),10),('TEXTCOLOR',(0,0),(-1,0),BLUE),('LINEBELOW',(0,0),(-1,0),.8,BLUE),('LINEBELOW',(0,-1),(-1,-1),.5,colors.lightgrey),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
t.wrap(507, 1000)
t.drawOn(c, 44, y-100); y -= 112
para('Table 1. Capped times in optimizer updates; all groups use 60% training data. All 24 runs reached the threshold within the cap. Pilot runs are not included.', small)
para('The baseline median is 4,275 updates, with observed range 1,875-27,175. Its mean exceeds its median, and its SD exceeds its mean, indicating substantial spread. The bootstrap 95% interval for mean U is approximately 3,579-10,615 updates. Baseline success by C is 12/12, with exact 95% interval 73.5%-100%; the sample does not establish certainty of population success.')
para('The preliminary one-way ANOVA gives p = 0.0077 and permutation sensitivity p = 0.0130. Residual normality fails (Shapiro-Wilk p ≈ 0.000068), so the comparison remains exploratory. Larger weight decay is associated with shorter capped time in this cohort, not established as universally optimal. Pearson r for log(decay) and U is -0.606; Spearman ρ is -0.741.')
para('Eighteen of 24 main runs later dipped below 95% unseen accuracy. The endpoint measures first confirmation, not stable generalization. All results are conditional on one fixed data split.')
c.showPage()

start(4, 'Restart predictions and future work')
para('4. Initial results (continued)', heading)
image('restart_predictions.png', 'Figure 2. Restart success predicted from the 12 baseline runs. These predictions are unvalidated in the Review 1 cohort.', height=180)
para('At total B = 30,000, predicted success is 100.0% for k=1, 99.3% for k=2 and 99.6% for k=4. The allocations are respectively 30,000, 15,000 and 7,500 updates per run. At B = 2,400, the predictions are 25%, 0% and 0%. A zero empirical estimate does not establish zero population probability. The generous full cap may conceal differences near the learning transition.')
para('5. Future work and Review 2 coverage', heading)
para('The frozen Review 1 milestone covers the training/logging pipeline, resumption, repeated-run export, policy runner, preliminary R analysis and first report: approximately 65% of the weighted implementation checklist, not 65% of scientific certainty. Review 2 will cover the expanded six-cell study, candidate Exponential/Gamma/Weibull models, multiple regression, two-factor ANOVA and fresh-seed policy comparison.')
para('Further research includes validating budgets near the learning transition, repeating the study with different data-split seeds, and measuring sustained rather than first-confirmed generalization. Runtime should be reported separately from logical update budgets. An institutional similarity score remains pending because no checker or acceptance threshold has been specified.')
para('References', heading)
for ref in CONTENT['references'][:3]:
    para(f"[{ref['id']}] {escape(ref['label'])}. {escape(ref['title'])}. <link href='{ref['url']}' color='#175F96'>{escape(ref['url'])}</link>", small)
para('[4] BAMAT207 official theory and embedded-lab syllabus, version 1; supplied archive. [5] Project evidence: frozen Review 1 summary, raw run traces and base-R outputs.', small)
c.save()
(OUT / 'submission_text.md').write_text('\n\n'.join(plain) + '\n', encoding='utf-8')
inputs = ['presentation/content.json', 'presentation/prepare.py', 'presentation/build.mjs', 'presentation/figures.R', 'data/review1_summary.csv', 'output/review1/group_statistics.csv', 'output/review1/inference.txt', 'output/review1/policy_predictions.csv', 'output/review1/learning_curve.png', 'output/review1_presentation/restart_predictions.png'] + [f"data/runs/main/{r['run_id']}/trace.csv" for r in main]
manifest = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
for p in ['presentation/render_final.mjs', 'presentation/export_slide_pdf.py', 'presentation/check_originality.py', 'configs/study.json', 'docs/SYLLABUS_MAP.md', 'output/pdf/review1_manifest.json']:
    manifest[p] = hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
(OUT/'submission_text.md').write_text('\n\n'.join(plain) + '\n', encoding='utf-8')
(OUT/'input_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'main_n': 24, 'baseline_n':12, 'slides':15, 'planned_seconds':total, 'submission_pages':4, 'input_hashes':len(manifest)}))
