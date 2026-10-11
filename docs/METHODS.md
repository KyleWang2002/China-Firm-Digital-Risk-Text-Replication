# Measurement workflow and assumptions

## A. Source document and sample

Lu, Shi, and Zhou (2025) study **A-share listed firms, 2003–2022**. The published paper reports **3,707 firms and 39,470 firm-year observations** after exclusions and winsorization. These are **paper-reported values**, not outputs reproduced here. The article reports financial data from CSMAR and Wind; these inputs are unavailable in the supplied materials.

The 2024 CNINFO link list and the 2024 Ping An Bank annual report were provided to test a **collection/processing process**, not as evidence of matching the article's sample. The 296-page PDF was inspected locally but is NOT redistributed.

## B. MD&A extraction

`src/digirisk/mda.py` finds strict section headings (e.g., `第三章 管理层讨论与分析`), continuing until the next major chapter. Multiple identical running headers are allowed. The extraction log records start/end lines, count of candidate headings, and status. **Every automatically extracted document is labeled `automatic_unverified`; it is never silently classified as hand checked.**

Typical failure modes: tables of contents, inconsistent section names, multi-column order, image-only annual reports, headers/footers, years with different disclosure templates. The test suite checks repeated heading behavior using a synthetic document. A local experiment on the user-provided bank report exposed and helped correct an early short-section truncation; that full report is not checked in.

## C. Keyword retrieval

The `data/lexicon/digital_risk_seed_keywords.csv` contains an **explicitly curated selection based on the categories in Lu et al. (2025), Table 1**. This is not a claim to transcribe every string in the table or authors' expanded dictionary. An uploaded source notebook had a missing comma between `"数据"` and `"窜改网页"` (Python would concatenate the literals); the new CSV avoids this bug.

Terms have `data`, `cyber` or `technology` categories. More generic seeds such as `数据` or `云计算` can boost candidate recall but also cause many false positives; they are **not included by default**, even though the article's footnote discusses widening candidate retrieval with word components. Our conservative lexical choice may miss true positives. Specific-technology terms contribute to the overall index, **not automatically** to both category indices.

Sentences containing keywords are **candidates**. No keyword match alone establishes actual risk exposure. Documents whose extraction fails must be reviewed rather than treated as no risk.

## D. Annotation protocol

Article description: randomly annotate **10%** of keyword-filtered sentences; use ChatGPT and ChatGLM for two tasks (risk exposure / preventive action); manually review disagreements or uncertainty. The supplied materials contain **no matching Chinese annotation corpus, API logs, adjudications, or positive-class distributions**.

Our queue supports `model_a`, `model_b`, `human_review`, `final_label`, `review_status`. Three possible labels: `risk`, `mitigation`, `irrelevant`. A disagreement requires human review. If models agree, that label is recorded with `model_agreement_unverified`—not portrayed as personally checked. The default Chinese trainer accepts **human_verified** only, unless `--include-model-agreement` is explicitly used. This is a scaffold, not proof of faithful implementation of the authors' full annotation procedure.

## E. Model training

The article describes a 60/40 training/validation split after labeling and fine-tuning a Chinese financial-language model (exact architecture and parameters are specified partly in a journal supplement not supplied here). Our optional script uses a user-chosen Hugging Face checkpoint, two class labels (`risk=0`, `mitigation=1`) and a seeded 60/40 split.

The earlier `6.BERT.ipynb` uses `bert-base-uncased`, English Financial PhraseBank sentences and a three-class `negative/neutral/positive` setup. It also contains a Jupyter shell command and some incomplete cells. **It is not the Chinese FinBERT used by Lu et al.** Similar limitations apply to the TextCNN/RNN demonstrations. The package does not ship the author's model weights, and has no measured out-of-sample Chinese classification accuracy.

When a candidate sentence is irrelevant, screen it out before probability prediction by supplying a completed annotation CSV. Without that file, `predict --assume-all-relevant` is allowed only for exploratory work and will force all matched sentences into a binary class.

## F. Firm-year exposure score

The original article (pp. 78–79) defines exposure as the largest negative sentiment probability among risk-exposure statements, minus the **mean** positive sentiment probability of statements about risk prevention, floored at zero:

\[
E_{it}=\max\left\{0,\ \max_{s \in R_{it}}p_{\mathrm{risk},s}-\frac{1}{|P_{it}|}\sum_{s\in P_{it}}p_{\mathrm{prevention},s}\right\}.
\]

- `R_it`: sentences classified as exposure to a digital-technology risk.
- `P_it`: sentences classified as actions preventing such risks.
- `Digi_Risk_Exposure`: overall matching set.
- `Data_Risk_Exposure`: subset with data-security terms.
- `Cyber_Risk_Exposure`: subset with network/cybersecurity terms.

**Implementation assumption requiring author-supplement verification:** when a class is absent, its corresponding statistic is set to zero; when reviewed statements are all irrelevant, the exposure index is zero. If there are no keyword-matched candidate sentences at all, the firm-year is absent unless an independently verified MD&A firm-year universe is explicitly supplied using `--universe-csv` (`firm_id,year,mda_verified`). This avoids silently coding failed extraction as no risk. The supplied paper text specifies clipping negative differences to zero, but does not clearly spell out every missing-class case. Revisit this rule before empirical use.

The toy fixture deliberately gives a risk maximum 0.93 and preventive mean (0.92+0.85)/2=0.885; the resulting illustrative overall score is **0.045**. This is **fictional** arithmetic, not an estimate for a listed firm.

## G. What remains outside the repository

To reproduce the full article, researchers would still need: the precise expanded keyword list and supplemental model setup, complete 2003–2022 MD&A, reviewed Chinese sentence labels, original/specified pretrained model, firm-year match keys, CSMAR/Wind data, supply-chain/network data, US industry instruments, winsorization rules, and complete econometric specifications. **No firm-value effect, IV estimate or mechanism test is calculated here.**

## H. Real 2024 processing examples

See [Case studies (English)](CASE_STUDIES.md) or [案例说明（中文）](CASE_STUDIES_zh.md). The repository includes a screenshot, original source URLs, paired short annual-report/MD&A excerpts, and 19 keyword-matched candidates from a user-supplied workbook. These examples are separate from synthetic probability/index fixtures.
