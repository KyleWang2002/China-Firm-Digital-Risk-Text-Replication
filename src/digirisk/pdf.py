"""Convert local annual-report PDF files to UTF-8 text, with diagnostics."""
from pathlib import Path


def convert_pdf(path, output_path, min_chars=50):
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError('Install optional dependency: pip install -e ".[collect]"') from exc
    path, output_path = Path(path), Path(output_path)
    with fitz.open(path) as doc:
        if doc.needs_pass:
            raise ValueError(f'Encrypted PDF: {path.name}')
        text = '\n\f\n'.join(page.get_text('text', sort=True) for page in doc)
        pages = len(doc)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding='utf-8')
    status = 'text_extracted' if len(text.strip()) >= min_chars else 'likely_scan_requires_ocr'
    return {'filename': path.name, 'pages': pages, 'characters': len(text.strip()), 'status': status}


def batch_convert(pdf_dir, text_dir):
    from .io import write_rows
    output, audit=[],[]
    for p in sorted(Path(pdf_dir).glob('*.pdf')):
        try:
            rec = convert_pdf(p, Path(text_dir)/(p.stem+'.txt'))
        except Exception as exc:
            rec={'filename':p.name,'pages':'','characters':'','status':f'ERROR: {exc}'}
        audit.append(rec)
    write_rows(Path(text_dir)/'conversion_audit.csv', audit,
               ['filename','pages','characters','status'])
    return audit
