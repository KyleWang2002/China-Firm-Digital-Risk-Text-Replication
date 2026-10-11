# Data dictionary

All CSVs are UTF-8 with a BOM for compatibility with spreadsheet applications. Keep `firm_id` (e.g. `000001`) as a **string** to preserve leading zeros. An Excel import can otherwise drop them.

| File / field | Meaning |
| --- | --- |
| `data/example/file_metadata.csv`: `filename` | TXT filename keyed to company-year |
| `firm_id` | Listing identifier, text, not numeric |
| `year` | Fiscal year, separate from annual-report publication date |
| `candidate_sentences.csv`: `sentence_id` | Sentence sequence **within one extracted MD&A file** |
| `categories` | `data`, `cyber`, and/or `technology`, separated with `\|` |
| `keywords` | Matching candidate terms, separated with `\|` |
| `sentence` | Exact retrieved candidate sentence after whitespace normalization |
| `annotation_queue.csv`: `model_a`, `model_b` | Assistant model labels (not automatically populated) |
| `human_review` | Manual adjudication label if supplied |
| `final_label` | `risk`, `mitigation`, or `irrelevant` |
| `review_status` | `human_verified`, `model_agreement_unverified`, or `needs_human_review` |
| `predicted_sentences.csv`: `prob_risk` | Probability from binary Chinese classifier that sentence reflects risk |
| `prob_mitigation` | Probability that sentence reflects risk-prevention activity |
| `digi_risk_exposure` | Overall maximum risk probability minus average mitigation probability, floor zero |
| `data_risk_exposure` | Same formula, on data-risk matched subset |
| `cyber_risk_exposure` | Same formula, on cyber-risk matched subset |
| `n_candidates`, `n_risk`, `n_mitigation` | Audit counts; not evidence of real firm-year values |

**Important:** If metadata is missing, the `index` command stops rather than inventing company identifiers. An extraction failure must not be coded as zero risk without further review. See `METHODS.md` for zero/missing convention limitations.
