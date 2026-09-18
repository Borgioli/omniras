"""Correct the count panel in the archived arXiv model card, retaining vector art.

Requires PyMuPDF. The archived arXiv PDF is an immutable input. The current
manuscript reports 254 seed-level downstream runs, including 109 partial-FT
runs (abstract and opening of Results). These are not additional runs.
"""
from pathlib import Path
import hashlib
import json
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/static/figures/arxiv-v2/omniras_overview.pdf'
OUTPUT = ROOT / 'docs/static/figures/updated-20260918'
EXPECTED_SOURCE_SHA = '57cccc2412d49a95bd8914aa6450ed4f1d619c51f62af42a99f4bc30335ba744'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert sha(SOURCE) == EXPECTED_SOURCE_SHA, 'Unexpected source figure; inspect before editing.'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(SOURCE)
    page = doc[0]
    assert '~160+' in page.get_text()
    source_font = next(f for f in page.get_fonts() if 'SegoeUI-Bold' in f[3])
    fontdata = doc.extract_font(source_font[0])[3]
    font = fitz.Font(fontbuffer=fontdata)
    replacements = [
        ((305.625, 461.25), '254', 26.625, (42/255, 100/255, 150/255)),
        ((362, 447.8), 'probe-finetune runs', 13.5, (91/255, 107/255, 124/255)),
        ((362, 463.5), 'includes 109 partial-FT', 10.8, (91/255, 107/255, 124/255)),
    ]
    for _, text, _, _ in replacements:
        assert all(font.has_glyph(ord(c)) for c in text), 'Text exceeds original font subset.'
    # Remove the old text itself, not just cover it, while preserving all artwork.
    panel = fitz.Rect(303, 431, 539, 469)
    page.add_redact_annot(panel, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname='CorrectedCount', fontbuffer=fontdata)
    for origin, text, size, color in replacements:
        page.insert_text(origin, text, fontsize=size, fontname='CorrectedCount', color=color)
    pdf = OUTPUT / 'omniras_overview.pdf'
    doc.save(pdf, garbage=4, deflate=True)
    doc.close()
    with fitz.open(pdf) as corrected:
        text = corrected[0].get_text().replace('\u2010', '-')
        assert '~160+' not in text and '254' in text and 'includes 109 partial-FT' in text
        png = ROOT / 'docs/static/images/omniras_overview.png'
        pix = corrected[0].get_pixmap(dpi=170, alpha=False)
        pix.save(png)
    # Only the campaign-count rectangle may change visually.
    with fitz.open(SOURCE) as original, fitz.open(pdf) as corrected:
        a, b = original[0].get_pixmap(), corrected[0].get_pixmap()
        assert (a.width, a.height) == (b.width, b.height)
        differences = []
        for y in range(a.height):
            for x in range(a.width):
                if a.pixel(x, y) != b.pixel(x, y):
                    differences.append((x, y))
                    assert panel.x0-1 <= x <= panel.x1+1 and panel.y0-1 <= y <= panel.y1+1
        assert differences
    metadata = {
        'updated': '2026-09-18',
        'base': '../arxiv-v2/omniras_overview.pdf',
        'base_sha256': EXPECTED_SOURCE_SHA,
        'change': 'Replace ~160+ probe-finetune runs with 254; explicitly include 109 partial-FT runs.',
        'evidence': 'Local vjepa_paper_arxiv/main.tex abstract and opening of Results; same totals already in project-page text.',
        'semantics': '254 counts seed-level downstream runs; 109 partial-backbone fine-tuning runs are a subset.',
        'scope': 'Count panel only; other content reproduced from the archived arXiv figure.',
        'pdf_sha256': sha(pdf), 'png_sha256': sha(png),
        'render_dpi': 170, 'png_width': pix.width, 'png_height': pix.height,
        'verification': 'Only count-panel pixels differ at 72 dpi; old text removed from PDF extraction.'
    }
    (OUTPUT / 'SOURCE.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
