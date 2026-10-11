"""Prepare human-review queue without representing machine guesses as human labels."""
from .io import read_rows, write_rows

FIELDS = ['firm_id','year','filename','sentence_id','categories','keywords','sentence',
          'model_a','model_b','human_review','final_label','review_status']
VALID = {'risk', 'mitigation', 'irrelevant'}


def annotation_queue(input_csv, output_csv):
    rows = []
    for row in read_rows(input_csv):
        rows.append({**row, 'model_a':'', 'model_b':'', 'human_review':'',
                     'final_label':'', 'review_status':'unreviewed'})
    write_rows(output_csv, rows, FIELDS)
    return len(rows)


def reconcile(input_csv, output_csv):
    """Agreement is provisional; disagreement requires human review.

    This is an independently written protocol scaffold, not the authors'
    released annotation procedure. For real publication, human QA is required.
    """
    rows, unresolved = [], 0
    for row in read_rows(input_csv):
        a,b,h = (row.get(k, '').strip().lower() for k in ('model_a','model_b','human_review'))
        for value in (a,b,h):
            if value and value not in VALID:
                raise ValueError(f'Unknown annotation label {value!r}')
        if h:
            row.update(final_label=h, review_status='human_verified')
        elif a and b and a == b:
            row.update(final_label=a, review_status='model_agreement_unverified')
        else:
            row.update(final_label='', review_status='needs_human_review')
            unresolved += 1
        rows.append(row)
    write_rows(output_csv, rows, FIELDS)
    return len(rows), unresolved
