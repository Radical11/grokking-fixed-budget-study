"""Build assessment-specific manuscripts from the immutable completed-study outputs."""
from pathlib import Path
import csv, hashlib, html, json, re, shutil, urllib.request
from grokking import paper_typesetting

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/assessments'
IEEE=OUT/'assessment9_ieee'
SHORT=OUT/'assessment10_final'
SOURCE=ROOT/'output/paper_v2'

def load(name):
    with (SOURCE/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def tex(s):
    s=html.unescape(re.sub(r'<[^>]+>',' ',s)).replace('**','')
    chars={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
    return ''.join(chars.get(c,c) for c in s).replace(r'T\_500',r'$T_{500}$')

def build_ieee():
    IEEE.mkdir(parents=True,exist_ok=True);fig=IEEE/'figures';fig.mkdir(exist_ok=True)
    url='https://mirrors.ctan.org/macros/latex/contrib/IEEEtran/IEEEtran.cls'
    cls=IEEE/'IEEEtran.cls'
    if not cls.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'Academic IEEE report preparation'})
        cls.write_bytes(urllib.request.urlopen(req,timeout=45).read())
    assert b'ProvidesClass{IEEEtran}' in cls.read_bytes()
    text=(SOURCE/'paper.md').read_text(encoding='utf-8')
    blocks=[b.strip() for b in text.split('\n\n') if b.strip()]
    abstract=blocks[blocks.index('## Abstract')+1]
    header=r'''\documentclass[conference,letterpaper]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{cite,amsmath,amssymb,graphicx,booktabs,tabularx,url}
\usepackage[hidelinks]{hyperref}
\title{Grokking Under a Fixed Budget:\\An Empirical Study of Learning Time and Independent Restarts}
\author{\IEEEauthorblockN{[Your name]}
\IEEEauthorblockA{[Registration number]\\{[Department and institution]}\\BAMAT207 Probability and Statistics}}
\begin{document}
\raggedbottom
\maketitle
\begin{abstract}
'''
    parts=[header,tex(abstract),r'\end{abstract}',r'\begin{IEEEkeywords}grokking, random variables, independent restarts, fixed training budget, generalization, statistical inference\end{IEEEkeywords}']
    i=blocks.index('## 1. Introduction and objectives')
    while i<len(blocks):
        b=blocks[i];i+=1
        if b=='## References':break
        if b=='---' or b.startswith('<!--'):continue
        if b.startswith('## '):
            title=re.sub(r'^\d+(?:\.\d+)*\.?\s*','',b[3:])
            sub=bool(re.match(r'## \d+\.\d+',b))
            parts.append(('\\subsection' if sub else '\\section')+'{'+tex(title)+'}')
        elif b.startswith('!['):
            name=re.search(r'\]\(([^)]+)\.png\)',b).group(1)
            shutil.copy2(SOURCE/(name+'.pdf'),fig/(name+'.pdf'))
            caption=blocks[i+1] if blocks[i].startswith('<!--') else blocks[i]
            i+=2 if blocks[i].startswith('<!--') else 1
            caption=re.sub(r'^Figure \d+\.\s*','',caption)
            parts.extend([r'\begin{figure*}[!t]',r'\centering',r'\includegraphics[width=.90\textwidth]{figures/'+name+'.pdf}',r'\caption{'+tex(caption)+'}',r'\label{fig:'+name+'}',r'\end{figure*}'])
        elif b.startswith('| '):
            rows=[[c.strip() for c in line.strip().strip('|').split('|')] for line in b.splitlines() if not re.match(r'^\|\s*---',line)]
            if rows[0][0]=='Split / B':
                ps=load('policy_statistics.csv');new=[['Split / B','1 run','2 runs','4 runs','2 minus 1','4 minus 1','Holm p: 2 / 4']]
                for row in rows[1:]:
                    match=re.fullmatch(r'S(\d) / (\d+)k',row[0]);split=20261012+int(match[1]);budget=int(match[2])*1000
                    counts=[next(r['successes']+'/30' for r in ps if int(r['split_seed'])==split and int(r['total_budget'])==budget and int(r['k'])==k and r['endpoint']=='first') for k in (1,2,4)]
                    new.append([row[0],*counts,*row[1:]])
                rows=new
            cols=len(rows[0]);wide=cols>=5 or rows[0][0]=='Cohort';kind='table*' if wide else 'table'
            width=r'\textwidth' if wide else r'\columnwidth'
            captions={'Cohort':'Experimental cohorts and observation units.','Split':'Calibration outcomes at the 30,000-update cap.','Split / B':'Fresh successes out of 30, probability differences in percentage points, and Holm-adjusted p-values.','Data fraction':'Original 120-run exploratory setting study.','Candidate':'Timing-family comparison on the expanded original-split calibration sample.'}
            parts.extend(['\\begin{'+kind+'}[!t]',r'\caption{'+tex(captions.get(rows[0][0],'Recorded study results.'))+'}',r'\centering\footnotesize',r'\begin{tabularx}{'+width+'}{'+'X'*cols+'}',r'\toprule',' & '.join(tex(c) for c in rows[0])+r'\\',r'\midrule'])
            parts.extend(' & '.join(tex(c) for c in row)+r'\\' for row in rows[1:])
            parts.extend([r'\bottomrule',r'\end{tabularx}','\\end{'+kind+'}'])
        else:
            if b.startswith('An update is one learning step;'):
                parts.extend([tex(b),r'''Let $Q_j$ be one when both accuracy thresholds hold at update $25j$, and zero otherwise. The two recorded endpoints are
\begin{align}
T&=25\min\{j\geq3:Q_{j-2}=Q_{j-1}=Q_j=1\},\\
T_{500}&=25\min\{j\geq21:Q_{j-20}=\cdots=Q_j=1\}.
\end{align}
If no qualifying streak finishes by $C$, its event time remains unknown. The fully observed capped outcome is $U=\min(T,C)$.'''])
            elif b.startswith('For k independent runs,'):
                parts.extend([r'''For a fixed split, let $F(t)=P(T\leq t)$. With $n=30$ calibration runs, estimate it by
\begin{equation}
\widehat F(t)=\frac{1}{n}\sum_{i=1}^{n}\mathbf{1}\{T_i\leq t\}.
\end{equation}
Unfinished runs contribute no event before the cap and remain in the denominator. Conditional on the same task and numerical settings, independent initializations give
\begin{equation}
P(\text{at least one success})=1-[1-F(B/k)]^k.
\end{equation}
Each validation attempt has a Bernoulli success indicator; its cell total follows a binomial sampling model. We estimate $F$ from calibration and test frozen predictions with fresh seeds. Exact binomial intervals accompany observed proportions. Independent bootstrap resampling of calibration runs and policy attempts captures both uncertainty sources when comparing prediction with observation.'''])
            else:parts.append(tex(b))
    refs=json.loads((ROOT/'paper/v2/references.json').read_text(encoding='utf-8'))
    details={1:'A. Power, Y. Burda, H. Edwards, I. Babuschkin, and V. Misra',2:'X. K. Truong, Q. H. Truong, D. T. Luu, and T. D. Phan',3:'M. Streeter, D. Golovin, and S. F. Smith',4:'Y. Ootani',5:'I. Loshchilov and F. Hutter',6:'A. Vaswani et al.',7:'BAMAT207 course specification'}
    parts.append(r'\begin{thebibliography}{7}')
    # The transformer appears before AdamW in the methods paragraph.
    # IEEE numbers references by their first citation in this manuscript.
    for r in sorted(refs,key=lambda r:{6:5,5:6}.get(r['id'],r['id'])):
        tail=(r' [Online]. Available: \url{'+r['url']+'}') if r['id']<7 else ' Official supplied syllabus, version 1, archived with the project.'
        year={1:2022,2:2026,3:2007,4:2026,5:2019,6:2017}.get(r['id'])
        parts.append(r'\bibitem{ref'+str(r['id'])+'} '+tex(details[r['id']])+', ``'+tex(r['title'])+",'' "+tex(r['status'])+(', '+str(year) if year and str(year) not in r['status'] else '')+'.'+tail)
    parts.extend([r'\end{thebibliography}',r'\end{document}'])
    # Numbered citations match the original, inspected reference order.
    source='\n\n'.join(parts)+'\n'
    source=re.sub(r'\[(\d)\]',lambda m:r'\cite{ref'+m[1]+'}',source)
    (IEEE/'main.tex').write_text(source,encoding='utf-8',newline='\n')
    shutil.copy2(ROOT/'paper/v2/references.bib',IEEE/'references.bib')
    (IEEE/'TEMPLATE_SOURCE.md').write_text('# IEEE template provenance\n\nStandard `IEEEtran` conference class, unchanged, from '+url+'\n\nIEEE guidance: https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/\n\nClass SHA256: `'+hashlib.sha256(cls.read_bytes()).hexdigest()+'`\n\nThis is a college assessment formatted with the conference class. It does not claim IEEE publication or acceptance. Replace author and affiliation placeholders before submission.\n',encoding='utf-8',newline='\n')

def build_brief():
    SHORT.mkdir(parents=True,exist_ok=True)
    policies=load('policy_statistics.csv');risk=load('risk_differences.csv')
    def get(s,b,k,ep='first'):return next(r for r in policies if int(r['split_seed'])==s and int(r['total_budget'])==b and int(r['k'])==k and r['endpoint']==ep)
    rows=['| Split / total steps | One run | Two runs | Four runs |','| --- | --- | --- | --- |']
    for si,s in enumerate((20261013,20261014,20261015),1):
        for b in (8000,12000):rows.append('| '+f'S{si} / {b:,}'+' | '+' | '.join(get(s,b,k)['successes']+'/30' for k in (1,2,4))+' |')
    content='''# Assessment 10: Final project explanation and results

Grokking Under a Fixed Budget: One Long Run or Several Restarts?

Name: [Your name] | Registration number: [Your registration number]

## 1. The problem and objective

A learning program can answer its practice questions correctly before it starts answering new questions correctly. Researchers call this delayed improvement grokking [1]. We measured how long that improvement takes across different random starts, then asked whether one long attempt or several shorter attempts is more reliable when both receive the same total training budget.

## 2. What the computer learns

The task is addition modulo 31: add two numbers and keep the remainder after division by 31. For example, (30 + 4) mod 31 = 3. There are 961 ordered input pairs. Each baseline split gives the model 576 practice pairs and holds back 385 pairs for evaluation. Three fixed splits check whether the result changes when the practice questions change.

## 3. How the code works

Python creates the pairs and correct answers, selects disjoint practice/evaluation sets and trains a small transformer with 36,992 adjustable parameters. A seed fixes the random starting weights, so an experiment can be repeated. One update is one learning step using all practice pairs. AdamW adjusts the weights; weight decay gently shrinks them and stays fixed at 1 in the follow-up. The learning rate stays at 0.003.

Every 25 updates, Python records practice and new-question accuracy in CSV traces. It saves checkpoints so interrupted runs can resume. R reads these records, computes the statistical results and creates the graphs. Unknown completion times stay unknown. The code checks labels, dataset separation, seeds and exact update totals.

## 4. What counts as success?

First confirmation T requires at least 99% practice accuracy and 95% new-question accuracy at three consecutive checks. We count the last check. A separate measure needs 21 successful checks spanning 500 updates, all inside the allocated budget. This longer window measures finite stability; later accuracy can still fall. For capped-time statistics, U=min(T,C), where C is the run limit.

## 5. The completed experiment

Calibration uses 30 full-length runs for each split: 90 observations, including 20 reused original runs and 70 new ones. Fresh validation tests budgets of 8,000 and 12,000 total updates with one, two or four runs. Each of the 18 conditions has 30 independent attempts. This gives 540 attempts containing 1,260 runs. The extension adds 1,330 training runs and 7.5 million logical updates. All runs finished without technical failure. A completed run can still miss the success criterion.

---

## 6. The probability and statistics

F(t) is the chance that one run confirms success by step t. We estimate it as the number of calibration runs confirmed by t divided by 30. If k independent starts each receive B/k steps, the probability that all fail is [1-F(B/k)]^k. Therefore, the chance that at least one succeeds is 1-[1-F(B/k)]^k [3]. Calibration predictions were frozen before fresh validation.

Each attempt gives a Bernoulli yes/no outcome; a group gives a binomial success count. Exact 95% confidence intervals describe sampling uncertainty. Twelve planned Fisher exact tests compare each restart policy with one long run. Holm correction accounts for testing twelve comparisons. Probability differences have conservative uncertainty bounds, with bootstrap resampling as a sensitivity analysis. Original setting comparisons, correlation, regression and ANOVA remain exploratory because their usual assumptions are imperfect here.

## 7. Results: successes out of 30 fresh attempts

'''+ '\n'.join(rows)+'''

At 8,000 total updates, one long run succeeds in 28/30 attempts on every split. Four shorter runs succeed in 12/30, 9/30 and 11/30. All three differences survive Holm correction. Their four-minus-one probability differences are -53.3, -63.3 and -56.7 percentage points. At 12,000 updates, only the second-split four-run comparison survives correction. No two-run comparison reaches the corrected threshold. That does not establish that the two policies are equivalent.

Uncertainty matters: 28/30 is 93.3% observed success, with an exact 95% interval of 77.9% to 99.2%. On split 1 at 8,000 updates, four runs give 12/30 first confirmations but only 4/30 confirmations of the 500-update window. The endpoint changes what “worked” means.

## 8. Conclusion, limits and future work

For this small model and these three splits, one long run is more reliable than four short runs at 8,000 total updates. Very short runs can end before delayed learning has enough time to appear. The result is conditional on the task, model and budgets. Thirty attempts cannot settle every small difference, and three splits do not represent every possible dataset. Future work can study other tasks, more splits and longer stability windows. The completed study and all recorded results already support the present conclusion.

References: [1] Power et al., “Grokking,” arXiv:2201.02177, 2022. [3] Streeter, Golovin and Smith, “Restart Schedules for Ensembles of Problem Instances,” 2007. Full references, methods and figures appear in Assessment 9 and the archived technical supplement.
'''
    (SHORT/'explanation.md').write_text(content,encoding='utf-8',newline='\n')
    def footer(canvas,doc):
        canvas.saveState();canvas.setFont('Helvetica',8)
        canvas.setFillColorRGB(.39,.48,.55)
        canvas.drawString(52,25,'Assessment 10 / Final project explanation and results')
        canvas.drawRightString(543,25,str(doc.page));canvas.restoreState()
    previous=paper_typesetting.footer
    try:
        paper_typesetting.footer=footer
        paper_typesetting.render_source(SHORT/'explanation.md',SHORT/'explanation.pdf',2)
    finally:paper_typesetting.footer=previous
    summary=dict(policy_counts=[{k:r[k] for k in ('split_seed','total_budget','k','endpoint','n','successes')} for r in policies],primary_significant=sum(r['endpoint']=='first' and float(r['p_holm'])<.05 for r in risk),source_sha256={f'output/paper_v2/{n}':hashlib.sha256((SOURCE/n).read_bytes()).hexdigest() for n in ('paper.md','policy_statistics.csv','risk_differences.csv','calibration_statistics.csv','presentation_evidence.json')})
    (OUT/'assessment_evidence.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':build_ieee();build_brief()
