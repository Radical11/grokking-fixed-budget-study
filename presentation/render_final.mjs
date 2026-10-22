import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const root=process.cwd();
const filename=process.argv[2] ?? 'review1_presentation.pptx';
const deck=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'output/review1_presentation',filename)));
for(let i=0;i<deck.slides.items.length;i++) {
  const png=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
  await fs.writeFile(path.join(root,'tmp/review1_presentation',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
console.log(`Rendered all ${deck.slides.items.length} final PPTX slides.`);
