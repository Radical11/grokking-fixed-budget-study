"""Cache/read cited primary PDFs and perform a limited, explicit phrase screen."""
from pathlib import Path
import argparse,hashlib,html,json,re,shutil,urllib.request
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/paper_v2';CACHE=ROOT/'tmp/paper_v2/source_corpus'

def tokens(s):return re.findall(r'[a-z0-9]+',html.unescape(re.sub(r'<[^>]+>',' ',s)).lower())
def windows(words,n):return {tuple(words[i:i+n]) for i in range(max(0,len(words)-n+1))}
def corpus():
    refs=json.loads((ROOT/'paper/v2/references.json').read_text(encoding='utf-8'));data=[];CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    for ref in refs:
        if 'pdf' not in ref:continue
        target=CACHE/f'source_{ref["id"]}.pdf'
        if not target.exists():
            old=ROOT/f'tmp/review1_presentation/source_corpus/source_{ref["id"]}.pdf'
            if ref['id']<=3 and old.exists():shutil.copy2(old,target)
            else:
                request=urllib.request.Request(ref['pdf'],headers={'User-Agent':'BAMAT207 academic source verification'})
                with urllib.request.urlopen(request,timeout=45) as response:target.write_bytes(response.read())
        reader=PdfReader(target);text='\n'.join(p.extract_text() or '' for p in reader.pages)
        assert len(text)>500,('Source text extraction failed',ref['id'])
        data.append({**ref,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'pages':len(reader.pages),'status':'read','tokens':tokens(text)})
    (OUT/'sources.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='tokens'} for s in data],indent=2)+'\n',encoding='utf-8',newline='\n')
    return data,refs

def screen():
    sources,refs=corpus();content=json.loads((OUT/'presentation_content.json').read_text(encoding='utf-8'))
    paper=re.split(r'\n\n(?:## )?References\n\n',(OUT/'paper.md').read_text(encoding='utf-8'))[0]
    units={'paper_body':paper,'supplement':(OUT/'supplement.md').read_text(encoding='utf-8'),
           'spoken_notes':'\n'.join(s['notes'] for s in content['slides']),
           'slide_body':'\n'.join(json.loads((ROOT/'tmp/paper_v2_presentation/slide_text.json').read_text(encoding='utf-8')))}
    for unit in units:
        for ref in refs:
            for term in ('label','title','url'):
                if ref.get(term):units[unit]=units[unit].replace(ref[term],'')
    matches=[]
    for name,text in units.items():
        words=tokens(text)
        for source in sources:
            a=windows(words,8)&windows(source['tokens'],8);b=windows(words,12)&windows(source['tokens'],12)
            matches.append(dict(unit=name,source_id=source['id'],eight_word_windows=len(a),twelve_word_windows=len(b),examples=[' '.join(p) for p in sorted(a)[:8]]))
    result=dict(screen='Exact contiguous 8- and 12-word windows after lowercase/alphanumeric normalization',
                sources=[{k:v for k,v in s.items() if k!='tokens'} for s in sources],matches=matches,official_similarity_score=None,
                limitations='Only the six cited public PDFs were screened. Bibliographic strings are excluded; the main-paper reference section is excluded. No internet-wide corpus, student-submission database, semantic paraphrase detector, code-plagiarism comparison or AI-authorship detector was used. Text extraction may miss overlaps. Standard formulas and attributed technical language require contextual review; an exact overlap is not by itself plagiarism.')
    (OUT/'originality_screen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'sources_read':len(sources),'matching_units':[m for m in matches if m['eight_word_windows'] or m['twelve_word_windows']],'official_similarity_score':None},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cache-only',action='store_true')
    if p.parse_args().cache_only:
        data,_=corpus();print(json.dumps({'sources_read':len(data),'pages':[s['pages'] for s in data]}))
    else:screen()
