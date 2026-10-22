"""Refresh notes/provenance after a deck-only wording edit, preserving the written submission."""
from pathlib import Path
import hashlib, json

root=Path(__file__).resolve().parents[1]
out=root/'output/review1_presentation'
content=json.loads((root/'presentation/content.json').read_text(encoding='utf-8'))
total=sum(s['seconds'] for s in content['slides'])
notes=['# Review 1 speaker notes', '', f'Main presentation: {total//60}:{total%60:02d} planned, including graph pauses. Slides 14-15 are optional.', '', 'Replace the editable name and registration-number fields before presenting. These explanations use the frozen Review 1 results.', '']
elapsed=0
for i,slide in enumerate(content['slides'],1):
    duration=slide['seconds']
    notes.extend([f"## {i}. {slide['title']}", '', f"Time: {duration} seconds; start at {elapsed//60}:{elapsed%60:02d}." if duration else 'Optional question slide; outside the main timing.', '', slide['notes'], '', 'Sources: '+'; '.join(f"[{r['id']}] {r['label']} - {r['url']}" for r in content['references'] if r['id'] in slide['sources']), ''])
    elapsed+=duration
(out/'speaker_notes.md').write_text('\n'.join(notes),encoding='utf-8',newline='\n')
manifest=json.loads((out/'input_manifest.json').read_text())
manifest['presentation/refresh_notes.py']=''
manifest={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in manifest}
(out/'input_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
print(f'Refreshed notes ({total} seconds planned) and {len(manifest)} source hashes.')
