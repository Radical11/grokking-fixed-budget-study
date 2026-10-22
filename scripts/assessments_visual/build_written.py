"""Visual assessment brief and a concise IEEE paper with an explicit workflow figure."""
from pathlib import Path
import csv,json,re,shutil,math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.lib.utils import simpleSplit

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/assessments_visual';SOURCE=ROOT/'output/paper_v2'
BLUE=HexColor('#175F96');INK=HexColor('#172B3A');GREY=HexColor('#637E8E');PALE=HexColor('#EAF1F7')
DATA=json.loads((SOURCE/'presentation_evidence.json').read_text(encoding='utf-8'))
AUTHORS=json.loads((ROOT/'configs/submission_authors.json').read_text(encoding='utf-8'))['authors']

def text(c,s,x,y,size=10,bold=False,color=INK,width=None,center=False):
    c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);c.setFillColor(color)
    lines=simpleSplit(s,'Helvetica-Bold' if bold else 'Helvetica',size,width) if width else s.split('\n')
    for i,line in enumerate(lines):
        if center:c.drawCentredString(x,y-i*(size+3),line)
        else:c.drawString(x,y-i*(size+3),line)

def node(c,s,x,y,w,h,size=10,fill=PALE):
    c.setFillColor(fill);c.setStrokeColor(BLUE);c.setLineWidth(.8);c.rect(x,y,w,h,fill=1)
    lines=s.split('\n')
    for i,line in enumerate(lines):text(c,line,x+w/2,y+h/2+(len(lines)-1)*(size+2)/2-i*(size+2)-size*.32,size,color=white if fill==BLUE else INK,center=True)

def arrow(c,x1,y1,x2,y2):
    c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(1);c.line(x1,y1,x2,y2)
    angle=math.atan2(y2-y1,x2-x1);p=c.beginPath();p.moveTo(x2,y2)
    for a in (angle+2.65,angle-2.65):p.lineTo(x2+5*math.cos(a),y2+5*math.sin(a))
    p.close();c.drawPath(p,stroke=0,fill=1)

def footer(c,n):
    text(c,'Assessment 10 / Visual explanation and measured results',46,24,8,color=GREY);text(c,str(n),543,24,8,color=GREY)

def workflow(path):
    c=canvas.Canvas(str(path),pagesize=(244,112));c.setTitle('Experimental workflow')
    labels=['Pairs + labels','Train + check','CSV traces','Paper + slides','R statistics','Run summaries']
    positions=[(3,65),(86,65),(169,65),(3,12),(86,12),(169,12)]
    for label,(x,y) in zip(labels,positions):node(c,label,x,y,72,29,9)
    arrow(c,75,79.5,86,79.5);arrow(c,158,79.5,169,79.5);arrow(c,205,65,205,41);arrow(c,169,26.5,158,26.5);arrow(c,86,26.5,75,26.5)
    text(c,'Python training',76,101,8,color=GREY,center=True);text(c,'R analysis and reporting',114,2,8,color=GREY,center=True)
    c.save()

def brief():
    OUT.mkdir(parents=True,exist_ok=True);c=canvas.Canvas(str(OUT/'Assessment10_Visual_Explanation.pdf'),pagesize=(595.28,841.89))
    c.setTitle('Assessment 10 - Visual explanation and results')
    text(c,'Grokking Under a Fixed Budget',46,805,20,True)
    c.setAuthor('; '.join(a['name'] for a in AUTHORS))
    for i,author in enumerate(AUTHORS):
        text(c,author['name'],46+i*168,779,9.5,True)
        text(c,author['registration_number'],46+i*168,765,9,color=GREY)
    text(c,'1. The task and dataset',46,739,13,True)
    node(c,'30 + 4 = 34',46,681,168,35,12);node(c,'34 mod 31 = 3',328,681,221,35,12);arrow(c,214,698.5,328,698.5)
    text(c,'Modulo keeps the remainder',270,663,9,color=GREY,center=True)
    w=503;train=w*576/961;node(c,'576 practice pairs',46,612,train,29,11,BLUE);node(c,'385 held-out pairs',46+train,612,w-train,29,11)
    text(c,'961 pairs. Three fixed splits. Independent starting seeds.',46,591,10)
    text(c,'2. How the code works',46,556,13,True)
    labels=['Python\npairs + labels','Train\nsmall model','CSV files\n25-step checks','R\nstatistics','Outputs\ngraphs + paper']
    for i,s in enumerate(labels):
        x=46+i*105;node(c,s,x,499,83,37,9)
        if i<4:arrow(c,x+83,517.5,x+105,517.5)
    text(c,'Checkpoint saves: weights, optimizer and random state.',46,480,9.5,color=GREY)
    text(c,'3. Grokking: practice improves before new-question accuracy',46,451,12,True)
    x0,y0,pw,ph=78,289,456,125
    for tick in (0,.5,1):
        c.setStrokeColor(HexColor('#DFE6EC'));c.setLineWidth(.5);c.line(x0,y0+tick*ph,x0+pw,y0+tick*ph);text(c,f'{tick*100:.0f}%',49,y0+tick*ph-3,8)
    for k,color,label in [('train_acc',BLUE,'Practice'),('test_acc',GREY,'Held-out')]:
        c.setStrokeColor(color);c.setLineWidth(1.3);p=c.beginPath()
        for i,r in enumerate(DATA['trace']):
            x=x0+pw*r['step']/7000;y=y0+ph*r[k]
            if i==0:p.moveTo(x,y)
            else:p.lineTo(x,y)
        c.drawPath(p)
    for i,(label,color) in enumerate([('Practice',BLUE),('Held-out',GREY)]):
        c.setStrokeColor(color);c.line(345+i*90,430,365+i*90,430);text(c,label,370+i*90,427,9)
    for tick in (0,2000,4000,6000,7000):text(c,str(tick),x0+pw*tick/7000,y0-14,8,center=True)
    text(c,'Training updates',x0+pw/2,260,9,center=True)
    text(c,'S1 calibration (n=30): mean 5,347; median 4,375; SD 4,610 updates.',46,237,9.5)
    text(c,'4. Two success rules',46,207,13,True)
    text(c,'Every check: practice >=99% and held-out >=95%.',46,188,10,color=BLUE)
    text(c,'First: 3 checks',46,157,10,True)
    for j in range(3):
        c.setFillColor(BLUE);c.circle(230+14.5*j,161,3,fill=1,stroke=0)
    text(c,'50-update span',310,157,10)
    text(c,'Window: 21 checks',46,123,10,True)
    for j in range(21):c.setFillColor(BLUE);c.circle(230+14.5*j,127,2.3,fill=1,stroke=0)
    text(c,'500-update span',310,106,9)
    text(c,'Spans start at the first good check. Count the last check inside B/k.',46,83,9.5)
    text(c,'U=min(T,C): capped time; eventual unfinished T stays unknown.',46,65,9.5)
    text(c,'Chance of >=1 success: 1 - [1 - F(B/k)]^k',46,45,10,True,color=BLUE)
    text(c,'F(t): one-run completion chance.',340,45,8.5,color=GREY)
    footer(c,1);c.showPage()
    text(c,'Results and the decision',46,805,20,True)
    text(c,'Binary attempts. Exact intervals. Twelve Fisher tests with Holm correction.',46,784,9.5,color=GREY)
    text(c,'5. Same total budget: B = 8,000 updates',46,755,13,True)
    for k,y in ((1,711),(2,674),(4,637)):
        text(c,f'{k} run'+('s' if k>1 else ''),46,y+8,11,True)
        gap=5;w=(383-(k-1)*gap)/k
        for j in range(k):node(c,f'{8000//k:,}',166+j*(w+gap),y,w,25,11,BLUE if k==1 else PALE)
    text(c,'Each segment is a fresh start. All allocated updates execute.',46,621,9.5,color=GREY)
    text(c,'6. Fresh successes at the 8,000-update budget',46,593,13,True)
    colors=[BLUE,GREY,HexColor('#253F50')]
    for i,(label,color) in enumerate(zip(('1 run','2 runs','4 runs'),colors)):
        c.setFillColor(color);c.rect(157+i*112,570,10,8,fill=1,stroke=0);text(c,label,172+i*112,569,9)
    x0,y0,pw,ph=80,402,454,148
    for tick in (0,10,20,30):
        c.setStrokeColor(HexColor('#DFE6EC'));c.setLineWidth(.5);c.line(x0,y0+ph*tick/30,x0+pw,y0+ph*tick/30);text(c,str(tick),59,y0+ph*tick/30-3,8.5)
    for i,sp in enumerate((20261013,20261014,20261015)):
        for j,k in enumerate((1,2,4)):
            r=next(r for r in DATA['policies'] if int(r['split_seed'])==sp and int(r['total_budget'])==8000 and int(r['k'])==k and r['endpoint']=='first');n=int(r['successes']);x=x0+22+i*151+j*31
            c.setFillColor(colors[j]);c.rect(x,y0,24,ph*n/30,fill=1,stroke=0);text(c,str(n),x+12,y0+ph*n/30+4,9.5,True,center=True)
        text(c,f'Split {i+1}',x0+65+i*151,y0-17,9.5,center=True)
    text(c,'Each bar: successes out of 30 independent attempts.',46,369,9.5)
    text(c,'All three 4-versus-1 differences survive Holm correction.',46,352,10,True,color=BLUE)
    text(c,'7. Results at 12,000 updates (out of 30)',46,325,13,True)
    for j,label in enumerate(('Split','1 run','2 runs','4 runs')):text(c,label,51+j*126,305,10,True,color=BLUE)
    for i,sp in enumerate((20261013,20261014,20261015)):
        row=[f'S{i+1}',*[next(r['successes'] for r in DATA['policies'] if int(r['split_seed'])==sp and int(r['total_budget'])==12000 and int(r['k'])==k and r['endpoint']=='first') for k in (1,2,4)]]
        for j,v in enumerate(row):text(c,v,51+j*126,284-i*18,10)
    text(c,'12k: only S2 detects a 4-vs-1 difference. Two-run results are inconclusive.',46,224,9.5)
    text(c,'Example uncertainty: 28/30 = 93.3%; exact 95% interval 77.9%-99.2%.',46,207,9.5,color=GREY)
    text(c,'8. Brief confirmation versus a longer window',46,182,12,True)
    text(c,'S1, 8k, four starts',46,163,9,color=GREY)
    for label,n,y,color in [('First',12,137,BLUE),('500-window',4,114,GREY)]:
        text(c,label,46,y+4,9.5);c.setFillColor(color);c.rect(157,y,n/30*310,14,fill=1,stroke=0);text(c,f'{n}/30',163+n/30*310,y+3,10,True)
    text(c,'Decision: one long run was more reliable at 8k.',46,87,13,True,color=BLUE)
    text(c,'Scope: one task, one model, three splits. Later accuracy can still fall.',46,67,9.5)
    text(c,'Next: other tasks, more splits and longer accuracy windows.',46,51,9.5)
    text(c,'Sources: Power et al. (2022); Streeter et al. (2007). Full references: Assessment 9.',46,36,8,color=GREY)
    footer(c,2);c.save()

def ieee():
    dest=OUT/'assessment9_ieee';dest.mkdir(parents=True,exist_ok=True)
    old=ROOT/'output/assessments/assessment9_ieee'
    for name in ('IEEEtran.cls','references.bib','TEMPLATE_SOURCE.md'):shutil.copy2(old/name,dest/name)
    template_record=dest/'TEMPLATE_SOURCE.md'
    template_record.write_text(template_record.read_text(encoding='utf-8').replace('Replace author and affiliation placeholders before submission.','The current author names and registration numbers come from configs/submission_authors.json. No affiliation has been asserted.'),encoding='utf-8',newline='\n')
    (dest/'figures').mkdir(exist_ok=True)
    for p in (old/'figures').glob('*.pdf'):shutil.copy2(p,dest/'figures'/p.name)
    workflow(dest/'figures/workflow.pdf')
    s=(old/'main.tex').read_text(encoding='utf-8')
    author_start=s.index(r'\author{')
    author_end=s.index(r'\begin{document}',author_start)
    author_blocks=[r'\IEEEauthorblockN{'+a['name']+'}\n'+r'\IEEEauthorblockA{'+a['registration_number']+'}' for a in AUTHORS]
    s=s[:author_start]+'\\author{\n'+('\n\\and\n'.join(author_blocks))+'\n}\n'+s[author_end:]
    s=s.replace(r'\usepackage[hidelinks]{hyperref}',r'\usepackage[hidelinks]{hyperref}'+'\n'+r'\hypersetup{pdfauthor={'+', '.join(a['name'] for a in AUTHORS)+'}}')
    abstract='''Grokking is delayed improvement on held-out examples after strong training performance. We study completion-time variation in a fixed small transformer learning addition modulo 31, then compare one long run with two or four independent starts at total budgets of 8,000 or 12,000 updates. There are 90 calibration observations across three fixed dataset splits, including 20 reused runs, and 540 fresh policy attempts. Primary success requires three accuracy checks; a secondary endpoint requires a 500-update window. At 8,000 updates, one run succeeds 28/30 times on every split; four starts succeed 12/30, 9/30 and 11/30. All three contrasts survive Holm correction. At 12,000, only the second-split four-versus-one contrast is detected. No two-run contrast is detected. Four of twelve planned tests are significant. We report uncertainty and keep unfinished event times unknown. The proposed empirical contribution links completion curves, equal-budget allocation and finite stability, conditional on this task and model.'''
    s=re.sub(r'(?s)(\\begin\{abstract\}).*?(\\end\{abstract\})',lambda m:m[1]+'\n'+abstract+'\n'+m[2],s,count=1)
    def paragraph_after(section,replacement):
        nonlocal s
        token=section+'\n\n';start=s.index(token)+len(token);end=s.index('\n\n',start);s=s[:start]+replacement+s[end:]
    paragraph_after(r'\section{Introduction and objectives}',r'''Grokking is delayed improvement on held-out examples after strong training performance \cite{ref1}. We study its timing across random initializations and ask how to allocate a fixed training budget. The objectives are:
\begin{itemize}
\item characterize completion-time variability;
\item estimate success before a training limit;
\item compare one long run with independent shorter starts.
\end{itemize}''')
    paragraph_after(r'\section{Experimental design}',r'''All 961 ordered pairs $a,b\in\{0,\ldots,30\}$ have label $(a+b)\bmod31$; for example, $(30+4)\bmod31=3$. The baseline has 576 practice and 385 held-out pairs. A fixed causal transformer \cite{ref6} has 36,992 parameters: one attention block, width 64, four heads and a 128-unit ReLU layer, without biases, dropout or layer normalization. Full-batch AdamW \cite{ref5} uses learning rate 0.003, betas (0.9,0.98) and weight decay 1.''')
    oldpara=next(b for b in s.split('\n\n') if b.startswith('Split seeds are '))
    s=s.replace(oldpara,r'''Split seeds 20261013--20261015 each have 30 calibration runs capped at $C=30,000$. Validation uses 30 fresh independent attempts in each split/budget/policy cell. For $k=1,2,4$, each constituent receives $B/k$ updates and all allocated updates execute. An attempt succeeds if any constituent qualifies. Seeds are disjoint between calibration and validation; model predictions are not averaged.''')
    oldpara=next(b for b in s.split('\n\n') if b.startswith('An update is one learning step;'))
    s=s.replace(oldpara,r'''Each update uses all practice pairs. Evaluate every 25 updates, with update zero excluded from qualifying streaks. Both thresholds must hold: practice accuracy $\geq99\%$ and held-out accuracy $\geq95\%$. Memorization time requires three practice-only checks. Primary $T$ uses three joint checks; secondary $T_{500}$ uses 21, spanning 500 updates. Both record the final check and neither guarantees permanent generalization.''')
    oldpara=next(b for b in s.split('\n\n') if b.startswith('The budgets were chosen using '))
    s=s.replace(oldpara,r'''The 8,000- and 12,000-update budgets were chosen from the original 20 baseline traces after every old policy succeeded 10/10 at 30,000. This data-informed choice is disclosed. Protocol and full seeds were committed before new training; calibration predictions were frozen before validation. Budgets, settings and sample sizes were not retuned after viewing outcomes.''')
    insertion=r'''\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{figures/workflow.pdf}
\caption{Recorded experimental workflow. Python trains and saves evaluation histories; R analyzes run and policy outcomes. Checkpoints support resumption. Numerical records remain separate from the reports.}
\label{fig:workflow}
\end{figure}'''
    s=s.replace(r'\section{Experimental design}',r'\section{Experimental design}'+'\n\n'+insertion,1)
    s=s.replace('Figure 3 uses conservative pointwise intervals',r'Fig.~\ref{fig:risk_differences} uses conservative pointwise intervals')
    (dest/'main.tex').write_text(s,encoding='utf-8',newline='\n')

if __name__=='__main__':brief();ieee()
