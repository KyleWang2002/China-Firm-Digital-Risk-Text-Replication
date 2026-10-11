"""Optional Chinese transformer training and calibrated-style probability export.

The fine-tuning is an independent implementation; it cannot reproduce the
original authors' FinBERT checkpoint without access to that model and labels.
"""
import argparse
import json
import random
from pathlib import Path
from .io import read_rows, write_rows

LABELS={'risk':0,'mitigation':1}

def _dependencies():
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
    except ImportError as exc:
        raise RuntimeError('Install optional ML requirements: pip install -e ".[model]"') from exc
    return torch, AutoTokenizer, AutoModelForSequenceClassification


def train(labels_csv, checkpoint, model_out, epochs=3, seed=42, max_length=192,
          batch_size=8, lr=2e-5, include_model_agreement=False):
    torch, Tokenizer, Model=_dependencies()
    accepted={'human_verified'}
    if include_model_agreement: accepted.add('model_agreement_unverified')
    rows=[r for r in read_rows(labels_csv)
          if r.get('final_label') in LABELS and r.get('review_status') in accepted
          and r.get('sentence','').strip()]
    if len(rows)<10:
        raise ValueError('At least 10 reviewed binary-labeled Chinese sentences are required; '
                         'the included synthetic fixture is NOT a training set')
    rng=random.Random(seed)
    rng.shuffle(rows)
    cut=max(1,min(len(rows)-1,int(.6*len(rows))))
    tr,valid=rows[:cut],rows[cut:]
    random.seed(seed); torch.manual_seed(seed)
    tok=Tokenizer.from_pretrained(checkpoint)
    model=Model.from_pretrained(checkpoint,num_labels=2,
        id2label={0:'risk',1:'mitigation'},label2id=LABELS,
        ignore_mismatched_sizes=True)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    optimizer=torch.optim.AdamW(model.parameters(),lr=lr)
    def batches(samples, shuffle):
        order=list(range(len(samples)))
        if shuffle: rng.shuffle(order)
        for start in range(0,len(order),batch_size):
            sub=[samples[i] for i in order[start:start+batch_size]]
            tokens=tok([r['sentence'] for r in sub],padding=True,truncation=True,
                       max_length=max_length,return_tensors='pt')
            tokens={k:v.to(device) for k,v in tokens.items()}
            tokens['labels']=torch.tensor([LABELS[r['final_label']] for r in sub],device=device)
            yield tokens
    metrics=[]
    for epoch in range(1,epochs+1):
        model.train();loss_sum=0.; n=0
        for batch in batches(tr,True):
            optimizer.zero_grad()
            loss=model(**batch).loss
            loss.backward()
            optimizer.step()
            loss_sum+=loss.item();n+=1
        model.eval(); correct=total=0
        with torch.no_grad():
            for batch in batches(valid,False):
                target=batch.pop('labels')
                pred=model(**batch).logits.argmax(dim=-1)
                correct+=(pred==target).sum().item();total+=len(target)
        metrics.append({'epoch':epoch,'train_loss_mean':loss_sum/max(n,1),
                        'validation_accuracy':correct/total if total else None,
                        'n_train':len(tr),'n_validation':len(valid)})
    out=Path(model_out); out.mkdir(parents=True,exist_ok=True)
    model.save_pretrained(out); tok.save_pretrained(out)
    (out/'training_manifest.json').write_text(json.dumps({
        'seed':seed,'source_checkpoint':checkpoint,'n_labeled':len(rows),
        'split':'sentence-level 60/40; not leakage-controlled by firm',
        'approved_statuses':sorted(accepted),'metrics':metrics,
        'warning':'Metrics are not evidence of reproducing Lu et al. (2025).'
    },ensure_ascii=False,indent=2),encoding='utf8')
    return metrics


def predict(candidates_csv, model_dir, output_csv, screening_csv=None,
            assume_all_relevant=False, batch_size=16, max_length=192):
    if not screening_csv and not assume_all_relevant:
        raise ValueError('Provide --screening-csv to filter irrelevant keywords, '
                         'or explicitly set --assume-all-relevant (exploratory only)')
    torch, Tokenizer, Model=_dependencies()
    tok=Tokenizer.from_pretrained(model_dir)
    model=Model.from_pretrained(model_dir)
    if model.config.num_labels!=2:
        raise ValueError('Expected a binary risk/mitigation classification model')
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device);model.eval()
    screen={}
    if screening_csv:
        for row in read_rows(screening_csv):
            key=(row.get('firm_id',''),row.get('year',''),row.get('filename',''),row['sentence_id'])
            label=row.get('final_label','').strip().lower()
            if label not in {'risk','mitigation','irrelevant'}:
                raise ValueError('Screening CSV requires final_label for every row')
            screen[key]=label
    incoming=list(read_rows(candidates_csv))
    eligible=[]; out=[]
    for row in incoming:
        key=(row.get('firm_id',''),row.get('year',''),row.get('filename',''),row['sentence_id'])
        if screening_csv and key not in screen:
            raise ValueError(f'Missing screening row for {key}')
        if screen.get(key)=='irrelevant':
            out.append({**row,'predicted_label':'irrelevant','prob_risk':'','prob_mitigation':''})
        else:
            eligible.append(row)
    for start in range(0,len(eligible),batch_size):
        subset=eligible[start:start+batch_size]
        inputs=tok([r['sentence'] for r in subset],padding=True,truncation=True,
                   max_length=max_length,return_tensors='pt')
        inputs={k:v.to(device) for k,v in inputs.items()}
        with torch.no_grad():
            probs=model(**inputs).logits.softmax(dim=-1).cpu().tolist()
        for row,pp in zip(subset,probs):
            out.append({**row,'predicted_label':'risk' if pp[0]>=pp[1] else 'mitigation',
                        'prob_risk':round(pp[0],8),'prob_mitigation':round(pp[1],8)})
    write_rows(output_csv,out,['firm_id','year','filename','sentence_id','categories',
                               'keywords','sentence','predicted_label',
                               'prob_risk','prob_mitigation'])
    return len(out)


def main(argv=None):
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='command',required=True)
    tr=sub.add_parser('train',help='fine-tune on human-reconciled Chinese sentences')
    tr.add_argument('--labels-csv',required=True);tr.add_argument('--checkpoint',required=True)
    tr.add_argument('--output-dir',required=True);tr.add_argument('--epochs',type=int,default=3)
    tr.add_argument('--include-model-agreement',action='store_true')
    pr=sub.add_parser('predict',help='export class probabilities for candidate sentences')
    pr.add_argument('--candidates-csv',required=True);pr.add_argument('--model-dir',required=True)
    pr.add_argument('--output-csv',required=True);pr.add_argument('--screening-csv')
    pr.add_argument('--assume-all-relevant',action='store_true')
    a=p.parse_args(argv)
    if a.command=='train':
        print(train(a.labels_csv,a.checkpoint,a.output_dir,a.epochs,
                    include_model_agreement=a.include_model_agreement))
    else:
        print(f'Predicted {predict(a.candidates_csv,a.model_dir,a.output_csv,a.screening_csv,a.assume_all_relevant)} rows')

if __name__=='__main__':main()
