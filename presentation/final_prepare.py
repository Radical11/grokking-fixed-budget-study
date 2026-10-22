"""Prepare the final presentation from completed study outputs; no new training."""
from pathlib import Path
import csv, json, statistics

root=Path(__file__).resolve().parents[1]
out=root/'output/final_package'; out.mkdir(parents=True,exist_ok=True)
def read(path):
    with (root/path).open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
summary=read('data/summary.csv')
main=[r for r in summary if r['stage']=='main' and r['status']=='completed']
validation=[r for r in summary if r['stage']=='validation' and r['status']=='completed']
assert len(main)==120 and len(validation)==70 and len(summary)==199
baseline=[r for r in main if float(r['train_fraction'])==.6 and float(r['weight_decay'])==1]
assert len(baseline)==20 and all(r['event_observed']=='True' for r in baseline)
times=[int(r['generalization_time']) for r in baseline]
assert statistics.mean(times)==5481.25 and statistics.median(times)==4025
trace=read('data/runs/main/main_f0.6_w1_s11113/trace.csv')
trace=[{k:float(v) for k,v in r.items()} for r in trace if int(r['step'])<=6500]
pred=[{k:float(v) for k,v in r.items()} for r in read('output/review2/policy_predictions.csv')]
groups=read('output/review2/group_statistics.csv')
assert len(groups)==6 and all(int(g['n'])==20 for g in groups)
policies=read('data/policies.csv'); assert len(policies)==30
assert all(int(p['completed_updates'])==int(p['total_budget'])==30000 for p in policies)
hist=[sum(i*5000<=t<(i+1)*5000 for t in times) for i in range(6)]
assert sum(hist)==20
data={'scope':'Completed final study; 120 main runs and 30 independent policy attempts',
      'main':main,'baseline_times':times,'groups':groups,'trace':trace,
      'histogram':{'labels':['0-5k','5-10k','10-15k','15-20k','20-25k','25-30k'],'counts':hist},
      'predictions':pred,'fits':read('output/review2/distribution_fits.csv'),
      'policy_validation':read('output/review2/policy_validation.csv'),
      'two_factor':read('output/review2/two_factor_tests.csv'),
      'model_summary':read('output/review2/model_summary.csv')[0]}
(out/'evidence.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
content=json.loads((root/'presentation/final_content.json').read_text())
refs=json.loads((root/'presentation/content.json').read_text())['references']
refs[-1]={**refs[-1],'label':'Project final-study evidence','title':'120 main runs, fresh-seed validation and base-R outputs','url':'data/summary.csv; data/policies.csv; output/review2/'}
content['references']=refs
(out/'content.json').write_text(json.dumps(content,indent=2)+'\n',encoding='utf-8',newline='\n')
total=sum(s['seconds'] for s in content['slides']); assert 600<=total<=720
notes=['# Final-review speaker notes','',f'Planned main duration: {total//60}:{total%60:02d}. Present slides 1-13; slides 14-15 are optional.','', 'Replace name and registration-number fields before presenting. All displayed results are from the completed final study.','']
elapsed=0
for i,s in enumerate(content['slides'],1):
    notes.extend([f"## {i}. {s['title']}",'',f"Target: {s['seconds']} seconds; start at {elapsed//60}:{elapsed%60:02d}." if s['seconds'] else 'Optional question slide.','',s['notes'],'','Sources: '+'; '.join(f"[{r['id']}] {r['label']} - {r['url']}" for r in refs if r['id'] in s['sources']),''])
    elapsed+=s['seconds']
(out/'speaker_notes.md').write_text('\n'.join(notes),encoding='utf-8',newline='\n')
print(json.dumps({'main':len(main),'validation_constituents':len(validation),'attempts':len(policies),'slides':len(content['slides']),'planned_seconds':total}))
