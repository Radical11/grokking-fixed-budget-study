"""Render the editable paper Markdown, retaining its explicit page and layout controls."""
from pathlib import Path
from xml.sax.saxutils import escape
import argparse,re
from PIL import Image as PILImage
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate,Paragraph,Image,Table,TableStyle,PageBreak


def make_styles():
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitlePaper',fontName='Helvetica-Bold',fontSize=18,leading=21,spaceAfter=9,textColor=colors.HexColor('#172B3A')))
    styles.add(ParagraphStyle(name='BodyPaper',fontName='Helvetica',fontSize=9.5,leading=13.1,spaceAfter=7))
    styles.add(ParagraphStyle(name='CaptionPaper',fontName='Helvetica',fontSize=8.3,leading=11,spaceAfter=8,textColor=colors.HexColor('#4A5963')))
    styles.add(ParagraphStyle(name='CellPaper',fontName='Helvetica',fontSize=8.3,leading=10.8))
    styles['Heading2'].fontName='Helvetica-Bold';styles['Heading2'].fontSize=12;styles['Heading2'].leading=15
    styles['Heading2'].spaceBefore=7;styles['Heading2'].spaceAfter=7
    return styles


def inline(text):
    return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',text)


def make_table(rows,widths,styles):
    assert rows and all(len(r)==len(rows[0]) for r in rows),'Table rows must have the same column count'
    assert len(widths)==len(rows[0]) and all(w>0 for w in widths) and sum(widths)<=6.82,'Invalid table widths in inches'
    cells=[[Paragraph(inline(escape(str(c))),styles['CellPaper']) for c in row] for row in rows]
    table=Table(cells,colWidths=[w*inch for w in widths],repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F4')),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#637E8E'))]))
    return table


def footer(canvas,doc):
    canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#667784'))
    canvas.drawString(52,25,'Grokking under a fixed budget | Paper v2 | BAMAT207')
    canvas.drawRightString(543,25,str(doc.page));canvas.restoreState()


def render_source(source,output,expected_pages=None):
    source=Path(source).resolve();output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    styles=make_styles();story=[];style='BodyPaper';widths=None;figure_width=6.65;title=source.stem
    for block in re.split(r'\n\s*\n',source.read_text(encoding='utf-8').strip()):
        block=block.strip()
        if not block:continue
        control=re.fullmatch(r'<!--\s*(style|table-widths|figure-width):\s*(.*?)\s*-->',block,re.S)
        if control:
            kind,value=control.groups()
            if kind=='style':
                assert value in ('BodyPaper','CaptionPaper'),'Unknown paragraph style'
                style=value
            elif kind=='table-widths':widths=[float(x) for x in value.split(',')]
            else:
                figure_width=float(value);assert 0<figure_width<=6.82,'Invalid figure width in inches'
            continue
        if block=='---':story.append(PageBreak());continue
        image=re.fullmatch(r'!\[.*\]\(([^\n]+)\)',block,re.S)
        if image:
            image_path=source.parent/image.group(1)
            with PILImage.open(image_path) as im:w,h=im.size
            story.append(Image(str(image_path),width=figure_width*inch,height=figure_width*inch*h/w));figure_width=6.65
            continue
        if block.startswith('|'):
            rows=[[cell.strip() for cell in line.strip().strip('|').split('|')] for line in block.splitlines()]
            assert len(rows)>=2 and all(re.fullmatch(r':?-+:?',c) for c in rows[1]),'Expected a Markdown table separator'
            rows=rows[:1]+rows[2:]
            story.append(make_table(rows,widths or [6.65/len(rows[0])]*len(rows[0]),styles));widths=None
            continue
        if block.startswith('## '):block=block[3:];paragraph_style='Heading2'
        elif block.startswith('# '):
            block=block[2:];paragraph_style='TitlePaper';title=re.sub('<[^>]+>',' ',block)
        else:paragraph_style=style
        story.append(Paragraph(inline(' '.join(block.splitlines())),styles[paragraph_style]));style='BodyPaper'
    assert widths is None,'A table-width control has no following table'
    document=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),leftMargin=52,rightMargin=52,topMargin=44,bottomMargin=43,
                               title=title,author='BAMAT207 student project')
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    pages=len(PdfReader(output).pages)
    if expected_pages is not None:assert pages==expected_pages,f'{output.name}: expected {expected_pages} pages, got {pages}; repair layout before delivery'
    return pages


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source');parser.add_argument('--output',required=True);parser.add_argument('--pages',type=int)
    args=parser.parse_args();print(f'Rendered {render_source(args.source,args.output,args.pages)} pages: {args.output}')
