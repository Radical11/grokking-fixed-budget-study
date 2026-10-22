"""Export the already rendered deck to a matching static PDF, without modifying the runtime."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

root = Path(__file__).resolve().parents[1]
pages = sorted((root/'tmp/review1_presentation').glob('slide-??.png'))
assert len(pages) == 15
pdf = canvas.Canvas(str(root/'output/pdf/review1_presentation.pdf'), pagesize=(960,540))
pdf.setTitle('Grokking Under a Fixed Budget - Review 1 Presentation')
for page in pages:
    pdf.drawImage(ImageReader(str(page)),0,0,width=960,height=540)
    pdf.showPage()
pdf.save()
print('Exported 15-page matching static presentation PDF.')
