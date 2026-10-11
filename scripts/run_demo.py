"""Offline smoke demo with fictional sentences and invented model probabilities.

This runs without external accounts, API keys, GPU, or network access.
"""
import tempfile
from pathlib import Path
from digirisk.mda import batch_extract
from digirisk.lexicon import batch_match
from digirisk.score import aggregate

root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    audit=batch_extract(root/'data/example',tmp/'mda',minimum_chars=60)
    n=batch_match(tmp/'mda',root/'data/lexicon/digital_risk_seed_keywords.csv',
                  tmp/'candidate_sentences.csv',root/'data/example/file_metadata.csv')
    print(f'MD&A files: {len(audit)}; matched sentence candidates: {n}')
    count=aggregate(root/'data/example/illustrative_scored_sentences.csv',
                    tmp/'illustrative_index.csv')
    print(f'Illustrative firm-years: {count}. All inputs are synthetic.')
    print((tmp/'illustrative_index.csv').read_text(encoding='utf-8-sig'))
