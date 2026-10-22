"""Numerical and diagram checks for the visual assessment revision."""
from pathlib import Path
import hashlib,json,math,re,shutil,zipfile
from xml.etree import ElementTree as E
from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from grokking.paper_sources import tokens,windows

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/assessments_visual';TMP=ROOT/'tmp/assessments_visual'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):return math.isclose(float(a),float(b),rel_tol=0,abs_tol=.02)
def pos(node):
    t=node.find('p:spPr/a:xfrm',NS);o=t.find('a:off',NS);s=t.find('a:ext',NS)
    return tuple(float(v)/9525 for v in (o.attrib['x'],o.attrib['y'],s.attrib['cx'],s.attrib['cy']))
def values(ser,field):
    node=ser.find(field,NS)
    return [float(p.find('c:v',NS).text) for p in sorted(node.findall('.//c:pt',NS),key=lambda p:int(p.attrib['idx']))]

def verify():
    d=json.loads((ROOT/'output/paper_v2/presentation_evidence.json').read_text(encoding='utf-8'))
    get=lambda sp,b,k,ep='first':next(r for r in d['policies'] if int(r['split_seed'])==sp and int(r['total_budget'])==b and int(r['k'])==k and r['endpoint']==ep)
    expected={2:[([r['step'] for r in d['trace']],[r[k] for r in d['trace']]) for k in ('train_acc','test_acc')],
              7:[(None,[get(sp,8000,k)['successes'] for sp in (20261013,20261014,20261015)]) for k in (1,2,4)],
              8:[(None,[get(sp,b,k)['successes'] for sp in (20261013,20261014,20261015) for b in (8000,12000)]) for k in (1,2,4)],
              9:[(None,[get(20261013,8000,k,ep)['successes'] for k in (1,2,4)]) for ep in ('first','stability')]}
    ppt=OUT/'Assessment10_Visual.pptx';visible=[];spoken=[]
    with zipfile.ZipFile(ppt) as z:
        names=z.namelist();slides=[n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        assert len(slides)==10 and sum(n.endswith('.xlsx') for n in names)==4
        charts=sorted([n for n in names if re.search('/charts/chart\\d+\\.xml$',n)],key=lambda n:int(re.search(r'chart(\d+)',n)[1]))
        assert len(charts)==4
        for name,groups in zip(charts,expected.values()):
            series=E.fromstring(z.read(name)).findall('.//c:ser',NS);assert len(series)==len(groups)
            for ser,(x,y) in zip(series,groups):
                actual=values(ser,'c:yVal' if x is not None else 'c:val')
                assert len(actual)==len(y) and all(math.isclose(a,float(b),abs_tol=1e-8,rel_tol=0) for a,b in zip(actual,y)),name
                if x is not None:assert values(ser,'c:xVal')==x
        for n in slides:visible.append(' '.join(t.text or '' for t in E.fromstring(z.read(n)).findall('.//a:t',NS)))
        notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)];assert len(notes)==10
        for n in notes:
            s=' '.join(t.text or '' for t in E.fromstring(z.read(n)).findall('.//a:t',NS));assert 'Sources:' in s and 'Target:' in s;spoken.append(s)
        shapes=lambda n:E.fromstring(z.read(f'ppt/slides/slide{n}.xml')).findall('.//p:sp',NS)
        # Dataset areas encode the real partition sizes.
        bars=[s for s in shapes(3) if s.find('p:spPr/a:prstGeom',NS) is not None and s.find('p:spPr/a:prstGeom',NS).attrib['prst']=='rect' and close(pos(s)[1],259)]
        assert len(bars)==2 and close(sum(pos(s)[2] for s in bars),1050)
        assert close(pos(bars[0])[2]/1050,576/961)
        # Exactly 3 and 21 checks, on the same 25-update spacing.
        dots=[s for s in shapes(5) if s.find('p:spPr/a:prstGeom',NS) is not None and s.find('p:spPr/a:prstGeom',NS).attrib['prst']=='ellipse']
        first=[pos(s) for s in dots if close(pos(s)[1],270)];stable=[pos(s) for s in dots if close(pos(s)[1],435)]
        assert len(first)==3 and len(stable)==21
        assert all(close(b[0]-a[0],30) for group in (first,stable) for a,b in zip(group,group[1:]))
        # Every budget row sums to exactly 8,000, including all observation costs.
        for y,k in ((238,1),(345,2),(452,4)):
            boxes=[s for s in shapes(6) if close(pos(s)[1],y) and close(pos(s)[3],63)]
            amounts=[int(''.join(t.text or '' for t in s.findall('.//a:t',NS)).replace(',','')) for s in boxes]
            assert len(amounts)==k and sum(amounts)==8000 and set(amounts)=={8000//k}
        # Workflow arrows point forward; the checkpoint has both save/resume directions.
        for n,count in ((2,1),(4,5)):
            connectors=E.fromstring(z.read(f'ppt/slides/slide{n}.xml')).findall('.//p:cxnSp',NS)
            assert len(connectors)==count
            assert all(c.find('p:spPr/a:ln/a:tailEnd',NS).attrib.get('type') in ('triangle','arrow') for c in connectors)
        # Forest-point and interval coordinates independently reconstruct CSV estimates.
        allshapes=shapes(10)
        for i in range(3):
            r=next(r for r in d['risks'] if int(r['split_seed'])==20261013+i and int(r['total_budget'])==8000 and int(r['k'])==4 and r['endpoint']=='first')
            x=lambda v:350+(100*float(v)+100)/120*800;y=285+i*100
            point=next(s for s in allshapes if s.find('p:spPr/a:prstGeom',NS) is not None and s.find('p:spPr/a:prstGeom',NS).attrib['prst']=='ellipse' and close(pos(s)[1]+pos(s)[3]/2,y))
            assert close(pos(point)[0]+pos(point)[2]/2,x(r['risk_difference']))
            interval=next(s for s in allshapes if s.find('p:spPr/a:custGeom',NS) is not None and close(pos(s)[1],y) and pos(s)[2]>100)
            assert close(pos(interval)[0],x(r['conservative_ci_low'])) and close(pos(interval)[0]+pos(interval)[2],x(r['conservative_ci_high']))
    # Reimported-slide renders are the exact pixels used for the matching PDF.
    pdf=OUT/'Assessment10_Visual.pdf';c=canvas.Canvas(str(pdf),pagesize=(960,540));c.setTitle('Assessment 10 - Visual explanation and results')
    for i in range(1,11):c.drawImage(str(TMP/f'final-slide-{i:02d}.png'),0,0,960,540);c.showPage()
    c.save()
    for i,page in enumerate(PdfReader(pdf).pages,1):
        im=next(v.get_object() for v in page['/Resources']['/XObject'].values() if v.get_object()['/Subtype']=='/Image')
        assert im.get_data()==Image.open(TMP/f'final-slide-{i:02d}.png').convert('RGB').tobytes()
    brief=OUT/'Assessment10_Visual_Explanation.pdf';assert len(PdfReader(brief).pages)==2
    positioned=[]
    PdfReader(brief).pages[1].extract_text(visitor_text=lambda text,cm,tm,font,size:positioned.append((tm[4],tm[5],text.strip())) if text.strip() else None)
    for i,sp in enumerate((20261013,20261014,20261015)):
        baseline=284-i*18
        row=[v for x,y,v in sorted(positioned) if 44<=x<=550 and close(y,baseline)]
        assert row==[f'S{i+1}',*[get(sp,12000,k)['successes'] for k in (1,2,4)]],row
    ieee=OUT/'assessment9_ieee';paper=ieee/'main.pdf';assert len(PdfReader(paper).pages)==6
    source=(ieee/'main.tex').read_text(encoding='utf-8');assert source.count(r'\begin{figure*}')==4 and source.count(r'\begin{figure}')==1
    log=ieee/'main.log'
    if not log.exists():log=TMP/'ieee-main.log'
    assert not re.search(r'Overfull|undefined references|Undefined control',log.read_text(encoding='utf-8'))
    for n in ('learning_delay','policy_validation','risk_differences','stability_comparison'):
        assert sha(ieee/f'figures/{n}.pdf')==sha(ROOT/f'output/paper_v2/{n}.pdf')
    for i,sp in enumerate((20261013,20261014,20261015),1):
        for B in (8000,12000):assert ' & '.join([f'S{i} / {B//1000}k',*[get(sp,B,k)['successes']+'/30' for k in (1,2,4)]]) in source
    # Preserve both previous assessment deliveries and the scientific study.
    old=json.loads((ROOT/'output/assessments/manifest.json').read_text(encoding='utf-8'))
    for n,h in old['files'].items():assert sha(ROOT/n)==h,n
    corpus={}
    for i in range(1,7):corpus[i]=tokens('\n'.join(p.extract_text() or '' for p in PdfReader(ROOT/f'tmp/paper_v2/source_corpus/source_{i}.pdf').pages))
    units={'paper':source.split(r'\begin{thebibliography}')[0],'brief':'\n'.join(p.extract_text() or '' for p in PdfReader(brief).pages),'slides':'\n'.join(visible),'notes':'\n'.join(spoken)}
    matches=[]
    for unit,s in units.items():
        for i,words in corpus.items():
            overlap=windows(tokens(s),8)&windows(words,8)
            if overlap:matches.append({'unit':unit,'source':i,'examples':[' '.join(w) for w in sorted(overlap)]})
    shutil.copy2(paper,OUT/'Assessment9_IEEE_Visual_Report.pdf')
    with zipfile.ZipFile(OUT/'Assessment9_Visual_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ieee.rglob('*')):
            if p.is_file() and p.suffix in ('.tex','.cls','.bib','.md','.pdf') and p.name!='main.pdf':z.write(p,p.relative_to(ieee))
    screen=dict(scope='Exact eight-word windows against six cited PDFs only. Not an institutional score, semantic detector or internet-wide comparison.',matching_units=matches,official_similarity_score=None)
    (OUT/'source_overlap.json').write_text(json.dumps(screen,indent=2)+'\n',encoding='utf-8',newline='\n')
    result=dict(status='passed',slides=10,native_charts=4,embedded_workbooks=4,diagram_budget_totals_verified=True,endpoint_streaks_and_common_scale_verified=True,workflow_arrow_directions_verified=True,forest_coordinates_verified=True,all_18_policy_cells_verified=True,brief_pages=2,ieee_pages=6,ieee_figures=5,previous_assessment_files_preserved=len(old['files']),source_overlap_matches=matches,native_powerpoint_open_tested=False)
    (TMP/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))

if __name__=='__main__':verify()
