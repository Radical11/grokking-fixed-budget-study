"""Verify final artifacts and optionally independently reproduce R graphs and manuscripts."""
from pathlib import Path
from xml.etree import ElementTree as ET
import argparse,hashlib,json,math,os,re,shutil,subprocess,sys,zipfile
from pypdf import PdfReader
from PIL import Image
from .paper_study import ROOT,DATA,read_csv,sha

OUT=ROOT/'output/paper_v2';TMP=ROOT/'tmp/paper_v2_presentation'
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def cache(node):return [float(p.find('c:v',NS).text) for p in sorted(node.findall('.//c:pt',NS),key=lambda p:int(p.attrib['idx']))]
def same(actual,expected,label):
    assert len(actual)==len(expected),(label,'length')
    assert all(math.isclose(a,float(b),rel_tol=0,abs_tol=1e-8) for a,b in zip(actual,expected)),label

def verify(reproduce=False):
    audit=json.loads((OUT/'audit.json').read_text());assert audit['status']=='passed'
    content=json.loads((OUT/'presentation_content.json').read_text());data=json.loads((OUT/'presentation_evidence.json').read_text())
    assert len(content['slides'])==15 and sum(s['seconds'] for s in content['slides'])==700
    assert all(s['seconds']>0 for s in content['slides'][:13]) and all(s['seconds']==0 for s in content['slides'][13:])
    policies=read_csv(OUT/'policy_statistics.csv');assert data['policies']==policies
    representative=read_csv(OUT/'representative_run.csv')[0]
    raw_trace=[{k:float(v) for k,v in r.items()} for r in read_csv(ROOT/representative['source_path']/'trace.csv') if int(r['step'])<=data['trace_end']]
    assert raw_trace==data['trace'], 'Presentation trace differs from the recorded run'
    def get(split,B,k,ep='first'):
        return next(p for p in policies if int(p['split_seed'])==split and int(p['total_budget'])==B and int(p['k'])==k and p['endpoint']==ep)
    cdf=read_csv(OUT/'completion_curves.csv');assert data['completion_curves']==cdf
    cdf_series=[]
    for split in (20261013,20261014,20261015):
        points=[(0,0)]
        for r in (r for r in cdf if int(r['split_seed'])==split and r['endpoint']=='first'):
            x,y=float(r['time']),float(r['probability'])
            if x==0:continue
            points.extend([(x,points[-1][1]),(x,y)])
        cdf_series.append(([p[0] for p in points],[p[1] for p in points]))
    orig=[get(20261013,B,k) for B in (8000,12000) for k in (1,2,4)]
    expected=[
      [([r['step'] for r in data['trace']],[r['train_acc'] for r in data['trace']]),([r['step'] for r in data['trace']],[r['test_acc'] for r in data['trace']])],
      cdf_series,
      [(None,[get(20261013,B,k)['observed_probability'] for k in (1,2,4)]) for B in (8000,12000)],
      [(None,[get(split,8000,k)['observed_probability'] for split in (20261013,20261014,20261015)]) for k in (1,2,4)],
      [(None,[p['predicted_probability'] for p in orig]),(None,[p['observed_probability'] for p in orig])],
      [(None,[p['observed_probability'] for p in orig]),(None,[get(20261013,B,k,'stability')['observed_probability'] for B in (8000,12000) for k in (1,2,4)])]]
    pptx=OUT/'presentation.pptx'
    with zipfile.ZipFile(pptx) as z:
        names=z.namelist();slides=[n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
        notes=[n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',n)]
        charts=sorted((n for n in names if re.fullmatch(r'ppt/slides/charts/chart\d+\.xml',n)),key=lambda p:int(re.search(r'chart(\d+)',p).group(1)))
        assert len(slides)==len(notes)==15 and len(charts)==6
        assert sum(n.endswith('.xlsx') for n in names)==6
        assert sum(len(ET.fromstring(z.read(n)).findall('.//a:tbl',NS)) for n in slides)==3
        expected_tables={
            8:[['Policy','8k','12k'],*[[f'{k} run'+('' if k==1 else 's'),get(20261013,8000,k)['successes']+'/30',get(20261013,12000,k)['successes']+'/30'] for k in (1,2,4)]],
            15:[['Split / budget','1 run','2 runs','4 runs'],*[[f'S{si} / {B//1000}k',*[get(split,B,k)['successes']+' / '+get(split,B,k,'stability')['successes'] for k in (1,2,4)]] for si,split in enumerate((20261013,20261014,20261015),1) for B in (8000,12000)]]}
        for slide_number,expected_rows in expected_tables.items():
            native_tables=ET.fromstring(z.read(f'ppt/slides/slide{slide_number}.xml')).findall('.//a:tbl',NS)
            assert len(native_tables)==1
            actual_rows=[[''.join(n.text or '' for n in cell.findall('.//a:t',NS)) for cell in row.findall('a:tc',NS)] for row in native_tables[0].findall('a:tr',NS)]
            assert actual_rows==expected_rows,('Native slide table differs from R results',slide_number)
        for name,series_expected in zip(charts,expected):
            series=ET.fromstring(z.read(name)).findall('.//c:ser',NS);assert len(series)==len(series_expected)
            for node,(x,y) in zip(series,series_expected):
                same(cache(node.find('c:val' if x is None else 'c:yVal',NS)),y,name)
                if x is not None:same(cache(node.find('c:xVal',NS)),x,name+' x')
        for name in notes:
            text=' '.join(n.text or '' for n in ET.fromstring(z.read(name)).findall('.//a:t',NS))
            assert 'Sources:' in text and ('Target:' in text or 'Optional appendix' in text)
    receipt=json.loads((TMP/'latest_validation.json').read_text());assert receipt['finalSha256']==sha(pptx)
    assert receipt['firstPartyImport']['passed'] and receipt['nativeChartValidation']['passed']
    slide_pdf=PdfReader(OUT/'presentation.pdf');assert len(slide_pdf.pages)==15
    for i,page in enumerate(slide_pdf.pages,1):
        images=[x.get_object() for x in page['/Resources']['/XObject'].values() if x.get_object()['/Subtype']=='/Image']
        assert len(images)==1;pixels=Image.open(TMP/f'slide-{i:02d}.png').convert('RGB')
        assert images[0].get_data()==pixels.tobytes()
    for name,count in (('paper.pdf',8),('supplement.pdf',4)):
        doc=PdfReader(OUT/name);assert len(doc.pages)==count
        assert all(len(p.extract_text() or '')>400 for p in doc.pages),(name,'PDF must contain selectable prose')
    names=('learning_delay','timing_variation','completion_curves','policy_validation','risk_differences','stability_comparison','distribution_fits','legacy_settings')
    for name in names:
        with Image.open(OUT/(name+'.png')) as im:assert im.width>=2200 and im.height>=1300
        assert len(PdfReader(OUT/(name+'.pdf')).pages)==1
    screen=json.loads((OUT/'originality_screen.json').read_text());assert len(screen['sources'])==6
    matches=[m for m in screen['matches'] if m['eight_word_windows'] or m['twelve_word_windows']]
    if matches:
        review=json.loads((OUT/'overlap_review.json').read_text())
        assert review['screen_sha256']==sha(OUT/'originality_screen.json') and review['all_matching_units_reviewed']
    result=dict(status='passed',calibration=90,policy_attempts=540,new_training_runs=1330,paper_pages=8,supplement_pages=4,
                slides=15,main_seconds=700,native_charts=6,native_tables=3,embedded_chart_workbooks=6,
                exported_chart_values_verified=True,exported_numerical_table_values_verified=True,presentation_pdf_matches_imported_slide_pixels=True,
                figure_pairs=8,official_similarity_score=None,native_powerpoint_application_open_tested=False,
                visual_inspection='Required separately; see visual_review.json')
    if reproduce:
        rep=ROOT/'tmp/paper_v2_reproduction';rep.mkdir(parents=True,exist_ok=True)
        rscript=ROOT/'.tools/R/app/bin/Rscript.exe'
        if not rscript.exists():rscript=Path(shutil.which('Rscript') or 'Rscript')
        subprocess.run([str(rscript),str(ROOT/'analysis/paper_v2.R'),str(DATA),str(rep)],cwd=ROOT,env={**os.environ,'LC_ALL':'C','LANG':'C'},check=True)
        tables=sorted(OUT.glob('*.csv'));assert len(tables)==9
        for original in tables:
            assert (rep/original.name).exists(),('Missing reproduced table',original.name)
            assert original.read_bytes()==(rep/original.name).read_bytes(),('Reproduced numerical table differs',original.name)
        for name in names:
            a=Image.open(OUT/(name+'.png')).convert('RGB');b=Image.open(rep/(name+'.png')).convert('RGB')
            assert a.size==b.size and a.tobytes()==b.tobytes(),('Reproduced graph differs',name)
            p,q=PdfReader(OUT/(name+'.pdf')),PdfReader(rep/(name+'.pdf'))
            assert p.pages[0].get_contents().get_data()==q.pages[0].get_contents().get_data(),('Vector graph differs',name)
        shutil.copy2(OUT/'audit.json',rep/'audit.json')
        subprocess.run([sys.executable,'-m','grokking.paper_report','--output',str(rep)],cwd=ROOT,check=True)
        for name in ('paper.md','supplement.md','abstract.md'):
            assert (OUT/name).read_bytes()==(rep/name).read_bytes(),('Reproduced Markdown source differs',name)
        for name in ('paper.pdf','supplement.pdf'):
            a,b=PdfReader(OUT/name),PdfReader(rep/name)
            assert [p.extract_text() for p in a.pages]==[p.extract_text() for p in b.pages],('Reproduced manuscript differs',name)
        result.update(reproduced_numerical_csvs=9,reproduced_png_figures=8,reproduced_vector_figures=8,reproduced_manuscript_text=True,reproduced_markdown_sources=3)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--reproduce',action='store_true')
    verify(p.parse_args().reproduce)
