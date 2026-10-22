import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {FileBlob,Presentation,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),build=path.join(root,'tmp/assessments_visual');
const runtime=path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const skill=path.join(process.env.USERPROFILE,'.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
process.env.RUNTIME_NODE=path.join(runtime,'node/bin/node.exe');
process.env.RUNTIME_PYTHON=path.join(runtime,'python/python.exe');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const final=process.env.ASSESSMENT_PPTX??path.join(root,'output/assessments_visual/Assessment10_Visual.pptx');
const candidate=path.join(build,'candidate.pptx');
if(process.argv.includes('--rebuild')){
 const {author}=await import(pathToFileURL(path.join(root,'scripts/assessments_visual/presentation.mjs')).href);
 const data=JSON.parse(await fs.readFile(path.join(root,'output/paper_v2/presentation_evidence.json'),'utf8'));
 const deck=Presentation.create({slideSize:{width:1280,height:720}});await author(deck,data);
 await (await PresentationFile.exportPptx(deck)).save(candidate);
}
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,
 explicitTotalSlideCount:10,requiredNativeChartOwnerSlides:[2,7,8,9],requiredNativeTableOwnerSlides:[],
 materializeLiteralChartWorkbooks:true,
 pythonExecutable:path.join(runtime,'python/python.exe'),
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(build,path.basename(final)+'.validation.json')});
const deck=await PresentationFile.importPptx(await FileBlob.load(final));
for(let i=0;i<deck.slides.items.length;i++){
 const blob=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`final-slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({status:result.status,final,slides:deck.slides.items.length}));
