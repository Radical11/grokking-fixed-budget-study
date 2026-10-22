"""Matching static slide PDF; editable source remains in the PPTX."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
ROOT=Path(__file__).resolve().parents[1]
pages=sorted((ROOT/'tmp/paper_v2_presentation').glob('slide-??.png'));assert len(pages)==15
pdf=canvas.Canvas(str(ROOT/'output/paper_v2/presentation.pdf'),pagesize=(960,540))
pdf.setTitle('Grokking under a fixed budget - Paper v2 presentation')
for page in pages:
    pdf.drawImage(ImageReader(str(page)),0,0,width=960,height=540);pdf.showPage()
pdf.save()
print('Exported matching 15-page presentation PDF.')
