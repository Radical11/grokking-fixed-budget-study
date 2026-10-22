import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = process.cwd();
const SKILL = 'C:/Users/notak/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
const RUNTIME = 'C:/Users/notak/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES = path.join(RUNTIME,'node/node_modules');
process.env.RUNTIME_NODE = path.join(RUNTIME,'node/bin/node.exe');
process.env.RUNTIME_PYTHON = path.join(RUNTIME,'python/python.exe');
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const content = JSON.parse(await fs.readFile(path.join(root, 'presentation/content.json'), 'utf8'));
const data = JSON.parse(await fs.readFile(path.join(root, 'output/review1_presentation/evidence.json'), 'utf8'));
const build = path.join(root, 'tmp/review1_presentation');
const out = path.join(root, 'output/review1_presentation');
await fs.mkdir(build, {recursive:true});
const blue = '#175F96', ink = '#172B3A', grey = '#667784', pale = '#DDE5EA';
const deck = Presentation.create({slideSize:{width:1280,height:720}});
const visible = [];

function text(s, value, x, y, w, h, size=30, options={}) {
  const t = s.shapes.add({geometry:'textbox', name:`text-${s.shapes.items.length}`, position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0}});
  t.text = value;
  t.text.style = {fontSize:size,typeface:'Arial',color:ink,verticalAlignment:'top',insets:0,autoFit:'none',wrap:'square',...options};
  visible.push(value); return t;
}
function lineText(s, lines, x=72, y=174, w=1136, gap=95, size=30) {
  lines.forEach((v,i)=>text(s,v,x,y+i*gap,w,gap-14,size));
}
function chart(s, type, cfg) {
  // Round plotted values only to 8 decimals for Excel workbook portability.
  // Raw trace precision is preserved in the immutable experimental CSVs.
  const plotted = cfg.series.map(series=>({...series,values:series.values.map(value=>Number(value.toFixed(8)))}));
  const c = s.charts.add(type,{chartFill:'#FFFFFF',plotAreaFill:'#FFFFFF',chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},titleTextStyle:{fontSize:24,fill:ink}, ...cfg,series:plotted});
  applyPresentationChartFont(c,{fontFamily:'Arial'});
  visible.push(cfg.title ?? '', ...(cfg.categories ?? []), ...cfg.series.map(v=>v.name));
  return c;
}
const axis = (title,extra={})=>({title:{text:title,textStyle:{fontSize:24,fill:ink}},textStyle:{fontSize:23,fill:ink},line:{fill:grey,width:1},numberFormatCode:'0',...extra});
const grid = {style:'solid',fill:pale,width:1};
function table(s, values, x,y,w,h,widths) {
  const t = s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
  t.borders.assign({fill:'#FFFFFF',width:0});
  for(let r=0;r<values.length;r++) for(let c=0;c<values[r].length;c++) {
    const cell=t.getCell(r,c); cell.fill='#FFFFFF';
    cell.text.style={typeface:'Arial',fontSize:24,color:r===0?blue:ink,bold:r===0,verticalAlignment:'middle',insets:9};
  }
  visible.push(...values.flat().map(String)); return t;
}
function make(i) {
  const s=deck.slides.add();s.background.fill='#FFFFFF';
  text(s,content.slides[i].title,72,48,1136,100,i===0?56:44,{bold:true,color:i===0?blue:ink});
  if(i!==0)text(s,'Review 1 | Results from 24 training attempts',72,682,850,24,18,{color:grey});
  text(s,String(i+1).padStart(2,'0')+(i>=13?' | Optional':''),1040,682,168,24,18,{color:grey,alignment:'right'});
  const refs=content.references.filter(r=>content.slides[i].sources.includes(r.id)).map(r=>`[${r.id}] ${r.label}. ${r.title}. ${r.url}`).join('\n');
  s.speakerNotes.text=`${content.slides[i].seconds ? `Target: ${content.slides[i].seconds} seconds.` : 'Optional appendix; outside main timing.'}\n\n${content.slides[i].notes}\n\nSources:\n${refs}`;
  return s;
}
let s=make(0);
text(s,'One Long Run or Several Restarts?',72,200,1090,105,46);
text(s,'Probability and Statistics | BAMAT207\nReview 1 | 15 October 2026',72,368,1000,90,30,{color:grey});
text(s,'Name: [Your name]\nRegistration number: [Your registration number]',72,535,1090,100,28);

s=make(1);
text(s,'How much training does a model need to answer new questions?',72,163,1136,105,36,{color:blue});
lineText(s,['Model = a learning program; here, a small neural network.','Measure how much the waiting time changes between attempts.','Compare training settings and the chance of success within a limit.','Budget = total learning steps; restart = begin again from a fresh start.'],72,300,1136,81,29);

s=make(2);
text(s,'The model gets practice questions right first.\nAfter more training, it improves on new questions.',72,166,1136,105,35,{color:blue});
text(s,'That delayed improvement is called grokking.',72,309,1136,61,35,{bold:true});
lineText(s,['Memorization = doing well on the practice examples.','Generalization = doing well on questions excluded from practice.','Accuracy = the percentage of answers that are correct.'],72,414,1136,69,29);
text(s,'Think of learning a maths rule after practising examples. Background: Power et al. [1]',72,636,1136,35,23,{color:grey});

s=make(3);
text(s,'Task: add two numbers, then keep the remainder after dividing by 31.\n(30 + 4) mod 31 = 3   because 34 = 31 + 3.',72,166,1136,100,29,{color:blue});
lineText(s,['961 number pairs → 576 practice questions + 385 new questions.','Random seed = a number that chooses a repeatable starting point.','Training update = one learning step that adjusts the model.','Python runs and records the experiment; R analyses the results.'],72,305,1136,72,28);
text(s,'Weight decay gently shrinks the model’s internal numbers; compare 0.3, 1 and 3.\n24 main attempts; 9 setup attempts are excluded from these comparisons.',72,600,1136,70,24,{color:grey});

s=make(4);
text(s,'T = learning steps needed to pass our success rule',72,166,1136,58,36,{color:blue});
text(s,'Get ≥ 99% of practice answers and ≥ 95% of new answers correct\nat three checks in a row. Check every 25 updates.',72,246,1136,96,30);
text(s,'Pass at 2,000, 2,025 and 2,050 → record T = 2,050.',72,368,1136,60,31);
text(s,'T changes between attempts: it is a random variable.',72,453,1136,56,30);
text(s,'Limit C = 30,000. Capped time U = min(T, C).\nIf unfinished, eventual T is unknown; U records the limit.',72,538,1136,82,28,{color:blue});
text(s,'Three successful checks do not guarantee that accuracy stays high forever.',72,637,1136,33,24,{color:grey});

s=make(5);
chart(s,'bar',{position:{left:58,top:166,width:770,height:440},title:'Reference setting: 12 attempts',categories:data.histogram.labels,series:[{name:'Attempts',values:data.histogram.counts,fill:blue}],barOptions:{direction:'column',gapWidth:8},hasLegend:false,xAxis:axis('Waiting time (learning steps)',{textStyle:{fontSize:22,fill:ink}}),yAxis:axis('Number of attempts',{min:0,max:10,majorUnit:2,majorGridlines:grid}),dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:23,fill:ink}}});
text(s,'Mean (average): 6,475\nMedian (middle): 4,275\nSD (spread): 7,041\n\nRange:\n1,875–27,175',865,197,343,340,28);
text(s,'SD = standard deviation: spread around the average. One slow run raises the mean.',72,628,1136,40,25,{color:blue});

s=make(6);
chart(s,'scatter',{position:{left:55,top:162,width:760,height:453},title:'F(t) = chance of success by time t',series:[{name:'Success by t',xValues:data.cdf.x,values:data.cdf.y,line:{fill:blue,width:3},marker:{symbol:'none'}}],scatterOptions:{style:'line'},hasLegend:false,xAxis:axis('Time limit (learning steps)',{min:0,max:30000,majorUnit:10000}),yAxis:axis('Chance of success',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,'By 2,400: 3/12 = 25%\nBy 30,000: 12/12 succeed',840,192,368,104,27);
text(s,'95% confidence interval:\n73.5%–100%\nShows uncertainty from\na small sample.',840,326,368,169,26);
text(s,'Bernoulli = one yes/no result.\nBinomial = number of successes.',840,530,368,78,24);
text(s,'All 12 worked by the limit. Another attempt could still fail.',72,628,1136,40,28,{color:blue});

s=make(7);
table(s,[['Method','Plain meaning','Question answered'],['Welch’s t-test','Compare two group averages.','Could the gap be due to chance?'],['ANOVA','Compare all three averages.','Could all groups have the same true average?'],['Correlation','Measure how two things vary together.','Does larger decay go with less waiting?'],['Regression','Fit a line through the data.','How does waiting time relate to decay?']],72,163,1136,350,[250,465,421]);
text(s,'ANOVA p = 0.0077: a surprising gap if group means were equal.',72,549,1136,50,27,{color:blue});
text(s,'Check the test’s conditions: our errors do not follow the usual bell-shaped pattern.\nTreat these small-sample comparisons as early evidence.',72,607,1136,66,25);

s=make(8);
chart(s,'scatter',{position:{left:55,top:153,width:1170,height:422},title:'One example attempt (seed 11105)',series:[{name:'Practice questions',xValues:data.trace.map(r=>r.step),values:data.trace.map(r=>r.train_acc),line:{fill:blue,width:3},marker:{symbol:'none'}},{name:'New questions',xValues:data.trace.map(r=>r.step),values:data.trace.map(r=>r.test_acc),line:{fill:grey,width:3},marker:{symbol:'none'}}],scatterOptions:{style:'line'},hasLegend:true,legend:{position:'top',overlay:false,textStyle:{fontSize:24,fill:ink}},xAxis:axis('Learning steps (updates)',{min:0,max:6000,majorUnit:2000}),yAxis:axis('Correct answers (%)',{min:0,max:1,majorUnit:.25,numberFormatCode:'0%',majorGridlines:grid})});
text(s,`Practice success: ${data.representative.memorization_time}  |  New-question success T: ${data.representative.generalization_time} steps`,72,586,1136,43,28,{color:blue});
text(s,'First 6,000 steps shown. Later accuracy drops occurred in 18 of the 24 attempts.',72,638,1136,30,23,{color:grey});

s=make(9);
text(s,'Weight decay = a control that gently shrinks the model’s adjustable numbers.',72,145,1136,60,26,{color:blue});
chart(s,'scatter',{position:{left:55,top:211,width:600,height:395},title:'Each dot is one training attempt',series:[{name:'Waiting time',xValues:data.runs.map(r=>r.decay),values:data.runs.map(r=>r.T),marker:{symbol:'circle',size:8,fill:blue},line:{fill:'none',width:0}}],scatterOptions:{style:'marker'},hasLegend:false,xAxis:axis('Weight-decay setting',{min:0,max:3.3,majorUnit:1,numberFormatCode:'0.0'}),yAxis:axis('Waiting time (steps)',{min:0,max:30000,majorUnit:10000,majorGridlines:grid})});
table(s,[['Setting','Runs','Average','SD'],...data.groups.map(g=>[String(g.weight_decay),g.n,Math.round(Number(g.mean_capped_time)).toLocaleString('en-US'),Math.round(Number(g.sd_capped_time)).toLocaleString('en-US')])],688,234,520,252,[110,85,160,165]);
text(s,'All 24 passed by 30,000 steps.\nHigher decay went with shorter\nwaiting times in this sample.',688,514,520,99,27,{color:blue});
text(s,'Small groups; one practice/test split. More repeats are needed for broader conclusions.',72,637,1136,33,24);

s=make(10);
text(s,'P(at least one success) = 1 − [1 − F(B/k)]ᵏ',72,158,1136,65,37,{color:blue});
text(s,'B = total steps; k = attempts; F(t) = chance of success by step t.',72,239,1136,54,27);
table(s,[['Fresh starts (k)','Steps per attempt','Predicted chance'],...data.full_budget_predictions.map(r=>[`${r.k} attempt${r.k===1?'':'s'}`,Number(r.per_run_budget).toLocaleString('en-US'),(r.predicted_success*100).toFixed(1)+'%'])],72,314,1136,224,[290,420,426]);
text(s,'Total B = 30,000. Chance at least one works = 1 − chance all fail.',72,559,1136,51,27);
text(s,'Predictions from 12 reference runs; unvalidated in the Review 1 sample.',72,632,1136,40,25,{color:blue});

s=make(11);
text(s,'Review 1 milestone: approximately 65% of implementation',72,161,1136,58,34,{color:blue});
text(s,'Training code, saved progress, repeat attempts, statistics and first report.',72,240,1136,77,29);
text(s,'Review 2 will cover',72,339,1136,48,32,{bold:true});
text(s,'More attempts; mathematical descriptions of waiting-time patterns;\ncomparisons using more than one training control.',72,405,1136,87,29);
text(s,'Further research',72,514,1136,46,32,{bold:true});
text(s,'Try smaller budgets and different practice/test questions.\nCheck if success stays high (sustained generalization).',72,580,1136,77,28);

s=make(12);
let yy=154;
for(const r of content.references.slice(0,3)) {
  text(s,`[${r.id}] ${r.label}\n${r.title}`,72,yy,1136,78,25);
  text(s,r.url,72,yy+81,1136,26,19,{color:blue}); yy+=124;
}
text(s,'[4] Supplied BAMAT207 syllabus   |   [5] Project’s frozen Review 1 data',72,544,1136,45,23);
text(s,'Our proposed addition: measure waiting times and compare training budgets.\nThese earlier ideas are credited; a worldwide-first claim is not established.',72,600,1136,67,26,{color:blue});

s=make(13);
text(s,'Illustration with assumed chances; not a measured result',72,160,1136,45,28,{color:grey});
text(s,'Two attempts × 6,000 steps = 12,000 total steps.\nAssume each has 60% success and 40% failure.',72,242,1136,100,33);
text(s,'Both fail: 0.40 × 0.40 = 0.16 (16%)',72,377,1136,65,36);
text(s,'At least one works: 1 − 0.16 = 0.84 (84%)',72,480,1136,65,36,{color:blue});
text(s,'Independent = one outcome does not change the other’s chance.\nWe still need the one-long-run chance to choose a winner.',72,583,1136,79,27);

s=make(14);
lineText(s,['Seed = repeatable starting point. Update = one learning step.','Generalization = doing well on questions excluded from practice.','Standard deviation = spread. Confidence interval = uncertainty range.','Why three checks? Reduce reliance on one lucky evaluation.','Unfinished attempt? We do not know its eventual learning time.','Limits: few attempts, one question split, test assumptions and later drops.'],72,163,1136,77,27);

await fs.writeFile(path.join(out,'slide_text.json'),JSON.stringify(visible,null,2));
await (await PresentationFile.exportPptx(deck)).save(path.join(build,'candidate.pptx'));
for(let i=0;i<deck.slides.items.length;i++) {
  const slide=deck.slides.items[i];
  await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await (await deck.export({slide,format:'png',scale:1})).arrayBuffer()));
  await fs.writeFile(path.join(build,`slide-${i+1}.layout.json`),await (await slide.export({format:'layout'})).text());
}
// The bundled direct PDF exporter has an unresolved standard-font module.
// Export the matching static PDF from these rendered pages with export_slide_pdf.py.
const final = path.join(out,process.env.DECK_FILENAME ?? 'review1_presentation.pptx');
const result = await finalizePresentation({workspaceDir:root,candidatePath:path.join(build,'candidate.pptx'),finalPath:final,pythonExecutable:path.join(RUNTIME,'python/python.exe'),integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--validate-bullet-geometry','--require-native-table-slide','8','--require-native-table-slide','10','--require-native-table-slide','11'],explicitTotalSlideCount:15,requiredNativeChartOwnerSlides:[6,7,9,10],requiredNativeTableOwnerSlides:[8,10,11],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation-' + Date.now() + '.json')});
await fs.writeFile(path.join(build,'latest_validation.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify({final,slides:15,editableCharts:4,editableTables:3,validation:'passed'}));
