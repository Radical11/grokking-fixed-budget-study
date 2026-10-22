from PIL import Image
from pypdf import PdfReader
from grokking.paper_typesetting import render_source


def test_editable_markdown_renders_text_tables_images_and_explicit_pages(tmp_path):
    Image.new('RGB',(40,20),'white').save(tmp_path/'figure.png')
    source=tmp_path/'editable.md';output=tmp_path/'paper.pdf'
    text='''# Editable paper

<!-- style: CaptionPaper -->

Name: [Your name]

## Methods

Original wording with **bold text** and a 95% interval.

<!-- table-widths: 2,4.65 -->

| Field | Meaning |
| --- | --- |
| T | First confirmation |

<!-- figure-width: 3 -->

![Example figure](figure.png)

<!-- style: CaptionPaper -->

Figure caption.

---

## Limitations

An explicit second page.
'''
    source.write_text(text,encoding='utf-8')
    assert render_source(source,output,2)==2
    pages=PdfReader(output).pages
    assert 'Original wording' in pages[0].extract_text()
    assert 'First confirmation' in pages[0].extract_text()
    assert 'Figure caption.' in pages[0].extract_text()
    assert 'An explicit second page.' in pages[1].extract_text()
    assert '/XObject' in pages[0]['/Resources']
    source.write_text(text.replace('Original wording','Revised wording'),encoding='utf-8')
    render_source(source,output,2)
    assert 'Revised wording' in PdfReader(output).pages[0].extract_text()
    assert 'Original wording' not in PdfReader(output).pages[0].extract_text()
