"""Optional Word2Vec candidate expansion; never silently insert words into final lexicon."""
from .io import read_rows, write_rows


def propose_extensions(lexicon_file, vectors_path, output_csv, topn=5, min_similarity=.55):
    try: from gensim.models import KeyedVectors
    except ImportError as exc: raise RuntimeError('pip install -e ".[embedding]"') from exc
    model=KeyedVectors.load_word2vec_format(str(vectors_path),binary=False,unicode_errors='ignore')
    results=[]
    for row in read_rows(lexicon_file):
        word=row['keyword']
        if word not in model: continue
        for proposed, sim in model.most_similar(word,topn=topn):
            if sim>=min_similarity:
                results.append({'category':row['category'],'seed_keyword':word,
                                'candidate':proposed,'similarity':round(sim,4),
                                'human_accept':'','comment':'candidate_only'})
    write_rows(output_csv,results,['category','seed_keyword','candidate',
                                   'similarity','human_accept','comment'])
    return len(results)
