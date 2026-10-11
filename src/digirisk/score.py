"""Firm-year digital risk exposure: max risk probability minus mean mitigation.

Method from Lu, Shi & Zhou (2025); missing-class conventions and classification
model choice are implementation decisions, not author-verified exact replication.
"""
from collections import defaultdict
from .io import read_rows, write_rows

CATS = ('overall','data','cyber')


def _prob(value, name):
    if value is None or str(value).strip() == '':
        raise ValueError(f'Missing probability {name}')
    x = float(value)
    if not 0 <= x <= 1:
        raise ValueError(f'Invalid probability {name}: {x}')
    return x


def risk_score(rows):
    risks = [_prob(x['prob_risk'],'prob_risk') for x in rows if x['predicted_label']=='risk']
    protective = [_prob(x['prob_mitigation'],'prob_mitigation') for x in rows
                  if x['predicted_label']=='mitigation']
    # If either type is absent, its corresponding statistic is defined as zero
    # for this implementation. This edge-case rule is NOT independently confirmed
    # from the paper's supplement; explicitly document it in methods.
    risk_max = max(risks, default=0.0)
    mitigation_mean = sum(protective) / len(protective) if protective else 0.0
    return max(0., risk_max - mitigation_mean)


def aggregate(input_csv, output_csv, universe_csv=None):
    groups = defaultdict(list)
    for row in read_rows(input_csv):
        firm, year = row['firm_id'].strip(), row['year'].strip()
        if not firm or not year:
            raise ValueError('firm_id/year required; use metadata mapping before aggregation')
        if row['predicted_label'] not in {'risk','mitigation','irrelevant'}:
            raise ValueError('Label must be risk, mitigation, or irrelevant')
        if row['predicted_label'] != 'irrelevant':
            # Validate both probabilities and their approximate normalization.
            pr, pm = _prob(row.get('prob_risk'), 'prob_risk'), _prob(row.get('prob_mitigation'), 'prob_mitigation')
            if abs(pr + pm - 1) > 0.02:
                raise ValueError('For a binary risk/mitigation model, probabilities must sum to one')
        groups[(firm,year)].append(row)
    # Fill missing candidate sets ONLY if the underlying MD&A was independently
    # checked. Otherwise absence of matched text might mean failed extraction.
    if universe_csv:
        for item in read_rows(universe_csv):
            firm, year = item['firm_id'].strip(), item['year'].strip()
            if not firm or not year:
                raise ValueError('Incomplete firm-year universe')
            if item.get('mda_verified','').strip().lower() not in ('1','true','yes'):
                raise ValueError(f'MD&A not verified for zero-fill: {firm} {year}')
            groups.setdefault((firm,year),[])
    out=[]
    for (firm, year), rows in sorted(groups.items()):
        def select(which):
            if which=='overall': return [r for r in rows if r['predicted_label'] != 'irrelevant']
            return [r for r in rows if r['predicted_label'] != 'irrelevant' and which in r.get('categories','').split('|')]
        out.append({'firm_id':firm,'year':year,
                    'digi_risk_exposure':round(risk_score(select('overall')),6),
                    'data_risk_exposure':round(risk_score(select('data')),6),
                    'cyber_risk_exposure':round(risk_score(select('cyber')),6),
                    'n_candidates':len(rows),
                    'n_risk':sum(r['predicted_label']=='risk' for r in rows),
                    'n_mitigation':sum(r['predicted_label']=='mitigation' for r in rows)})
    write_rows(output_csv, out, ['firm_id','year','digi_risk_exposure','data_risk_exposure',
                                 'cyber_risk_exposure','n_candidates','n_risk','n_mitigation'])
    return len(out)
