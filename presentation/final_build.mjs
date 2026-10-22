import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const root = process.cwd();
const skill = process.env.CODEX_PRESENTATION_SKILL ?? path.join(os.homedir(), '.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations');
const runtime = process.env.CODEX_RUNTIME_DEPENDENCIES ?? path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies');
process.env.RUNTIME_NODE_MODULES = path.join(runtime, 'node/node_modules');
process.env.RUNTIME_NODE = path.join(runtime, 'node/bin/node.exe');
process.env.RUNTIME_PYTHON = path.join(runtime, 'python/python.exe');
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(skill, 'container_tools/artifact_tool_utils.mjs')).href);
const content = JSON.parse(await fs.readFile(path.join(root, 'output/final_package/content.json'), 'utf8'));
const data = JSON.parse(await fs.readFile(path.join(root, 'output/final_package/evidence.json'), 'utf8'));
const build = path.join(root, 'tmp/final_presentation');
const out = path.join(root, 'output/final_package');
await fs.mkdir(build, { recursive: true });
const blue = '#175F96', ink = '#172B3A', grey = '#667784', pale = '#DDE5EA';
const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const visible = [];

function text(s, value, x, y, w, h, size = 28, options = {}) {
  const t = s.shapes.add({ geometry: 'textbox', name: `text-${s.shapes.items.length}`, position: { left: x, top: y, width: w, height: h }, fill: 'none', line: { fill: 'none', width: 0 } });
  t.text = value;
  t.text.style = { fontSize: size, typeface: 'Arial', color: ink, verticalAlignment: 'top', insets: 0, autoFit: 'none', wrap: 'square', ...options };
  visible.push(value); return t;
}
function lines(s, values, x = 72, y = 184, w = 1136, gap = 70, size = 28) { values.forEach((v, i) => text(s, v, x, y + i * gap, w, gap - 8, size)); }
function chart(s, type, cfg) {
  const series = cfg.series.map(v => ({ ...v, ...(v.values ? { values: v.values.map(n => Number(n.toFixed(8))) } : {}) }));
  const c = s.charts.add(type, { chartFill: '#FFFFFF', plotAreaFill: '#FFFFFF', chartLine: { fill: 'none', width: 0 }, plotAreaLine: { fill: 'none', width: 0 }, titleTextStyle: { fontSize: 24, fill: ink }, ...cfg, series });
  applyPresentationChartFont(c, { fontFamily: 'Arial' });
  visible.push(cfg.title ?? '', ...(cfg.categories ?? []), ...series.map(v => v.name));
  return c;
}
const axis = (title, extra = {}) => ({ title: { text: title, textStyle: { fontSize: 24, fill: ink } }, textStyle: { fontSize: 23, fill: ink }, line: { fill: grey, width: 1 }, numberFormatCode: '0', ...extra });
const grid = { style: 'solid', fill: pale, width: 1 };
function table(s, values, x, y, w, h, widths, fontSize = 23) {
  const t = s.tables.add({ rows: values.length, columns: values[0].length, left: x, top: y, width: w, height: h, columnWidths: widths, values });
  t.borders.assign({ fill: '#FFFFFF', width: 0 });
  for (let r = 0; r < values.length; r++) for (let c = 0; c < values[r].length; c++) {
    const cell = t.getCell(r, c); cell.fill = '#FFFFFF';
    cell.text.style = { typeface: 'Arial', fontSize, color: r === 0 ? blue : ink, bold: r === 0, verticalAlignment: 'middle', insets: 8 };
  }
  visible.push(...values.flat().map(String)); return t;
}
function slide(i) {
  console.log(`Building slide ${i + 1}`);
  const s = deck.slides.add(); s.background.fill = '#FFFFFF';
  text(s, content.slides[i].title, 72, 45, 1136, 91, i === 0 ? 54 : 42, { bold: true, color: i === 0 ? blue : ink });
  if (i !== 0) text(s, 'Final study | 120 main attempts', 72, 681, 850, 25, 18, { color: grey });
  text(s, `${String(i + 1).padStart(2, '0')}${i >= 13 ? ' | Optional' : ''}`, 1040, 681, 168, 25, 18, { color: grey, alignment: 'right' });
  const refs = content.references.filter(r => content.slides[i].sources.includes(r.id)).map(r => `[${r.id}] ${r.label}. ${r.title}. ${r.url}`).join('\n');
  s.speakerNotes.text = `${content.slides[i].seconds ? `Target: ${content.slides[i].seconds} seconds.` : 'Optional appendix; outside main timing.'}\n\n${content.slides[i].notes}\n\nSources:\n${refs}`;
  return s;
}
let s = slide(0);
text(s, 'One Long Run or Several Restarts?', 72, 195, 1136, 90, 44, { color: blue });
text(s, 'Probability and Statistics | BAMAT207\nFinal study | 15 October 2026', 72, 334, 1000, 90, 29, { color: grey });
text(s, 'Name: [Your name]\nRegistration number: [Your registration number]', 72, 515, 1100, 100, 27);

s = slide(1);
text(s, 'Grokking: a delayed jump from practice answers to new questions', 72, 155, 1136, 72, 33, { color: blue });
lines(s, ['Memorization: getting familiar practice questions right.', 'Generalization: using the rule on questions held back from practice.', 'Grokking: new-question performance improves after practice performance.', 'Our objectives: measure the waiting time, compare settings, and compare equal training budgets.'], 72, 264, 1136, 79, 28);
text(s, 'Like learning a maths rule after practising examples; the analogy does not claim human-like understanding.', 72, 620, 1136, 44, 23, { color: grey });

s = slide(2);
text(s, 'One fixed arithmetic rule, repeated independent starting points', 72, 154, 1136, 58, 32, { color: blue });
lines(s, ['Task: (30 + 4) mod 31 = 3; “mod” keeps the remainder.', '961 pairs: 40% uses 384 practice + 577 new; 60% uses 576 + 385.', 'Weight decay gently shrinks model weights; compare 0.3, 1 and 3.', '20 starting seeds × six settings = 120 main attempts; 9 pilot runs are separate.', 'Python trains and records; R calculates the statistical summaries.'], 72, 238, 1136, 67, 26);
text(s, 'A seed chooses repeatable starting weights. An update is one learning step.', 72, 613, 1136, 43, 23, { color: grey });

s = slide(3);
text(s, 'We use the same success rule for every attempt', 72, 155, 1136, 52, 33, { color: blue });
text(s, 'T = first update with 3 checks in a row at ≥99% practice and ≥95% held-out accuracy.', 72, 239, 1136, 86, 31);
text(s, 'Checks occur every 25 updates. The limit is C = 30,000 updates.', 72, 365, 1136, 50, 29);
text(s, 'If no event is seen, eventual T is unknown. For observed comparisons: U = min(T, C).', 72, 448, 1136, 79, 29, { color: blue });
text(s, '37 of 120 main attempts had no confirmed event by the limit. “Run completed” ≠ “generalized.”', 72, 575, 1136, 54, 25);

s = slide(4);
text(s, 'Practice accuracy rises before new-question accuracy', 72, 145, 1136, 53, 32, { color: blue });
chart(s, 'scatter', { position: { left: 58, top: 205, width: 1165, height: 400 }, title: 'Representative run (seed 11113)', series: [
  { name: 'Practice questions', xValues: data.trace.map(r => r.step), values: data.trace.map(r => r.train_acc), line: { fill: blue, width: 3 }, marker: { symbol: 'none' } },
  { name: 'New questions', xValues: data.trace.map(r => r.step), values: data.trace.map(r => r.test_acc), line: { fill: '#A97924', width: 3 }, marker: { symbol: 'none' } }
], scatterOptions: { style: 'line' }, hasLegend: true, legend: { position: 'top', overlay: false, textStyle: { fontSize: 23, fill: ink } }, xAxis: axis('Learning steps (updates)', { min: 0, max: 6500, majorUnit: 2000 }), yAxis: axis('Correct answers', { min: 0, max: 1, majorUnit: 0.25, numberFormatCode: '0%', majorGridlines: grid }) });
text(s, 'Practice threshold: 225 updates  |  First confirmed generalization T: 4,375 updates', 72, 619, 1136, 37, 25, { color: blue });

s = slide(5);
text(s, 'Average capped time U differs across the six settings', 72, 144, 1136, 52, 31, { color: blue });
chart(s, 'bar', { position: { left: 54, top: 198, width: 662, height: 400 }, title: 'Mean U; 20 attempts per group', categories: ['0.3', '1', '3'], series: [
  { name: '40% practice data', values: [30000, 19822.5, 20282.5], fill: '#A97924' },
  { name: '60% practice data', values: [15235, 5481.25, 1430], fill: blue }
], barOptions: { direction: 'column', gapWidth: 90 }, hasLegend: true, legend: { position: 'top', overlay: false, textStyle: { fontSize: 20, fill: ink } }, xAxis: axis('Weight decay'), yAxis: axis('Mean capped updates', { min: 0, max: 30000, majorUnit: 10000, majorGridlines: grid }) });
table(s, [['Data', 'Decay', 'Events', 'Mean U'], ['40%', '0.3', '0/20', '30,000'], ['40%', '1', '14/20', '19,823'], ['40%', '3', '10/20', '20,283'], ['60%', '0.3', '19/20', '15,235'], ['60%', '1', '20/20', '5,481'], ['60%', '3', '20/20', '1,430']], 741, 211, 467, 370, [92, 90, 125, 160], 20);
text(s, 'An unfinished run is capped at C in U; its eventual T is still unknown.', 72, 620, 1136, 39, 23, { color: grey });

s = slide(6);
text(s, '60% practice data, decay 1 | 20 attempts', 72, 144, 1136, 53, 32, { color: blue });
chart(s, 'bar', { position: { left: 55, top: 198, width: 720, height: 409 }, title: '60% data, decay 1 (n = 20)', categories: data.histogram.labels, series: [{ name: 'Attempts', values: data.histogram.counts, fill: blue }], barOptions: { direction: 'column', gapWidth: 45 }, hasLegend: false, xAxis: axis('Generalization time (updates)', { textStyle: { fontSize: 20, fill: ink } }), yAxis: axis('Number of attempts', { min: 0, max: 12, majorUnit: 3, majorGridlines: grid }) });
text(s, 'Mean: 5,481 updates\nMedian: 4,025\nSD: 5,548\nRange: 1,875–27,175\n\nSuccess: 20/20\nExact 95% CI: 83.2–100%\nBootstrap mean-U CI:\n3,596–8,224', 835, 210, 355, 356, 25);
text(s, 'SD = standard deviation (spread). The exact interval reflects the small sample.', 72, 620, 1136, 38, 23, { color: grey });

s = slide(7);
text(s, 'Three candidate patterns for the waiting-time data', 72, 145, 1136, 53, 32, { color: blue });
text(s, 'Model fit accounts for the 25-update check grid and the 50-update confirmation lag.', 72, 220, 1136, 52, 26);
table(s, [['Candidate pattern', 'AIC', 'Status'], ['Exponential', '257.15', 'Converged'], ['Gamma', '253.96', 'Converged'], ['Weibull', '256.85', 'Converged']], 72, 313, 1136, 240, [420, 260, 456]);
text(s, 'AIC balances fit and model complexity; lower is better among these candidates.', 72, 577, 1136, 42, 25, { color: blue });
text(s, 'The reference sample has 20 events and 0 unfinished attempts. Gamma ranks first here; this does not prove the true timing law.', 72, 624, 1136, 40, 22, { color: grey });

s = slide(8);
text(s, 'Statistics answer different questions; assumptions still matter', 72, 143, 1136, 53, 31, { color: blue });
lines(s, ['One-way ANOVA at 60% data: decay-group averages differ in this sample (p < 0.001).', 'Two-factor ANOVA: data fraction and decay differ; interaction is not clearly supported (p = 0.289).', 'Correlation: log decay and U move together at 60% data (Pearson −0.715; Spearman −0.866).', 'Regression: R² = 0.630 describes sample variation in capped time U.', 'Residuals fail a normal-shape check (Shapiro p = 0.00020); results are exploratory.'], 72, 222, 1136, 75, 25);
text(s, 'Permutation checks add a sensitivity view but assume exchangeable observations; they do not fix every model problem.', 72, 624, 1136, 41, 22, { color: grey });

s = slide(9);
text(s, 'Restart probability from the measured single-run curve', 72, 145, 1136, 53, 31, { color: blue });
text(s, 'P(at least one success) = 1 − [1 − F(B/k)]ᵏ', 72, 214, 1136, 62, 37, { color: blue });
text(s, 'B = total updates  |  k = number of fresh starts  |  F(t) = chance one run succeeds by t', 72, 288, 1136, 45, 24);
const policyGroups = [1, 2, 4].map(k => ({ k, rows: data.predictions.filter(r => Number(r.k) === k).sort((a, b) => Number(a.total_budget) - Number(b.total_budget)) }));
const colors = [blue, '#A97924', '#638E77'];
const series = policyGroups.map((g, idx) => {
  const points = [{ x: 0, y: 0 }];
  for (const r of g.rows) {
    const x = Number(r.total_budget), y = Number(r.predicted_success);
    if (x === 0) continue;
    const last = points.at(-1); if (last.x < x) points.push({ x, y: last.y }); points.push({ x, y });
  }
  return { name: `${g.k} start${g.k === 1 ? '' : 's'}`, xValues: points.map(p => p.x), values: points.map(p => p.y), line: { fill: colors[idx], width: 3 }, marker: { symbol: 'none' } };
});
chart(s, 'scatter', { position: { left: 56, top: 345, width: 754, height: 280 }, title: 'Predicted success with equal total budgets', series, scatterOptions: { style: 'line' }, hasLegend: true, legend: { position: 'top', overlay: false, textStyle: { fontSize: 20, fill: ink } }, xAxis: axis('Total update budget B', { min: 0, max: 30000, majorUnit: 10000 }), yAxis: axis('Predicted chance', { min: 0, max: 1, majorUnit: 0.25, numberFormatCode: '0%', majorGridlines: grid }) });
text(s, 'At B = 30,000:\n1 start: 100%\n2 starts: 99.8%\n4 starts: 99.9%\n\nFrom main data; these are predictions, not fresh-run evidence.', 847, 363, 340, 224, 25, { color: ink });

s = slide(10);
text(s, 'Fresh seeds gave the same outcome at this generous budget', 72, 143, 1136, 53, 31, { color: blue });
table(s, [['Policy', 'Allocation', 'Success', 'Exact 95% CI'], ['1 start', '1 × 30,000', '10/10', '69.2–100%'], ['2 starts', '2 × 15,000', '10/10', '69.2–100%'], ['4 starts', '4 × 7,500', '10/10', '69.2–100%']], 72, 231, 1136, 250, [240, 330, 240, 326]);
text(s, '30 independent budget attempts; 70 individual training runs; exactly 30,000 logical updates per attempt.', 72, 516, 1136, 50, 24);
text(s, 'No clear winner at this budget; equal results do not prove the policies equivalent. Runtime was not a controlled comparison.', 72, 583, 1136, 58, 24, { color: blue });

s = slide(11);
text(s, 'Findings and limits', 72, 145, 1136, 55, 34, { color: blue });
lines(s, ['Waiting time changes across random starts and training settings.', '83/120 main runs confirmed generalization within 30,000 updates; 37 remained unfinished.', '62/83 confirmed runs later fell below 95% held-out accuracy: first success is not permanent success.', 'All restart policies succeeded 10/10 at the tested budget, so the policy comparison is inconclusive.', 'Next research: smaller budgets, different practice/test splits, and sustained generalization.'], 72, 235, 1136, 74, 26);
text(s, 'The evidence is for this task, one fixed split and this small model.', 72, 624, 1136, 39, 23, { color: grey });

s = slide(12);
let y = 150;
for (const r of content.references.slice(0, 3)) {
  text(s, `[${r.id}] ${r.label}\n${r.title}`, 72, y, 1136, 68, 23);
  text(s, r.url, 72, y + 69, 1136, 25, 18, { color: blue }); y += 116;
}
text(s, '[4] Official BAMAT207 syllabus  |  [5] This project’s recorded final-study results', 72, 510, 1136, 40, 21);
text(s, 'Proposed empirical connection: learning-time variation and equal-budget restarts. No worldwide-first claim is established.', 72, 568, 1136, 65, 24, { color: blue });

s = slide(13);
text(s, 'Words and a worked probability', 72, 145, 1136, 50, 34, { color: blue });
lines(s, ['Seed = repeatable random starting point. Update = one learning step.', 'Censored = the event was not seen before the observation limit.', 'Assume two independent starts each have a 60% chance; failure chance = 40%.', 'Both fail: 0.40 × 0.40 = 0.16. At least one succeeds: 1 − 0.16 = 0.84 (84%).'], 72, 224, 1136, 80, 27);
text(s, 'This calculation is hypothetical, not a measured result. Independence is an assumption.', 72, 584, 1136, 46, 24, { color: grey });

s = slide(14);
text(s, 'Statistical details for questions', 72, 145, 1136, 50, 33, { color: blue });
lines(s, ['One-way ANOVA at 60% data: p = 3.69 × 10⁻¹⁰; permutation check p ≈ 0.001.', 'Two-factor ANOVA: fraction p ≈ 5.65 × 10⁻²³; decay p ≈ 7.09 × 10⁻¹²; interaction p = 0.289.', 'Regression on U: R² = 0.630; fitted 40%-to-60% difference ≈ −15,986 updates.', 'Policy intervals are wide because there are only ten attempts in each group.', 'The local copied-phrase screen is limited; an institutional plagiarism score is pending its chosen checker.'], 72, 226, 1136, 80, 24);
text(s, 'See the final report for exact methods, assumptions, uncertainty and source record.', 72, 624, 1136, 38, 22, { color: grey });

await fs.writeFile(path.join(build, 'slide_text.json'), JSON.stringify(visible, null, 2));
await (await PresentationFile.exportPptx(deck)).save(path.join(build, 'candidate.pptx'));
for (let i = 0; i < deck.slides.items.length; i++) {
  const current = deck.slides.items[i];
  await fs.writeFile(path.join(build, `slide-${String(i + 1).padStart(2, '0')}.png`), new Uint8Array(await (await deck.export({ slide: current, format: 'png', scale: 1 })).arrayBuffer()));
  await fs.writeFile(path.join(build, `slide-${i + 1}.layout.json`), await (await current.export({ format: 'layout' })).text());
}
const filename = process.env.DECK_FILENAME ?? 'final_presentation.pptx';
const final = path.join(out, filename);
const result = await finalizePresentation({ workspaceDir: root, candidatePath: path.join(build, 'candidate.pptx'), finalPath: final,
  pythonExecutable: path.join(runtime, 'python/python.exe'), integrityValidatorPath: path.join(skill, 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(skill, 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-heading-fit', '--validate-bullet-geometry', '--require-native-table-slide', '6', '--require-native-table-slide', '8', '--require-native-table-slide', '11'],
  explicitTotalSlideCount: 15, requiredNativeChartOwnerSlides: [5, 6, 7, 10], requiredNativeTableOwnerSlides: [6, 8, 11],
  materializeLiteralChartWorkbooks: true, fontPolicy: { basis: 'design', families: ['Arial'] }, verifyArtifactToolImport: true,
  receiptPath: path.join(build, `validation-${Date.now()}.json`) });
await fs.writeFile(path.join(build, 'latest_validation.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify({ final, slides: 15, editableCharts: 4, editableTables: 3, validation: 'passed' }));
