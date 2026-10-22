import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,PresentationFile} from '@oai/artifact-tool';
const root=process.cwd(),out=path.join(root,'tmp/paper_v2_presentation');
const deck=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'output/paper_v2/presentation.pptx')));
for(let i=0;i<deck.slides.items.length;i++)await fs.writeFile(path.join(out,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await(await deck.export({slide:deck.slides.items[i],format:'png',scale:1})).arrayBuffer()));
console.log(`Reimported and rendered ${deck.slides.items.length} final slides.`);
