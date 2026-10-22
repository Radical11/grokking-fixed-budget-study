import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
const root=process.cwd(),out=path.join(root,'output/paper_v2'),build=path.join(root,'tmp/paper_v2_presentation');
const skill=process.env.CODEX_PRESENTATION_SKILL??path.join(os.homedir(),'.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations');
const runtime=process.env.CODEX_RUNTIME_DEPENDENCIES??path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');process.env.RUNTIME_NODE=path.join(runtime,'node/bin/node.exe');process.env.RUNTIME_PYTHON=path.join(runtime,'python/python.exe');
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const content=JSON.parse(await fs.readFile(path.join(out,'presentation_content.json'),'utf8'));
const data=JSON.parse(await fs.readFile(path.join(out,'presentation_evidence.json'),'utf8'));
const deck=Presentation.create({slideSize:{width:1280,height:720}});await fs.mkdir(build,{recursive:true});
const blue='#175F96',ink='#172B3A',grey='#667784',pale='#DDE5EA',colors=[blue,'#637E8E','#253F50'];const visible=[];
function text(s,value,x,y,w,h,size=28,options={}) {
 const t=s.shapes.add({geometry:'textbox',name:`text-${s.shapes.items.length}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 t.text=value;t.text.style={fontSize:size,typeface:'Arial',color:ink,verticalAlignment:'top',insets:0,autoFit:'none',wrap:'square',...options};visible.push(value);return t;
}
function lines(s,values,y=235,gap=77,size=28){values.forEach((v,i)=>text(s,v,72,y+i*gap,1136,gap-8,size));}
const axis=(title,extra={})=>({title:{text:title,textStyle:{fontSize:24,fill:ink}},textStyle:{fontSize:23,fill:ink},line:{fill:grey,width:1},numberFormatCode:'0',...extra});
const grid={style:'solid',fill:pale,width:1};
function chart(s,type,cfg){
 const series=cfg.series.map(v=>({...v,values:v.values.map(n=>Number(Number(n).toFixed(8)))}));
 const c=s.charts.add(type,{chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},titleTextStyle:{fontSize:24,fill:ink},...cfg,series});
 applyPresentationChartFont(c,{fontFamily:'Arial'});visible.push(cfg.title??'',...(cfg.categories??[]),...series.map(v=>v.name));return c;
}
function table(s,values,x,y,w,h,widths,fontSize=23){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});t.borders.assign({fill:'#FFFFFF',width:0});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[r].length;c++){const cell=t.getCell(r,c);cell.fill='#FFFFFF';cell.text.style={typeface:'Arial',fontSize,color:r===0?blue:ink,bold:r===0,verticalAlignment:'middle',insets:8};}
 visible.push(...values.flat().map(String));return t;
}
function slide(i){
 const s=deck.slides.add();s.background.fill='#FFFFFF';text(s,content.slides[i].title,72,45,1136,92,i===0?54:42,{bold:true,color:i===0?blue:ink});
 if(i!==0)text(s,'Paper v2 | Grokking under a fixed budget',72,682,930,25,18,{color:grey});
 text(s,`${String(i+1).padStart(2,'0')}${i>=13?' | Optional':''}`,1040,682,168,25,18,{color:grey,alignment:'right'});
 const refs=content.references.filter(r=>content.slides[i].sources.includes(r.id)).map(r=>`[${r.id}] ${r.label}. ${r.title}. ${r.url}`).join('\n');
 s.speakerNotes.text=`${content.slides[i].seconds?`Target: ${content.slides[i].seconds} seconds.`:'Optional appendix; outside main timing.'}\n\n${content.slides[i].notes}\n\nSources:\n${refs}`;return s;
}
const get=(split,B,k,ep='first')=>data.policies.find(p=>Number(p.split_seed)===split&&Number(p.total_budget)===B&&Number(p.k)===k&&p.endpoint===ep);
let s=slide(0);
text(s,'One Long Run or Several Restarts?',72,195,1136,90,44,{color:blue});
text(s,'Probability and Statistics | BAMAT207\nThree fixed dataset splits; two smaller budgets',72,340,1136,88,29,{color:grey});
text(s,'Name: [Your name]\nRegistration number: [Your registration number]',72,530,1136,96,27);
s=slide(1);
text(s,'The practice answers improve first. New-question accuracy improves later.',72,158,1136,91,34,{color:blue});
lines(s,['Memorization = doing well on familiar practice examples.','Generalization = doing well on questions held back from practice.','Grokking = a delayed improvement on those new questions.','Example: (30 + 4) mod 31 = 3. “Mod” keeps the remainder.'],286,76,28);
text(s,'This is a measured learning pattern, not a claim of human-like understanding.',72,624,1136,40,23,{color:grey});
s=slide(2);
text(s,'With the same total learning steps, is one long run or several fresh starts more reliable?',72,156,1136,101,34,{color:blue});
lines(s,['One update = one learning step. A restart begins with new starting weights.','The original 30,000-update comparison gave 10/10 for every policy.','Now test 8,000 and 12,000 total updates, chosen before fresh validation.','Estimate probabilities, then check them with separate new runs.'],292,76,27);
s=slide(3);
lines(s,['Task: 961 number pairs; 576 practice + 385 new questions.','A split chooses the practice questions. We fix three different splits.','A seed chooses repeatable starting weights; weight decay gently shrinks them.','90 calibration runs estimate probabilities: 30 per split, including 20 reused.','540 fresh budget attempts test the policies, with 30 per condition.','Same small model and CPU settings. Python trains; R analyses.'],166,78,26);
s=slide(4);
chart(s,'scatter',{position:{left:55,top:154,width:1170,height:426},title:'Representative calibration run; early training window',series:[{name:'Practice questions',xValues:data.trace.map(p=>p.step),values:data.trace.map(p=>p.train_acc),line:{fill:blue,width:3},marker:{symbol:'none'}},{name:'New questions',xValues:data.trace.map(p=>p.step),values:data.trace.map(p=>p.test_acc),line:{fill:grey,width:3},marker:{symbol:'none'}}],scatterOptions:{style:'line'},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:23,fill:ink}},xAxis:axis('Learning steps (updates)',{min:0,max:data.trace_end}),yAxis:axis('Correct answers',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'First confirmation: 3 checks in a row. Longer window: 21 checks spanning 500 updates.',72,599,1136,44,25,{color:blue});
text(s,'Both require ≥99% practice and ≥95% new-question accuracy; check every 25 updates.',72,647,1136,30,21,{color:grey});
s=slide(5);
chart(s,'scatter',{position:{left:56,top:164,width:1158,height:430},title:'First-confirmation completion curves; 30 calibration runs per split',series:[20261013,20261014,20261015].map((split,i)=>{const g=data.completion_curves.filter(r=>Number(r.split_seed)===split&&r.endpoint==='first');const points=[{x:0,y:0}];for(const r of g){const x=Number(r.time),y=Number(r.probability);if(x===0)continue;points.push({x,y:points.at(-1).y},{x,y});}return{name:`Split ${i+1}`,xValues:points.map(p=>p.x),values:points.map(p=>p.y),line:{fill:colors[i],width:3},marker:{symbol:'none'}}}),scatterOptions:{style:'line'},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:23,fill:ink}},xAxis:axis('Learning steps (updates)',{min:0,max:30000,majorUnit:10000}),yAxis:axis('Fraction confirmed',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'Unfinished runs stay in the denominator. Their eventual learning times are unknown.',72,625,1136,45,25,{color:blue});
s=slide(6);
text(s,'P(at least one works) = 1 − [1 − F(B/k)]ᵏ',72,153,1136,65,37,{color:blue});
text(s,'B = total updates; k = fresh starts; F(t) = chance one run succeeds by t.',72,233,1136,49,26);
table(s,[['Method','Meaning in this experiment'],['Bernoulli / binomial','One yes/no attempt; a count of successes.'],['Confidence interval','Uncertainty from a finite sample.'],['Fisher test + Holm','Compare policies; account for 12 planned tests.'],['Bootstrap / exact bounds','Two views of uncertainty in probability differences.']],72,323,1136,282,[340,796]);
text(s,'The formula assumes independent fresh starts within the same setting.',72,632,1136,37,24,{color:grey});
s=slide(7);
chart(s,'bar',{position:{left:54,top:168,width:740,height:429},title:'Original split; fresh first-confirmation outcomes',categories:['1 run','2 runs','4 runs'],series:[8000,12000].map((B,i)=>({name:`B = ${B.toLocaleString('en-US')}`,values:[1,2,4].map(k=>Number(get(20261013,B,k).observed_probability)),fill:colors[i]})),barOptions:{direction:'column',gapWidth:70},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:22,fill:ink}},xAxis:axis('Policy'),yAxis:axis('Observed success',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
table(s,[['Policy','8k','12k'],...[1,2,4].map(k=>[`${k} run${k===1?'':'s'}`,`${get(20261013,8000,k).successes}/30`,`${get(20261013,12000,k).successes}/30`])],827,241,381,239,[133,124,124],22);
const exampleCI=get(20261013,8000,1);
text(s,`One run at 8k: exact 95% interval ${(100*Number(exampleCI.ci_low)).toFixed(1)}% to ${(100*Number(exampleCI.ci_high)).toFixed(1)}% (n = 30).`,72,628,1136,42,24,{color:blue});
s=slide(8);
chart(s,'bar',{position:{left:55,top:165,width:1160,height:431},title:'8,000 total updates; n = 30 per policy and split',categories:['Split 1','Split 2','Split 3'],series:[1,2,4].map((k,i)=>({name:`${k} run${k===1?'':'s'}`,values:[20261013,20261014,20261015].map(split=>Number(get(split,8000,k).observed_probability)),fill:colors[i]})),barOptions:{direction:'column',gapWidth:80},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:23,fill:ink}},xAxis:axis('Fixed dataset split'),yAxis:axis('Observed first-confirmation success',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'The full paper also reports 12,000 updates on every split; three splits are a limited replication.',72,628,1136,42,24,{color:blue});
s=slide(9);
const categories=['8k / 1','8k / 2','8k / 4','12k / 1','12k / 2','12k / 4'];
chart(s,'bar',{position:{left:55,top:164,width:1160,height:432},title:'Original split: predictions frozen before validation',categories,series:[{name:'Predicted',values:data.original.map(p=>Number(p.predicted_probability)),fill:grey},{name:'Observed',values:data.original.map(p=>Number(p.observed_probability)),fill:blue}],barOptions:{direction:'column',gapWidth:60},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:23,fill:ink}},xAxis:axis('Total budget / number of runs',{textStyle:{fontSize:21,fill:ink}}),yAxis:axis('First-confirmation probability',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'Separate calibration and validation samples. The paper includes both sources of uncertainty.',72,629,1136,42,24,{color:blue});
s=slide(10);
chart(s,'bar',{position:{left:55,top:164,width:1160,height:432},title:'Original split: both endpoints on the same 30 attempts per condition',categories,series:[{name:'First confirmation',values:data.original.map(p=>Number(p.observed_probability)),fill:blue},{name:'500-update window',values:[8000,12000].flatMap(B=>[1,2,4].map(k=>Number(get(20261013,B,k,'stability').observed_probability))),fill:grey}],barOptions:{direction:'column',gapWidth:60},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:23,fill:ink}},xAxis:axis('Total budget / number of runs',{textStyle:{fontSize:21,fill:ink}}),yAxis:axis('Observed success',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'A longer accuracy window is a different outcome. It still does not guarantee permanent success.',72,628,1136,42,24,{color:blue});
s=slide(11);
text(s,`${data.significant_tests} of 12 planned contrasts have Holm-adjusted p < 0.05.`,72,159,1136,73,35,{color:blue});
lines(s,['8k budget: four restarts underperform one long run on all three splits.','12k budget: only the second-split four-run contrast survives correction.','The 500-update outcome separates a brief confirmation from a longer window.','Small gaps may remain unresolved; nonsignificance does not prove equivalence.','Future research: new tasks, new splits and longer accuracy windows.'],275,74,27);
s=slide(12);
let y=147;for(const ref of content.references.slice(0,4)){text(s,`[${ref.id}] ${ref.label}: ${ref.title}`,72,y,1136,60,23);text(s,ref.url,72,y+62,1136,26,18,{color:blue});y+=109;}
text(s,'[5-6] AdamW and transformer methods  |  [7] Official syllabus  |  [8] Project data',72,597,1136,34,21);
text(s,'Proposed empirical comparison; established ideas credited; no worldwide-first claim.',72,642,1136,30,22,{color:blue});
s=slide(13);
lines(s,['Illustration only: two independent attempts each have 60% success.','Each fails with probability 40%.','Both fail: 0.40 × 0.40 = 0.16.','At least one works: 1 − 0.16 = 0.84 (84%).','We still need the one-long-run probability before choosing a policy.'],179,85,30);
s=slide(14);
text(s,'Each entry: first-confirmation count / 500-window count; both out of 30.',72,151,1136,54,27,{color:blue});
const rows=[['Split / budget','1 run','2 runs','4 runs']];for(const [i,split] of [20261013,20261014,20261015].entries())for(const B of [8000,12000])rows.push([`S${i+1} / ${B/1000}k`,...[1,2,4].map(k=>`${get(split,B,k).successes} / ${get(split,B,k,'stability').successes}`)]);
table(s,rows,72,242,1136,350,[350,262,262,262]);text(s,'Full intervals, corrected comparisons and all source data are in the paper and supplement.',72,628,1136,42,24,{color:grey});
await fs.writeFile(path.join(build,'slide_text.json'),JSON.stringify(visible,null,2));
await (await PresentationFile.exportPptx(deck)).save(path.join(build,'candidate.pptx'));
for(let i=0;i<deck.slides.items.length;i++){const sl=deck.slides.items[i];await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await(await deck.export({slide:sl,format:'png',scale:1})).arrayBuffer()));await fs.writeFile(path.join(build,`slide-${i+1}.layout.json`),await(await sl.export({format:'layout'})).text());}
const final=path.join(out,process.env.DECK_FILENAME??'presentation.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'candidate.pptx'),finalPath:final,pythonExecutable:path.join(runtime,'python/python.exe'),integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry','--require-native-table-slide','7','--require-native-table-slide','8','--require-native-table-slide','15'],explicitTotalSlideCount:15,requiredNativeChartOwnerSlides:[5,6,8,9,10,11],requiredNativeTableOwnerSlides:[7,8,15],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,`validation-${Date.now()}.json`)});
await fs.writeFile(path.join(build,'latest_validation.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({final,slides:15,nativeCharts:6,nativeTables:3,status:'passed'}));
