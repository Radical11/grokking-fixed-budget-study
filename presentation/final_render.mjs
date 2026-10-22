import fs from 'node:fs/promises';
import path from 'node:path';
import { FileBlob, PresentationFile } from '@oai/artifact-tool';
const root = process.cwd();
const pptx = path.join(root, 'output/final_package/final_presentation.pptx');
const build = path.join(root, 'tmp/final_presentation');
const deck = await PresentationFile.importPptx(await FileBlob.load(pptx));
for (let i = 0; i < deck.slides.items.length; i++) {
  const png = await deck.export({ slide: deck.slides.items[i], format: 'png', scale: 1 });
  await fs.writeFile(path.join(build, `slide-${String(i + 1).padStart(2, '0')}.png`), new Uint8Array(await png.arrayBuffer()));
}
console.log(`Rendered all ${deck.slides.items.length} final presentation slides.`);
