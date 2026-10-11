"""Risk keyword taxonomy and traceable candidate extraction."""
import re
from collections import defaultdict
from pathlib import Path
from .io import read_rows, write_rows


def load_terms(path):
    terms = defaultdict(set)
    for row in read_rows(path):
        group, term = row['category'].strip(), row['keyword'].strip()
        if group not in {'data', 'cyber', 'technology'}:
            raise ValueError(f'Unknown category: {group}')
        if term:
            terms[group].add(term)
    return {g: sorted(v, key=lambda s: (-len(s), s)) for g, v in terms.items()}


def sentence_split(text):
    # Text may contain wrapped lines from PDF. No fabricated sentence boundary
    # at a line break; Chinese sentence punctuation remains authoritative.
    compact = re.sub(r'(?<![。！？!?；;])\n(?!\n)', '', text)
    return [s.strip() for s in re.split(r'(?<=[。！？!?；;])|\n{2,}', compact) if s.strip()]


def match_sentences(text, taxonomy):
    """Sentence-level retrieval; broad matches are candidates, NOT risk labels."""
    result = []
    for ordinal, sentence in enumerate(sentence_split(text), 1):
        matches = {cat: [kw for kw in kws if kw in sentence]
                   for cat, kws in taxonomy.items()}
        categories = sorted(cat for cat, words in matches.items() if words)
        if categories:
            result.append({'sentence_id': ordinal, 'sentence': sentence,
                           'categories': '|'.join(categories),
                           'keywords': '|'.join(sorted({w for ws in matches.values() for w in ws}))})
    return result


def batch_match(input_dir, lexicon_file, output_file, metadata_file=None):
    from .io import write_rows
    taxonomy = load_terms(lexicon_file)
    metadata = {}
    if metadata_file:
        metadata = {row['filename']: row for row in read_rows(metadata_file)}
    collected = []
    for path in sorted(Path(input_dir).glob('*.txt')):
        filemeta = metadata.get(path.name, {})
        for row in match_sentences(path.read_text(encoding='utf-8-sig'), taxonomy):
            collected.append({'filename': path.name,
                              'firm_id': filemeta.get('firm_id', ''),
                              'year': filemeta.get('year', ''), **row})
    headers = ['firm_id','year','filename','sentence_id','categories','keywords','sentence']
    write_rows(output_file, collected, headers)
    return len(collected)
