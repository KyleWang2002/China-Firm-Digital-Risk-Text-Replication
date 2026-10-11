"""Conservative MD&A section extraction from text-converted Chinese annual reports.

Sections differ by year and issuer. This extracts candidates and writes quality metadata;
it does not silently certify that a section is correct.
"""
import re
from pathlib import Path

START = re.compile(
    r'^\s*(?:第\s*[一二三四五六七八九十百\d]{1,4}\s*[章节]\s*)?'
    r'(?:管理层讨论与分析|经营情况讨论与分析|董事会报告|董事局报告)\s*$'
)
# Explicitly anchor the next major chapter; prevent accidentally ending on the
# frequent in-section subheading "风险管理".
CHAPTER = re.compile(r'^\s*第\s*([一二三四五六七八九十百\d]{1,4})\s*章\s*(.+?)\s*$')
NEXT_SECTION = ('公司治理', '公司管治', '重大事项', '重要事项', '财务报告',
                '监事会报告', '股份变动', '环境和社会责任', '公司简介')


def extract_mda(text, minimum_chars=200):
    lines = text.replace('\r\n', '\n').splitlines()
    starts = [i for i, x in enumerate(lines) if START.fullmatch(x.strip())]
    candidates = []
    for start in starts:
        start_chapter = CHAPTER.match(lines[start].strip())
        original_chapter = start_chapter.group(1) if start_chapter else None
        end = len(lines)
        for j in range(start + 1, len(lines)):
            candidate = lines[j].strip()
            m = CHAPTER.match(candidate)
            if m and (m.group(1) != original_chapter or original_chapter is None) and (
                any(item in m.group(2) for item in NEXT_SECTION) or j > start + 12):
                end = j
                break
            if (j > start + 15 and candidate in NEXT_SECTION):
                end = j
                break
        section = '\n'.join(lines[start + 1:end]).strip()
        if len(section) >= minimum_chars:
            candidates.append((len(section), section, start + 1, end))
    if not candidates:
        return {'text': '', 'status': 'needs_manual_review', 'start_line': '',
                'end_line': '', 'candidate_count': len(starts)}
    # A duplicated table-of-contents title can occur; retain longest plausible text.
    _, section, start, end = max(candidates)
    return {'text': section, 'status': 'automatic_unverified',
            'start_line': start, 'end_line': end, 'candidate_count': len(starts)}


def normalize_section(text):
    """Minimal normalization; preserve content and punctuation for auditability."""
    text = re.sub(r'[ \t\u3000]+', ' ', text)
    text = re.sub(r'(?m)^\s*\d{1,3}\s*$', '', text)  # isolated page numbers
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def batch_extract(input_dir, output_dir, minimum_chars=200):
    from .io import write_rows
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    if not input_dir.is_dir():
        raise FileNotFoundError(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audit = []
    for source in sorted(input_dir.glob('*.txt')):
        result = extract_mda(source.read_text(encoding='utf-8-sig'), minimum_chars)
        if result['text']:
            (output_dir / source.name).write_text(
                normalize_section(result['text']), encoding='utf-8')
        audit.append({'filename': source.name,
                      'characters': len(result['text']),
                      **{k: v for k, v in result.items() if k != 'text'}})
    write_rows(output_dir / 'extraction_audit.csv', audit,
               ['filename', 'characters', 'status', 'start_line', 'end_line',
                'candidate_count'])
    return audit
