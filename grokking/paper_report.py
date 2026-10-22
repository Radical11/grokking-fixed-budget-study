"""Eight-page integrated paper and four-page supplement, gated on actual audited data."""
from pathlib import Path
from xml.sax.saxutils import escape
import csv,json
from .paper_typesetting import render_source

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/paper_v2'

def read(name):
    with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def number(x):return f'{float(x):,.0f}'
def percent(x):return f'{100*float(x):.1f}%'
def pvalue(x):return f'{float(x):.3g}'

def build():
    audit=json.loads((OUT/'audit.json').read_text())
    assert audit['status']=='passed' and audit['validation_attempts']==540 and audit['calibration']==90
    stats=read('calibration_statistics.csv');policy=read('policy_statistics.csv');risk=read('risk_differences.csv')
    with (ROOT/'data/paper_v2/run_summary.csv').open(newline='',encoding='utf-8') as f:
        new_runs=[r for r in csv.DictReader(f) if r['reused']=='False']
    runtime_hours={cohort:sum(float(r['elapsed_seconds']) for r in new_runs if r['cohort']==cohort)/3600 for cohort in ('calibration','validation')}
    runtime_text=(f'Recorded per-run elapsed times sum to {runtime_hours["calibration"]:.2f} run-hours for new calibration and {runtime_hours["validation"]:.2f} for validation. Parallel jobs overlap, so these sums are not wall-clock duration. Unsaved work before interruption is not fully measured.')
    models=read('distribution_fits.csv');representative=read('representative_run.csv')[0]
    refs=json.loads((ROOT/'paper/v2/references.json').read_text())
    legacy=[]
    with (ROOT/'output/review2/group_statistics.csv').open(newline='',encoding='utf-8') as f:legacy=list(csv.DictReader(f))
    baseline=next(s for s in stats if s['endpoint']=='first' and int(s['split_seed'])==20261013)
    primary=[r for r in risk if r['endpoint']=='first'];significant=[r for r in primary if float(r['p_holm'])<.05]
    def group(split,B,k,ep='first'):
        return next(p for p in policy if int(p['split_seed'])==split and int(p['total_budget'])==B and int(p['k'])==k and p['endpoint']==ep)
    original8=[group(20261013,8000,k) for k in (1,2,4)]
    converged=[m for m in models if m['converged']=='TRUE']
    assert converged, 'No converged timing candidate; do not rank invalid fits'
    best_model=min(converged,key=lambda x:float(x['AIC']))
    total_events=sum(int(s['events']) for s in stats if s['endpoint']=='first')
    stable_events=sum(int(s['events']) for s in stats if s['endpoint']=='stability')
    class Article:
        def __init__(self):self.markdown=[]
        def p(self,text,style='BodyPaper'):
            if style=='CaptionPaper':self.markdown.append('<!-- style: CaptionPaper -->')
            prefix='# ' if style=='TitlePaper' else '## ' if style=='Heading2' else ''
            self.markdown.append(prefix+text.replace('<b>','**').replace('</b>','**'))
        def h(self,text):self.p(text,'Heading2')
        def page(self):self.markdown.append('---')
        def fig(self,name,caption,width=6.65):
            assert (OUT/(name+'.png')).exists()
            self.markdown.extend([f'<!-- figure-width: {width} -->',f'![Figure: {name.replace("_"," ")}]({name}.png)'])
            self.p(caption,'CaptionPaper')
        def table(self,rows,widths):
            self.markdown.append('<!-- table-widths: '+','.join(map(str,widths))+' -->')
            lines=['| '+' | '.join(map(str,rows[0]))+' |','| '+' | '.join('---' for _ in rows[0])+' |']
            lines.extend('| '+' | '.join(map(str,row))+' |' for row in rows[1:])
            self.markdown.append('\n'.join(lines))
        def save(self,name,pages):
            source=OUT/Path(name).with_suffix('.md')
            source.write_text('\n\n'.join(self.markdown)+'\n',encoding='utf-8',newline='\n')
            render_source(source,OUT/name,pages)
    paper=Article()
    paper.p('Grokking Under a Fixed Budget:<br/>An Empirical Study of Learning Time and Independent Restarts','TitlePaper')
    paper.p('BAMAT207 Probability and Statistics | Follow-up protocol specified 15 October 2026<br/>Name: [Your name] | Registration number: [Your registration number]','CaptionPaper')
    paper.h('Abstract')
    abstract=(f'Grokking describes delayed improvement on unseen examples after a model fits its training examples. We study time to confirmed generalization in a small transformer learning addition modulo 31. An original 120-run setting study is extended with 90 calibration observations across three fixed dataset splits, including 20 reused observations, and 540 fresh policy attempts. One, two or four independent runs share total budgets of 8,000 or 12,000 updates. First confirmation requires three qualifying evaluations; a secondary endpoint requires a 500-update accuracy window. On the original split at 8,000 updates, observed first-confirmation success is {", ".join(p["successes"]+"/30" for p in original8)} for the three policies. Four restarts underperform one long run at 8,000 updates on all three splits after Holm correction. At 12,000, only one of the three four-run contrasts is detected; no two-run contrast is detected. In total, {len(significant)} of twelve pre-specified contrasts pass adjusted testing at 0.05. Exact intervals are reported separately for every split. The design estimates budget-dependent reliability without treating unfinished times as known completions or inferring equivalence from nonsignificance. The proposed contribution is a reproducible empirical comparison, conditional on this task, architecture and numerical environment.')
    paper.p(abstract)
    paper.h('1. Introduction and objectives')
    paper.p('A model can answer its practice questions correctly while still failing on questions excluded from training. Delayed improvement on the latter is the pattern called grokking [1]. A single successful trajectory cannot describe how often that pattern occurs or how long another random start might take. Our objectives are to characterize this variation, estimate success within a finite budget, and test the predictions obtained when that budget is divided among independent starts.')
    paper.h('2. Related work and contribution')
    paper.p('Power et al. established the grokking phenomenon [1]. Truong et al. study prediction of the delay as a first-passage problem [2], while restart schedules have an established randomized-algorithm literature [3]. Ootani emphasizes repeated seeds and a controlled numerical environment [4]. Our contribution is the measured connection between completion-time variability, equal-update allocation and a finite stability check. We do not introduce the restart identity or establish worldwide novelty.')
    paper.page()
    paper.h('3. Experimental design')
    paper.p('Generate all 961 ordered pairs a,b in {0,...,30}, with label (a+b) mod 31. For example, (30+4) mod 31=3. The baseline uses 576 practice pairs and 385 held-out pairs. The network is a fixed causal transformer with 36,992 trainable parameters [6]: one attention block, embedding width 64, four heads and a 128-unit ReLU feed-forward layer, without biases, dropout or layer normalization. Full-batch AdamW [5] uses learning rate 0.003, betas (0.9,0.98) and weight decay 1. The supplementary setting study varies decay and data fraction; architecture and numerical rules remain fixed.')
    paper.table([['Cohort','Purpose','Sample'],['Original main study','Exploratory setting comparisons','120 runs; 20 per six cells'],['Follow-up calibration','Completion curves for three fixed splits','90 runs; 20 reused + 70 new'],['Follow-up validation','Fresh equal-budget comparisons','540 attempts; 1,260 runs']], [1.45,2.55,2.65])
    paper.p('Split seeds are 20261013, 20261014 and 20261015. Each has 30 calibration runs to C=30,000 updates. Fresh validation uses 30 attempts per split/budget/policy, with k=1,2,4 constituent runs receiving B/k updates each. Seeds are disjoint between calibration and validation. All allocated updates execute, even if success occurs early. This is an at-least-one-success policy, not prediction averaging across models.')
    paper.h('3.1 Outcomes and prospective controls')
    paper.p('An update is one learning step; accuracy is the fraction of correct answers. Evaluate every 25 updates, excluding update zero from streaks. T records the third consecutive check with practice accuracy at least 99% and held-out accuracy at least 95%. Memorization time M uses three checks with at least 99% practice accuracy; T itself need not be delayed. T_500 records the 21st consecutive qualifying check, spanning 500 updates. Both are final confirmation times, not the beginning of a streak. T_500 measures finite-window stability, not permanent learning.')
    paper.p('The budgets were chosen using the original 20 baseline traces, after all old policies succeeded 10/10 at 30,000 updates. That data-informed choice is disclosed. The follow-up protocol and full seed manifest were committed before training; all calibration predictions were frozen before validation. Budgets, settings and sample sizes were not retuned to produce a preferred result. The original delivery remains archived separately.')
    paper.h('3.2 Execution')
    paper.p('Training uses CPU, four threads per run, float32, deterministic algorithms and disabled TF32, with no more than three independent processes. CUDA was unavailable in the recorded environment. Checkpoint recovery may repeat unsaved physical work; elapsed time excludes downtime and is affected by scheduling contention. Equality refers to logical optimizer updates within the same setting, not wall-clock speed or physical recovery overhead.')
    paper.p(runtime_text)
    paper.page()
    paper.h('4. Learning-time variability')
    paper.p(f'Across the 90 calibration observations, {total_events} first confirmations and {stable_events} 500-update confirmations occur by C. On the original split, mean capped first-confirmation time U is {number(baseline["mean_U"])} updates, median {number(baseline["median_U"])} and sample SD {number(baseline["sd_U"])}. The means describe U=min(T,C); an unfinished T remains unknown. Calibration extends only the baseline setting, not all six original experimental cells.')
    paper.fig('learning_delay',f'Figure 1. Top: an original-split calibration run selected closest to median T, with first confirmation at {number(representative["first_time"])} updates. The early window is illustrative; the full trace is retained. Bottom: empirical first-confirmation curves for all three splits, each with 30 calibration observations through 30,000 updates and unfinished outcomes retained in its denominator. Split 1 includes 20 reused runs; the other 70 calibration observations are new.')
    paper.p('Each curve is the fraction of its 30 runs confirmed by time t. Unfinished runs remain in the denominator. Differences are conditional on these fixed partitions, not all possible tasks.')
    # The capped-time distribution is also retained as a standalone figure.
    paper.table([['Split','First events','500-window events','Mean U','Median U'],*[['S'+str(i+1),next(s for s in stats if int(s['split_seed'])==split and s['endpoint']=='first')['events']+'/30',next(s for s in stats if int(s['split_seed'])==split and s['endpoint']=='stability')['events']+'/30',number(next(s for s in stats if int(s['split_seed'])==split and s['endpoint']=='first')['mean_U']),number(next(s for s in stats if int(s['split_seed'])==split and s['endpoint']=='first')['median_U'])] for i,split in enumerate((20261013,20261014,20261015))]], [0.65,1.15,1.65,1.6,1.6])
    paper.page()
    paper.h('5. Budget reliability: prediction and validation')
    paper.p('For k independent runs, each receiving B/k updates, the chance all fail is [1-F(B/k)]^k. Thus P(at least one succeeds)=1-[1-F(B/k)]^k. We estimate F from the separate calibration sample; validation uses fresh seeds. Exact binomial intervals accompany observed proportions. Independent bootstrap resampling of calibration runs and policy attempts captures both sources of uncertainty when comparing prediction with observation.')
    paper.fig('policy_validation','Figure 2. Filled points show observed first-confirmation proportions with exact 95% binomial intervals (30 fresh attempts per policy). Open points show frozen predictions with the transformed exact calibration intervals (30 separate calibration runs per split). All intervals are pointwise. S1 includes 20 reused calibration runs; its prediction intervals do not adjust for the earlier budget choice. All six conditions are reported, including unfavourable or inconclusive outcomes.')
    paper.p('Three splits are fixed replications, not three new tasks. We interpret each panel separately. Point estimates near one can still have substantial uncertainty at n=30. Agreement with a prediction is not proof of the full timing model, and a nonsignificant contrast is not evidence that policies are equivalent.')
    paper.page()
    paper.h('5.1 Pre-specified policy comparisons')
    paper.p(f'Twelve two-sided Fisher exact tests compare k=2 or k=4 with k=1 within each budget and split. Each null hypothesis states that the success probabilities are equal. Holm correction is applied jointly across all twelve; {len(significant)} adjusted p-values are below 0.05. The risk difference is restart probability minus the one-run probability. Negative values favour the one-run policy; positive values favour the specified restart policy. Figure 3 uses conservative pointwise intervals from exact binomial margins. Planned bootstrap intervals remain in the numerical output as sensitivity summaries. Table differences are in percentage points (pp).')
    paper.fig('risk_differences','Figure 3. First-confirmation probability differences. S1-S3 identify the fixed splits. Bounds combine two exact 97.5% marginal intervals to give conservative pointwise 95% coverage for a difference; they are not simultaneous across all contrasts. This avoids a collapsed bootstrap interval in constant-outcome groups. The zero line denotes equal probabilities.',width=6.3)
    rows=[['Split / B','2 runs minus 1','4 runs minus 1','Holm p: 2 / 4']]
    for si,split in enumerate((20261013,20261014,20261015),1):
        for B in (8000,12000):
            a=next(r for r in primary if int(r['split_seed'])==split and int(r['total_budget'])==B and int(r['k'])==2)
            b=next(r for r in primary if int(r['split_seed'])==split and int(r['total_budget'])==B and int(r['k'])==4)
            rows.append([f'S{si} / {B//1000}k',f'{100*float(a["risk_difference"]):+.1f} pp',f'{100*float(b["risk_difference"]):+.1f} pp',pvalue(a['p_holm'])+' / '+pvalue(b['p_holm'])])
    paper.table(rows,[1.15,1.65,1.65,2.2])
    paper.page()
    paper.h('6. First confirmation versus 500-update stability')
    paper.p('The primary rule confirms three checks separated by 25 updates. It does not require later accuracy to remain high. In the original 120-run study, 62 of 83 generalized runs later fell below 95% held-out accuracy. The follow-up therefore derives a distinct endpoint requiring 21 qualifying checks, spanning 500 updates, from exactly the same traces.')
    paper.fig('stability_comparison','Figure 4. Both endpoints use the same attempt and must finish within its constituent cap B/k; panels use total B=8,000 or 12,000. Circles denote first confirmation and triangles the 500-update window. Bars are exact 95% intervals. The two endpoints are correlated, not independent samples.')
    paper.p('A stability event must finish before the constituent cap; no extra follow-up is granted to a short run. The stability event implies the primary event, so its probability cannot exceed primary success in the same sample. These secondary comparisons are descriptive. They distinguish a brief confirmation from a longer accuracy window, while allowing further deterioration after either event. Neither endpoint establishes permanent generalization or human-like rule understanding.')
    paper.page()
    paper.h('7. Supporting setting comparisons and timing models')
    paper.p('The original study retains 20 runs in each of six data-fraction/weight-decay cells. Its results provide exploratory context rather than additional validation attempts. The all-unfinished cell has U=C in every sample; zero sample SD of U does not imply zero variability in unrestricted T. Mean comparisons, regression and ANOVA describe capped outcomes only.')
    paper.table([['Data fraction','Decay','Events / n','Mean U','SD U'],*[[r['train_fraction'],r['weight_decay'],r['successes']+'/'+r['n'],number(r['mean_capped_time']),number(r['sd_capped_time'])] for r in legacy]], [1.3,.8,1.2,1.7,1.65])
    paper.p('At 60% data, Pearson correlation of U with log decay is -0.715 and Spearman correlation is -0.866. The original two-factor residual Shapiro-Wilk p=0.000199 cautions against normal-error ANOVA claims. Permutation sensitivity also assumes exchangeable errors. The additive regression R-squared=0.630 describes sample variation, not held-out prediction accuracy. These syllabus analyses remain exploratory.')
    paper.h('7.1 Candidate distributions')
    paper.p(f'The expanded original-split calibration sample fits Exponential, Gamma and Weibull timing families. The recording-grid likelihood assigns event mass G(t-50)-G(t-75) to T=t and survival 1-G(C-50) to an unfinished run. AIC balances fit and parameter count; among converged fits, {best_model["distribution"]} ranks lowest here (AIC {float(best_model["AIC"]):.2f}). This is candidate ranking, not proof of a true timing law. Fitted curves are supplied separately; policy predictions use empirical F, not these timing fits.')
    paper.table([['Candidate','Events / n','AIC','Converged'],*[[r['distribution'],r['events']+'/'+r['n'],f'{float(r["AIC"]):.2f}',r['converged']] for r in models]], [2.1,1.35,1.35,1.85])
    paper.p('The project applies random variables, capped expectation and variability, Bernoulli/binomial outcomes, intervals, hypothesis comparisons, regression and ANOVA where justified by the supplied syllabus [7]. It does not force a variance test or goodness-of-fit test onto unsuitable capped samples.')
    paper.page()
    paper.h('8. Discussion and limitations')
    paper.p('At 8,000 updates, one long run succeeds in 28/30 attempts on every split; four restarts succeed in 12/30, 9/30 and 11/30. All three contrasts survive Holm correction. At 12,000 updates, one run succeeds in 30/30 on every split, versus 24/30, 20/30 and 23/30 for four restarts; only the second-split contrast survives correction. No two-run contrast is detected. Dividing the budget too finely leaves less time for each learning delay. This interpretation is conditional on the measured curves, rather than a general argument against restarts. The earlier 30,000-update ceiling result remains consistent with these smaller-budget differences.')
    paper.p('Evidence is conditional on one arithmetic task, one small architecture, selected decay and three fixed splits. Thirty attempts per condition are useful for substantial differences but cannot reliably resolve tiny gaps or establish equivalence. Held-out pairs are excluded from gradient updates but monitored for the endpoint; no additional untouched test set is claimed. Calibration predictions across budgets are correlated, and S1 intervals do not adjust for budget selection using reused traces. Bootstrap intervals are pointwise; normal-error assumptions fail in the exploratory setting models. Three split replications do not establish transfer to larger networks, natural-language tasks or different numerical environments.')
    paper.h('9. Conclusion')
    paper.p('For this model and these three splits, four short runs are less reliable than one long run at 8,000 total updates. The 12,000-update results leave several comparisons unresolved; nonsignificance does not establish equality. Completion curves make budget allocation testable, while the 500-update endpoint shows why brief confirmation needs a separate stability description. Future work can test other tasks, additional splits and longer windows. No universal restart rule or new timing theorem is established.')
    paper.h('Data availability and contribution')
    paper.p('The versioned project repository retains source, fixed configuration, complete seed manifest, raw evaluation traces, R tables and graph sources, plus reproduction and audit commands. Repository access is controlled by its owner. Local checkpoints and dependency runtimes are excluded from Git. New training records, figures and manuscripts are separate from the archived original delivery. Established grokking and restart ideas are attributed; worldwide novelty and institutional similarity clearance are not claimed.')
    paper.h('References')
    for ref in refs:
        paper.p(f'[{ref["id"]}] {escape(ref["label"])}. <i>{escape(ref["title"])}</i>. {escape(ref["status"])}. {escape(ref["url"])}','CaptionPaper')
    paper.save('paper.pdf',8)
    supplement=Article()
    supplement.p('Technical Supplement','TitlePaper')
    supplement.h('S1. Design, samples and independence')
    supplement.p('The original delivery at commit d8ffc56 contains 9 pilot runs, 120 main runs and 70 validation constituents. Its 20 original baseline main runs are reused once in the 90-run follow-up calibration sample; they are not additional observations. Seventy new calibration runs and 1,260 fresh validation runs add 1,330 unique training runs. The follow-up has 540 independent budget attempts, not 1,260 independent policy observations.')
    supplement.table([['Quantity','Fixed total'],['Splits / calibration per split','3 / 30'],['Calibration observations / reused / new','90 / 20 / 70'],['Budgets / policies / attempts per cell','2 / 3 / 30'],['Validation attempts / constituent runs','540 / 1,260'],['Additional logical training updates','7,500,000']], [3.7,2.95])
    supplement.p('New calibration seeds run consecutively from 100000 in split/replicate order; validation seeds start at 200000 in split/budget/k/attempt/component order. The complete manifest precedes new training. Changing the initialization seed does not change the split-seeded permutation. Partitions are regenerated and checked for correct labels and disjointness in the raw audit. The smaller 40% original training sets are nested within the 60% sets; comparisons across those fractions also change the held-out pair set.')
    supplement.h('S1.1 Phase gate and execution')
    supplement.p('All 90 calibration observations finish before predictions and raw-trace hashes are frozen. Validation verifies this freeze before it starts or resumes. Configurations, complete traces, statuses and errors are retained; unknown event times remain blank. No seed is replaced for poor learning performance. A technical failure remains a technical failure and must be resumed or reported, not converted into a negative learning outcome.')
    supplement.p('CPU runs use four threads, float32 and PyTorch 2.11.0+cu128; the CUDA-enabled library build does not imply GPU training. Up to three independent processes run concurrently. Checkpoints occur every 500 updates, and resumed work restores model, optimizer and RNG state. Lost partial-checkpoint work may repeat physically; logical budget equality remains distinct from wall-clock or recovery cost.')
    supplement.p(runtime_text)
    supplement.h('S1.2 Endpoint reconstruction')
    supplement.p('At update zero, record accuracy only. At each later 25-update check, increment a qualifying streak only if both practice >=0.99 and held-out >=0.95, otherwise reset to zero. Primary T is the first check ending a streak of length three. T_500 ends the first length-21 streak. A 500-update span requires 21 observations, not 20. Do not backdate either endpoint, and do not use checks after a run cap. A stability event must be at least 450 updates after first confirmation, but may occur much later if streaks reset.')
    supplement.page()
    supplement.h('S2. Statistical calculations and assumptions')
    supplement.p('For a fixed split, F_hat(t)=count(observed event time <=t)/30, through C=30,000. Unfinished times remain in the denominator and contribute no event. U=min(T,C) is fully observed, but is not an imputation of T. Histograms of observed events alone are conditional summaries. Constant U in an entirely unfinished cell does not imply constant T, and a degenerate bootstrap interval cannot recover uncertainty in an unseen tail.')
    supplement.p('For each policy attempt, the binary outcome is whether any of its k independent constituents confirms within B/k updates. Conditional on the fixed setting, P(success)=1-[1-F(B/k)]^k. Exact 95% Clopper-Pearson intervals use base R binom.test. Predicted intervals transform the single-run interval monotonically. These intervals are pointwise and correlated across budgets because the same calibration traces are reused. Original-split intervals do not adjust for choosing budgets using 20 reused observations; fresh validation comparisons use the already fixed design.')
    supplement.p('With R seed 20261015, use 5,000 resamples. Capped mean intervals resample calibration observations. Risk-difference intervals independently resample the two policy-attempt groups. Prediction-minus-observation intervals independently resample the calibration event times and the observed attempt outcomes, transform the bootstrap completion proportion, and subtract the bootstrap observed mean. Do not bootstrap constituent runs as if they were policy attempts. Secondary endpoints are correlated outcomes from the same attempt.')
    supplement.p('The primary family is twelve two-sided Fisher exact comparisons: k=2 versus k=1 and k=4 versus k=1, for two budgets and three splits. Holm adjustment applies to all twelve together, including identical-outcome cells assigned descriptive p=1. Secondary stability comparisons have intervals and no additional significance family. Pointwise bootstrap intervals must not be treated as simultaneous multiplicity-adjusted inference. At n=30, a small observed difference or nonsignificant result cannot establish equivalence.')
    supplement.p('A pre-validation implementation note adds conservative difference bounds [L1-U0,U1-L0] using two exact 97.5% marginal binomial intervals. Their noncoverage probabilities sum to at most 5%. These pointwise bounds remain nondegenerate when a binary group is constant; the main difference plot uses them, while the planned bootstrap outputs remain available. The same construction also bounds transformed-prediction minus observation. This changes no primary tests or outcomes.')
    supplement.h('S2.1 Candidate timing likelihood')
    supplement.p('For each candidate CDF G of X=T-50, the recorded event mass is G(t-50)-G(t-75), with G(x)=0 for nonpositive x. An unfinished observation contributes 1-G(C-50). Positive parameters are optimized on a log scale. Exponential has a rate; Gamma and Weibull have shape/scale parameters. AIC=2q-2 log(L). Use only the expanded original-split calibration sample and at least eight events. Model ranking remains conditional on this small sample.')
    supplement.h('S2.2 Exploratory syllabus analyses')
    supplement.p('The archived original study uses Welch comparisons with Holm adjustment, capped-time bootstrap intervals, Pearson/Spearman relationships, simple/multiple regression and one-/two-factor ANOVA. Capping, skew and unequal variance limit normal-error interpretations. The original residual-permutation sensitivity requires exchangeable errors and does not cure unequal variance. These analyses are supporting exploration, distinct from the pre-specified fresh policy tests.')
    supplement.page()
    supplement.h('S3. Complete validation counts')
    rows=[['Split','B','k','First / 30','Predicted first','500 window / 30']]
    for split in (20261013,20261014,20261015):
        for B in (8000,12000):
            for k in (1,2,4):
                a=group(split,B,k);b=group(split,B,k,'stability')
                rows.append(['S'+str(split-20261012),str(B),str(k),a['successes']+'/30',percent(a['predicted_probability']),b['successes']+'/30'])
    supplement.table(rows,[.55,.8,.4,1.3,1.75,1.85])
    supplement.p('Each row represents a different group of 30 fresh attempts. First and stability counts within a row come from the same attempts. Predictions use 30 separate calibration observations for that split and were frozen before validation. The complete exact probability intervals, transformed calibration intervals and bootstrap prediction errors are provided in policy_statistics.csv.')
    supplement.h('S3.1 Calibration samples')
    supplement.table([['Split','Endpoint','Events / 30','Mean capped time','Mean-time 95% bootstrap CI'],*[[str(int(s['split_seed'])-20261012),s['endpoint'],s['events']+'/30',number(s['mean_U']),number(s['mean_ci_low'])+' to '+number(s['mean_ci_high'])] for s in stats]], [.6,1.0,1.15,1.3,2.6])
    supplement.p('Secondary rows cap T_500 at C, giving U_500=min(T_500,C). S1=20261013, S2=20261014, S3=20261015. Twenty observations in S1 are reused from the original main study. All other follow-up seeds are new. New split seeds provide fixed-partition robustness checks rather than a random sample of all possible tasks or models.')
    supplement.page()
    supplement.h('S4. Complete primary comparisons')
    rows=[['Split / B','Contrast','Risk difference','Conservative 95% CI','Holm p']]
    for r in primary:
        rows.append(['S'+str(int(r['split_seed'])-20261012)+' / '+str(int(r['total_budget'])//1000)+'k',r['k']+' vs 1',f'{100*float(r["risk_difference"]):+.1f} pp',f'{100*float(r["conservative_ci_low"]):+.1f} to {100*float(r["conservative_ci_high"]):+.1f} pp',pvalue(r['p_holm'])])
    supplement.table(rows,[1.05,.85,1.25,2.1,1.4])
    supplement.p('Risk differences compare success probabilities. Raw Fisher p-values and exact method flags are retained in risk_differences.csv. The intervals are pointwise; the Holm column belongs to the jointly corrected twelve-test family. All twelve comparisons are disclosed, including nonsignificant results.')
    supplement.h('S4.1 Reproduction and provenance')
    supplement.p('The run_paper_v2.ps1 entry point resumes calibration and validation, performs the raw audit, runs base R, builds the paper/supplement/presentation, and writes verification records. Reproduction from saved data uses its analysis-only mode. The original report inputs are hash-checked separately. Source configurations, trace hashes, freeze records and analysis inputs identify the delivered version. Checkpoints and local runtimes remain excluded from Git.')
    supplement.p('All scientific graphs are exported in high-resolution PNG and vector PDF. Numerical slide charts remain editable. The local exact phrase-overlap screen covers cited public papers only; it is not an institutional similarity score or a semantic/code/AI-authorship detector. Bibliographic titles and attributed standard formulas are distinguished from original experiment data and prose. No worldwide-first claim is made.')
    supplement.save('supplement.pdf',4)
    (OUT/'abstract.md').write_text(abstract+'\n',encoding='utf-8',newline='\n')
    finding=dict(primary_holm_significant=len(significant),primary_tests=12,calibration_events=total_events,calibration_stability_events=stable_events,
                 original_split_8000=[{'k':int(r['k']),'successes':int(r['successes']),'n':30,'ci_low':float(r['ci_low']),'ci_high':float(r['ci_high'])} for r in original8],best_candidate=best_model['distribution'])
    (OUT/'findings.json').write_text(json.dumps(finding,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'paper_pages':8,'supplement_pages':4,'primary_tests':12,'holm_significant':len(significant)}))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',default=None)
    args=parser.parse_args()
    if args.output:OUT=Path(args.output).resolve()
    build()
