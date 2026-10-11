# Paper-to-code correspondence

Evidence: Lu, Shi & Zhou (2025), *经济研究* 2025(2), pp. 73–89; uploaded notebook files; and accompanying slide deck. The source notebooks are retained under `notebooks/` after removing stored outputs. Where a source feature has not been validated, status is explicit.

| Research step | Original article | Supplied materials | Public repository treatment |
| --- | --- | --- | --- |
| Sample | 2003–2022 Chinese A shares, 3,707 firms, 39,470 firm-years | 2024 annual-report link workbook, and one 2024 bank report used locally | Only a 3-row catalog excerpt; no false equivalence with 2003–2022 |
| Retrieval | Annual reports / MD&A | `1.年报抓取.ipynb`; `2.pdf下载与转码.ipynb` | `digirisk crawl/download/pdf-to-txt`; opt-in, conservative limits |
| MD&A | Management Discussion and Analysis | `3.MD&A提取.ipynb` | `digirisk extract-mda`, audited extraction; tested on local 296-page PDF |
| Dictionary | Table 1, data / cyber / technology risks, Word2Vec extension | `4. Word2Vec.ipynb`; `5.文本匹配提取.ipynb` | Reviewed seed CSV and optional *candidate* expansion; missing comma fixed |
| Labeling | GPT + ChatGLM + disagreement review, 10% annotated | No matching Chinese labeled file supplied | Human annotation spreadsheet protocol, not automatic GPT results |
| Sentiment | Chinese financial pretrained model / FinBERT | BERT/CNN/RNN experiments on English Financial PhraseBank | Experiments isolated; optional Chinese checkpoint trainer provided |
| Indices | Overall / data / cyber, max minus mean, lower bound zero | No complete final index or scored Chinese sentence corpus supplied | Correctly structured index function; synthetic unit test |
| Empirical analysis | Tobin's Q, governance, IV, suppliers/customers, reputation | Slides summarize the article but not statistical input/code | Not implemented; no fake regression findings |

## Important limitations

- The `README.md` included among the uploads contains the text and links of a third-party project, [legeling/Annualreport_tools](https://github.com/legeling/Annualreport_tools). Do **not** claim that text, images, or software as independently authored by the repository maintainer.
- The Word2Vec notebook describes a Baidu/Baike source while loading a file named `sgns.financial1.bigram-char` from a financial-text embedding family. This inconsistency should be resolved before publication; the public code requires the actual model path and does not claim it was used to produce verified expansions.
- The English TextCNN/RNN notebooks can contain data leakage (e.g. sentence splits and overlapping 75%/100% confidence groups). Their reported classification outcomes should **not** be presented as scientific performance without independently audited splits and data rights.
- The notebook `6.BERT.ipynb` includes shell syntax (`!pip install ...`) and a problematic `load_metric` call; it should not be automatically executed as part of CI.
- Real-model training/inference was not run during this packaging exercise; the CI tests cover only standard-library logic and fictional fixtures.
