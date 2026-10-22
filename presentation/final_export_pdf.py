"""Create a matching static PDF from the final deck's inspected slide renders."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

root = Path(__file__).resolve().parents[1]
pages = sorted((root / 'tmp/final_presentation').glob('slide-??.png'))
assert len(pages) == 15, f'Expected 15 final slide renders, found {len(pages)}'
out = root / 'output/pdf/final_presentation.pdf'
out.parent.mkdir(parents=True, exist_ok=True)
pdf = canvas.Canvas(str(out), pagesize=(960, 540))
pdf.setTitle('Grokking Under a Fixed Budget - Final Study')
for page in pages:
    pdf.drawImage(ImageReader(str(page)), 0, 0, width=960, height=540)
    pdf.showPage()
pdf.save()
print(f'Exported {len(pages)} matching presentation pages to {out}')
