"""Minimal paper-style PDF built from R outputs and raw experiment metadata."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
ROOT=Path(__file__).resolve().parents[1]


def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def build(mode='review1'):
    out=ROOT/'output'/mode
    evidence=json.loads((out/'audit.json').read_text())
    expected=24 if mode=='review1' else 120
    if evidence.get('status')!='passed' or evidence.get('mode')!=mode or evidence.get('completed_main_runs')!=expected:
        raise ValueError('A completed raw-trace audit is required before report generation.')
    stats=read_csv(out/'group_statistics.csv')
    audit=read_csv(out/'audit_counts.csv')[0]
    if int(audit['completed'])!=expected or sum(int(r['n']) for r in stats)!=expected:
        raise ValueError('Report sample sizes do not match the completed milestone.')
    if mode=='review2':
        validation_rows=read_csv(out/'policy_validation.csv')
        if len(validation_rows)!=3 or {int(r['k']) for r in validation_rows}!={1,2,4} or any(int(r['attempts'])!=10 for r in validation_rows):
            raise ValueError('Final report requires ten completed fresh-seed attempts for each policy.')
    pred=read_csv(out/'policy_predictions.csv')
    selected=json.loads((ROOT/'data/baseline.json').read_text())
    baseline=next(r for r in stats if float(r['train_fraction'])==.6 and float(r['weight_decay'])==selected['weight_decay'])
    cap=int(audit['cap']); n=int(audit['completed'])
    destination=ROOT/'output/pdf'/f'{mode}_report.pdf'
    destination.parent.mkdir(parents=True,exist_ok=True)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='PaperTitle',fontName='Helvetica-Bold',fontSize=17,leading=21,spaceAfter=10))
    styles.add(ParagraphStyle(name='SmallBody',fontName='Helvetica',fontSize=9.3,leading=13,spaceAfter=7))
    styles.add(ParagraphStyle(name='Caption',fontName='Helvetica',fontSize=8.2,leading=11,spaceAfter=10,textColor=colors.HexColor('#444444')))
    styles['Heading2'].fontSize=12;styles['Heading2'].leading=15;styles['Heading2'].spaceBefore=10
    story=[]; markdown=[]
    def para(text,style='SmallBody'):
        story.append(Paragraph(text,styles[style]));markdown.append(text.replace('<b>','**').replace('</b>','**'))
    def heading(text):para(text,'Heading2')
    def page():story.append(PageBreak());markdown.append('\n---\n')
    def fig(name,caption,height=2.55):
        path=out/f'{name}.png'
        if not path.exists():raise FileNotFoundError(path)
        from PIL import Image as PILImage
        with PILImage.open(path) as im:w,h=im.size
        width=6.45*inch;target_h=width*h/w
        if target_h>height*inch:width*=height*inch/target_h;target_h=height*inch
        story.append(Image(str(path),width=width,height=target_h))
        para(caption,'Caption');markdown.append(f'![{caption}](../{mode}/{name}.png)')
    def table(rows,widths):
        cells=[[Paragraph(escape(str(c)),styles['Caption']) for c in row] for row in rows]
        t=Table(cells,colWidths=[w*inch for w in widths],repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E9EDF0')),('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),
                              ('LINEBELOW',(0,0),(-1,0),.5,colors.grey),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#DDDDDD'))]))
        story.append(t);markdown.extend([' | '.join(map(str,row)) for row in rows])
    def fmt(value):return f'{float(value):,.0f}'
    para('Grokking Under a Fixed Budget:<br/>One Long Run or Several Restarts?','PaperTitle')
    para(f'<b>{"Review 1 - preliminary study" if mode=="review1" else "Review 2 - expanded study"}</b> | Protocol established 13 October 2026 | BAMAT207 Probability and Statistics')
    heading('1. Question and idea')
    para('A neural network may learn the examples it was trained on before it learns a rule that works on unseen examples. When that improvement is delayed, it is called grokking. We study how much the waiting time varies between independently initialized runs.')
    para('Our question is whether a fixed training budget is better spent on one long run or several shorter runs starting from fresh random weights. Grokking timing and restart strategies already have prior research. Their connection here is a proposed empirical contribution, not a claim that worldwide novelty has been established.')
    heading('2. Experiment')
    para('Modular addition wraps a sum back into 0-30: for example, (30 + 4) mod 31 = 3. One training update adjusts the network weights once using the entire training subset.')
    para('We generate all 961 ordered pairs for y = (a + b) mod 31. At 60% training data, 576 pairs train the network and 385 unseen pairs measure generalization. '+('The expanded study also uses 40% data: 384 training and 577 unseen pairs. ' if mode=='review2' else '')+'The split seed is fixed. Initialization seeds are independent, so the random variable is conditional on this dataset split.')
    para('The network has one causal attention block, embedding size 64, four attention heads and a 128-unit feed-forward layer. There is no dropout or layer normalization. Full-batch AdamW uses learning rate 0.003 and betas (0.9, 0.98); weight decay is varied across 0.3, 1 and 3. Computation uses float32 with TF32 disabled.')
    devices=sorted({r['device'] for r in read_csv(out/'analysis_rows.csv')})
    if mode=='review2':
        para('CPU execution uses four threads per run; three main processes overlap sequential validation. CUDA was unavailable. Budgets count logical updates along resumed trajectories; recovery can repeat unsaved work. Physical recovery overhead is not measured. Runtime includes CPU contention, excludes paused intervals and may omit lost partial-checkpoint work.')
    else:
        para(f'Execution device: {", ".join(devices)}. CPU runs use four threads each; independent main runs may execute in three separate processes. CUDA was unavailable to this execution environment. Update counts are the primary budget unit; runtime includes scheduling and logging overhead.')
    para(f'T is the checkpoint confirming three consecutive evaluations with unseen accuracy at least 95% and training accuracy at least 99%. Evaluations occur every 25 updates. Memorization time is recorded separately. Our operational delayed label requires T to be at least three times memorization time and at least 200 updates later. This label identifies a delay; it does not prove a particular mechanism.')
    para(f'Each main run is observed to C = {cap:,} updates. If it has not generalized, T remains unknown and the run is retained as unfinished within this budget. U = min(T, C) is a separate, fully observed capped-time outcome. Pilot runs select the baseline and are excluded from main-study statistics.')
    heading('Current evidence')
    para(f'<b>{n} completed main-study runs</b>; {audit["pilot_runs"]} pilot runs; {audit["failed"]} failed and {audit["paused"]} paused main runs. Selected baseline: 60% data, weight decay {selected["weight_decay"]:g}. '+('Each of six experimental cells contains 20 seeds. Fresh-seed policy validation is separate from calibration.' if mode=='review2' else 'Review 1 results are exploratory; settings have small, unequal sample sizes.'))
    page()
    heading('3. From memorization to generalization')
    validation=(out/'validation.txt').read_text()
    representative=validation.split('Representative trace:')[-1].strip()
    fig('learning_curve',f'Figure 1. Early training window for {representative}, selected near the baseline median event time. The complete {cap:,}-update trace is retained. Markers show confirmation checkpoints; later dips do not reset the first confirmed T, and relapse flags are retained.',height=2.75)
    fig('time_distribution',f'Figure 2. Generalization times for the selected baseline: n = {baseline["n"]}, events = {baseline["successes"]}, unfinished = {baseline["censored"]}. This histogram describes observed events only, not the unrestricted distribution of T.',height=2.75)
    para('A gap between the curves means the model performs well on training examples while still struggling with unseen pairs. Different event times across seeds show variability under otherwise fixed conditions. These observations do not identify the cause of the delay.')
    relapse_count=sum(r.get('relapsed','').lower()=='true' for r in read_csv(out/'analysis_rows.csv'))
    event_count=sum(int(r['successes']) for r in stats)
    para(f'{relapse_count} of {event_count} generalized runs ({n} total runs) had at least one later unseen-accuracy dip below 95%. T therefore measures the first confirmed three-checkpoint event, not permanent accuracy. This distinction also applies to the restart success predictions.')
    page()
    heading('4. Variability and budget reliability')
    rows=[['Train fraction','Weight decay','Runs','Events','Delayed','Mean U','SD U']]
    for r in stats:rows.append([r['train_fraction'],r['weight_decay'],r['n'],r['successes'],r['delayed'],fmt(r['mean_capped_time']),fmt(r['sd_capped_time'])])
    table(rows,[.85,.85,.45,.65,.65,1.1,1.1])
    para('All time values are optimizer updates. A success is a confirmed threshold event by C. Means and standard deviations describe capped time U; unfinished runs are included at the cap. Conditional medians among successful runs are available in the CSV but must not be confused with an unrestricted median.')
    if mode=='review2':para('A cell with no events has constant U = C. Zero SD of U does not mean zero variability of T; a degenerate bootstrap mean interval also misses uncertainty from events not seen in the sample.')
    para(f'For the baseline, observed success probability is {baseline["successes"]}/{baseline["n"]} = {float(baseline["success_probability"]):.1%}, with exact 95% interval {float(baseline["prob_ci_low"]):.1%} to {float(baseline["prob_ci_high"]):.1%}. Mean U has a bootstrap 95% interval of {fmt(baseline["mean_ci_low"])} to {fmt(baseline["mean_ci_high"])} updates. The delayed count uses the operational timing criterion, not a mechanistic diagnosis.')
    fig('setting_comparison','Figure 3. Capped-time comparison '+('in both data fractions; 20 seeds per cell.' if mode=='review2' else 'at 60% data.')+' Dots represent independent runs; unfinished runs remain at the cap.',height=2.0 if mode=='review2' else 2.4)
    fig('budget_probability','Figure 4. Empirical F(t) at 60% data, with all completed runs in each setting as the denominator. The curve is supported only up to C.',height=2.0 if mode=='review2' else 2.4)
    page()
    heading('5. One long run or several restarts?')
    para('For k independent runs that each receive B/k updates, the probability of at least one success is 1 - [1 - F(B/k)]<super>k</super>. The formula follows from independence; the research question is whether splitting the budget helps in the measured setting.')
    fig('restart_predictions','Figure 5. Predicted policy success across total budgets, on a log update axis. Each curve uses the same baseline calibration runs. The intervals listed below at B = C transform exact 95% binomial intervals; policy estimates are correlated.',height=2.7)
    reference_budget=min(cap,max(100,int((selected.get('pilot_median',cap)+99)//100)*100))
    if reference_budget < cap:
        reference=[r for r in pred if int(r['total_budget'])==reference_budget]
        para(f'At B = {reference_budget:,}, a reference budget rounded from the pilot median, predicted probabilities are '+
             '; '.join(f'k = {r["k"]}: {float(r["predicted_success"]):.1%}' for r in reference)+'. These are exploratory predictions, not validation results.')
    para('At the full observation budget B = C:')
    for r in pred:
        if int(r['total_budget'])==cap:
            para(f'k = {r["k"]}: {int(float(r["per_run_budget"])):,} updates per run; predicted success {float(r["predicted_success"]):.1%} (interval {float(r["ci_low"]):.1%} to {float(r["ci_high"]):.1%}).')
    para('<b>These are calibration predictions.</b> '+('Page 7 compares them with independent fresh-seed validation.' if mode=='review2' else 'Review 2 tests them on fresh seeds.')+' Equal updates are compared within one setting; different training-data fractions have different costs per update. Runtime is recorded separately.')
    para('A generous cap can make all policies highly successful while obscuring differences near the learning transition. Predictions at smaller budgets remain unvalidated.')
    page()
    heading('6. Study scope and syllabus' if mode=='review2' else '6. Progress and Review 2')
    if mode=='review1':
        para('Review 1 implements the experiment protocol, training and checkpoint resumption, repeated-run export, fixed-budget policy runner, preliminary R analysis and this report. These components represent the planned approximately 65% implementation milestone; that percentage is not a measure of statistical evidence collected.')
        para('Review 2 expands to 20 seeds in each of six settings (120 main runs), then performs ten fresh-seed attempts for each of k = 1, 2 and 4. It adds censored distribution fitting, multiple regression and two-factor ANOVA. Small validation samples may leave policy differences inconclusive; that is an acceptable result.')
    else:
        para('The final study includes 120 main runs, nine pilot runs and 70 independent validation runs grouped into 30 fixed-budget attempts. Review 1 remains a separate frozen milestone. All runs retain configurations, evaluation traces and failure status; checkpoint resumption and outcomes reconstructed from traces are verified.')
        para(f'Across the six cells, {sum(int(r["censored"]) for r in stats)} runs remain unfinished within the cap. Finite observation cannot identify unrestricted mean T. Findings are conditional on the fixed split, architecture and CPU numerical environment; these samples do not establish universal restart advice.')
    heading('Syllabus connection')
    para('Module 1: random variables, expectation, variance and independent events. Module 2: Bernoulli/binomial outcomes and candidate Exponential, Gamma and Weibull time models. Module 3: confidence intervals and hypothesis tests. Module 4: correlation and regression. Module 5: one-way and two-factor ANOVA. The grokking application provides a contemporary topic for Module 6. Methods with unsuitable assumptions or sparse counts are not forced onto the data.')
    para('R output includes exact binomial confidence intervals, bootstrap capped-mean intervals, Welch comparisons with Holm adjustment, one-way ANOVA with permutation sensitivity, and correlation/regression. These are supporting statistical analyses; confidence intervals and sensitivity checks accompany the point estimates.')
    if mode=='review2':
        summary=read_csv(out/'model_summary.csv')[0]
        para(f'At 60% data, one-way ANOVA gives p = {float(summary["one_way_p"]):.4g}; permutation sensitivity p = {float(summary["one_way_permutation_p"]):.4g}. Pearson correlation of U with log decay is {float(summary["pearson_r"]):.3f}; Spearman correlation with decay is {float(summary["spearman_r"]):.3f}. These describe the measured settings, not an unrestricted timing law.')
        para(f'Two-factor residual Shapiro-Wilk p = {float(summary["residual_shapiro_p"]):.4g}. Small p values and the plotted diagnostics caution against relying only on ordinary normal-error tests. Permutation checks also require exchangeable errors.')
        fig('model_diagnostics','Figure 6. Diagnostics for the two-factor model. Capping, skew and differing group spread can limit ordinary ANOVA inference; permutation sensitivity is reported alongside it.',height=3.5)
    if mode=='review2':
        page();heading('7. Expanded statistical analysis')
        terms=read_csv(out/'two_factor_tests.csv')
        para('Two-factor ANOVA uses data fraction, categorical weight decay and their interaction. The permutation check uses reduced-model residual permutation for each term; it is a sensitivity check requiring exchangeable errors, and does not eliminate unequal-variance concerns.')
        term_labels={'factor(train_fraction)':'Training fraction','factor(weight_decay)':'Weight decay',
                     'factor(train_fraction):factor(weight_decay)':'Fraction x decay'}
        table([['Term','ANOVA p','Permutation p']]+[[term_labels.get(r['term'],r['term']),f'{float(r["p_value"]):.4g}',f'{float(r["permutation_p"]):.4g}'] for r in terms],[2.8,1.3,1.5])
        coeff=read_csv(out/'regression_coefficients.csv')
        fraction_beta=next(float(r['estimate']) for r in coeff if r['term']=='train_fraction')
        decay_beta=next(float(r['estimate']) for r in coeff if r['term']=='log(weight_decay)')
        para(f'Multiple regression describes U using data fraction and log decay (R-squared = {float(summary["multiple_R_squared"]):.3f}). Holding decay fixed, increasing training data from 40% to 60% changes fitted U by {fraction_beta*.2:,.0f} updates. A one-unit increase in log decay changes it by {decay_beta:,.0f} updates. Full coefficients are in the CSV. This linear description does not replace the interaction model.')
        if (out/'distribution_fits.png').exists():fig('distribution_fits','Figure 7. Candidate families model T minus the 50-update confirmation lag, discretized to evaluations. Unfinished runs contribute survival probabilities. AIC ranks these candidates without establishing the true distribution.',height=2.5)
        if (out/'distribution_fits.csv').exists():
            fr=read_csv(out/'distribution_fits.csv');table([['Model','Converged','AIC']]+[[r['distribution'],r['converged'],f'{float(r["AIC"]):.2f}'] for r in fr],[2.2,1.6,1.8])
            converged=[r for r in fr if r['converged'].lower()=='true']
            if converged:
                best=min(converged,key=lambda r:float(r['AIC']))
                para(f'{best["distribution"]} has the lowest AIC among these candidates. Fitting uses only the selected baseline: {baseline["n"]} runs, {baseline["successes"]} events and {baseline["censored"]} unfinished runs. This small-sample ranking does not establish the true timing law.')
        page();heading('8. Fresh-seed validation')
        if (out/'policy_validation.png').exists():
            fig('policy_validation','Figure 8. Fresh-seed outcomes versus calibration predictions. Exact confidence intervals reflect only ten attempts per policy.',height=2.5)
            ps=read_csv(out/'policy_validation.csv');table([['k','Successes / attempts','Observed (95% CI)','Mean runtime (s)']]+[[r['k'],f'{r["successes"]} / {r["attempts"]}',f'{float(r["observed_probability"]):.0%} ({float(r["ci_low"]):.1%}-{float(r["ci_high"]):.1%})',f'{float(r["mean_runtime_seconds"]):,.1f}'] for r in ps],[.4,1.4,2.8,1.3])
            para('Measured success: '+ '; '.join(f'k = {r["k"]}: {r["successes"]}/{r["attempts"]}' for r in ps)+'. '+('All policies succeeded in every attempt. This generous budget does not distinguish them; it does not establish equivalence.' if all(r['successes']==r['attempts'] for r in ps) else 'The samples are small; differences must be interpreted with the exact intervals and policy test in policy_tests.txt.'))
            test=read_csv(out/'policy_test_summary.csv')[0]
            if test['p_value'] not in ('NA',''):
                p_value=float(test['p_value'])
                para(f'{escape(test["method"])}: p = {p_value:.4g}. '+('The observed results do not provide clear evidence for a policy difference; this does not establish equivalence.' if p_value>=.05 else 'The observed association is conditional on this task, split and budget; its magnitude must be assessed with the intervals.'))
        else:para('Fresh-seed validation has not yet been completed. No validation results are claimed.')
        para('The validation outcome measures at least one confirmed generalization event by the budget. All policies allocate equal total optimizer updates and run sequentially. These results are conditional on one modular-addition task, one architecture and one fixed dataset split; they do not generalize automatically to larger networks or other tasks.')
        para('Runtime is descriptive because CPU contention from main-study collection overlaps validation. The table is not a controlled wall-clock speed comparison.')
    heading('References and reproducibility')
    para('Power et al. (2022), Grokking: Generalization Beyond Overfitting on Small Algorithmic Datasets. arxiv.org/abs/2201.02177.<br/>Truong et al. (2026), First-Passage Prediction of Grokking Delay. arxiv.org/abs/2605.18845.<br/>Streeter, Golovin and Smith (2007), Restart Schedules for Ensembles of Problem Instances. cs.cmu.edu/~dgolovin/papers/aaai07b.pdf.<br/>BAMAT207 official theory and embedded-lab syllabus, version 1, supplied archive.')
    para('Reproduce using the commands in README.md. Raw run configurations, traces and summary.csv are retained. R analysis uses only base R. This PDF and its graphs are generated from those outputs. Full inferential details are in inference.txt.')
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.grey)
        canvas.drawString(48,27,'Grokking fixed-budget study | BAMAT207')
        canvas.drawRightString(564,27,str(doc.page));canvas.restoreState()
    doc=SimpleDocTemplate(str(destination),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=42,
                         title='Grokking Under a Fixed Budget',author='Probability and Statistics Lab Project')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (ROOT/'output/pdf'/f'{mode}_report.md').write_text('\n\n'.join(markdown),encoding='utf-8')
    # Manifest establishes the exact inputs used by this report.
    summary_input=ROOT/'data/review1_summary.csv' if mode=='review1' and (ROOT/'data/review1_summary.csv').exists() else ROOT/'data/summary.csv'
    inputs=[summary_input,ROOT/'data/baseline.json',ROOT/'data/runtime_lock.json',ROOT/'output/runtime.json',ROOT/'configs/study.json',ROOT/'analysis/analyze.R',ROOT/'grokking/report.py',ROOT/'docs/PROTOCOL.md',
            out/'group_statistics.csv',out/'policy_predictions.csv']+sorted(out.glob('*.png'))
    inputs += sorted((ROOT/'sources').glob('*.pdf'))
    for row in read_csv(out/'analysis_rows.csv'):
        inputs.extend([ROOT/'data/runs/main'/row['run_id']/'config.json',ROOT/'data/runs/main'/row['run_id']/'trace.csv'])
    if mode=='review2':
        inputs += [ROOT/'data/policies.csv']+sorted(out.glob('*.csv'))+sorted(out.glob('*.txt'))+[out/'audit.json']
        for row in read_csv(ROOT/'data/summary.csv'):
            if row['stage']=='validation':
                inputs.extend([ROOT/'data/runs/validation'/row['run_id']/'config.json',ROOT/'data/runs/validation'/row['run_id']/'trace.csv'])
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs if p.exists()}
    (ROOT/'output/pdf'/f'{mode}_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(destination)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['review1','review2'],nargs='?',default='review1');build(p.parse_args().mode)
