"""Create matching slide PDF and verify assessment results against recorded evidence."""
from pathlib import Path
import csv,hashlib,json,math,re,shutil,zipfile
from xml.etree import ElementTree as ET
from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from grokking.paper_sources import tokens,windows

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/assessments';BUILD=ROOT/'tmp/assessments'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    final=OUT/'assessment10_final';ieee=OUT/'assessment9_ieee'
    ppt=final/'Assessment10_Final.pptx';pdf=final/'Assessment10_Final.pdf'
    c=canvas.Canvas(str(pdf),pagesize=(960,540));c.setTitle('Assessment 10 - Final project results')
    for i in range(1,11):c.drawImage(str(BUILD/f'final-slide-{i:02d}.png'),0,0,960,540);c.showPage()
    c.save()
    assert len(PdfReader(ieee/'main.pdf').pages)==6
    assert len(PdfReader(final/'explanation.pdf').pages)==2
    assert len(PdfReader(pdf).pages)==10
    assert all(len(p.extract_text() or '')>1000 for p in PdfReader(ieee/'main.pdf').pages)
    tex=(ieee/'main.tex').read_text(encoding='utf-8');assert r'\documentclass[conference,letterpaper]{IEEEtran}' in tex
    assert tex.count(r'\bibitem{')==7 and tex.count(r'\begin{figure*}')==4 and tex.count(r'\begin{align}')==1
    log=ieee/'main.log'
    if not log.exists():log=BUILD/'ieee-main.log'
    assert not re.search(r'Overfull|Undefined control sequence|undefined references',log.read_text(encoding='utf-8'))
    evidence=json.loads((ROOT/'output/paper_v2/presentation_evidence.json').read_text(encoding='utf-8'))
    ps=evidence['policies']
    get=lambda s,b,k:next(r for r in ps if int(r['split_seed'])==s and int(r['total_budget'])==b and int(r['k'])==k and r['endpoint']=='first')
    with zipfile.ZipFile(ppt) as z:
        names=z.namelist();slides=[n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        assert len(slides)==10
        assert len([n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)])==10
        assert len([n for n in names if n.endswith('.xlsx')])==2
        charts=sorted(n for n in names if re.search(r'/charts/chart\d+\.xml$',n))
        assert len(charts)==2
        expected=[[( [r['step'] for r in evidence['trace']], [r[k] for r in evidence['trace']]) for k in ('train_acc','test_acc')],[(None,[get(s,8000,k)['observed_probability'] for s in (20261013,20261014,20261015)]) for k in (1,2,4)]]
        for name,groups in zip(charts,expected):
            series=ET.fromstring(z.read(name)).findall('.//c:ser',NS);assert len(series)==len(groups)
            for ser,(x,y) in zip(series,groups):
                for field,values in [('c:val' if x is None else 'c:yVal',y)]+([] if x is None else [('c:xVal',x)]):
                    pts=ser.find(field,NS).findall('.//c:pt',NS)
                    actual=[float(p.find('c:v',NS).text) for p in sorted(pts,key=lambda p:int(p.attrib['idx']))]
                    assert len(actual)==len(values) and all(math.isclose(a,float(b),abs_tol=1e-8,rel_tol=0) for a,b in zip(actual,values)),name
        table=ET.fromstring(z.read('ppt/slides/slide8.xml')).find('.//a:tbl',NS)
        rows=[[''.join(t.text or '' for t in cell.findall('.//a:t',NS)) for cell in row.findall('a:tc',NS)] for row in table.findall('a:tr',NS)]
        expected_rows=[['Split / total steps','One run','Two runs','Four runs']]
        for i,s in enumerate((20261013,20261014,20261015),1):
            for b in (8000,12000):
                counts=[get(s,b,k)['successes']+'/30' for k in (1,2,4)]
                expected_rows.append([f'S{i} / {b:,}',*counts])
                assert ' & '.join([f'S{i} / {b//1000}k',*counts]) in tex
                brief=(final/'explanation.md').read_text(encoding='utf-8')
                assert '| '+f'S{i} / {b:,}'+' | '+' | '.join(counts)+' |' in brief
        assert rows==expected_rows
        visible='\n'.join(' '.join(t.text or '' for t in ET.fromstring(z.read(n)).findall('.//a:t',NS)) for n in slides)
    for i,page in enumerate(PdfReader(pdf).pages,1):
        images=[x.get_object() for x in page['/Resources']['/XObject'].values() if x.get_object()['/Subtype']=='/Image']
        assert len(images)==1 and images[0].get_data()==Image.open(BUILD/f'final-slide-{i:02d}.png').convert('RGB').tobytes()
    units={'ieee_body':tex.split(r'\begin{thebibliography}')[0],'brief':brief.split('References:')[0],'slides':visible,'notes':(final/'speaker_notes.md').read_text(encoding='utf-8')}
    matches=[]
    for i in range(1,7):
        source=ROOT/f'tmp/paper_v2/source_corpus/source_{i}.pdf';words=tokens('\n'.join(p.extract_text() or '' for p in PdfReader(source).pages))
        for name,text in units.items():
            # Remove cited bibliography titles from notes/visible reference text.
            for r in evidence.get('references',[]):text=text.replace(r['title'],'')
            a=windows(tokens(text),8)&windows(words,8);b=windows(tokens(text),12)&windows(words,12)
            if a or b:matches.append({'unit':name,'source':i,'eight_word':len(a),'twelve_word':len(b),'examples':[' '.join(x) for x in sorted(a)[:8]]})
    screen=dict(scope='Exact normalized eight-word and twelve-word windows against six cited PDFs only. No institutional or internet-wide score; standard formulas and attributed technical language need context.',matching_units=matches,official_similarity_score=None)
    (OUT/'source_overlap.json').write_text(json.dumps(screen,indent=2)+'\n',encoding='utf-8',newline='\n')
    shutil.copy2(ieee/'main.pdf',OUT/'Assessment9_IEEE_Report.pdf')
    with zipfile.ZipFile(OUT/'Assessment9_LaTeX_Source.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ieee.rglob('*')):
            if p.is_file() and p.suffix in ('.tex','.cls','.bib','.md','.pdf') and p.name!='main.pdf':z.write(p,p.relative_to(ieee))
    result=dict(status='passed',ieee_pages=6,brief_pages=2,slides=10,slide_pdf_pages=10,native_charts=2,native_tables=1,embedded_workbooks=2,all_18_policy_counts_verified=True,exported_chart_values_verified=True,slide_pdf_matches_reviewed_imported_pixels=True,source_overlap_matches=matches,native_powerpoint_open_tested=False,identity_fields='editable placeholders')
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))

if __name__=='__main__':main()
