# Real annual-report processing examples (2024)

[中文版](CASE_STUDIES_zh.md) · [Main README](../README.md)

These are **examples from fiscal-year 2024 reports**, not observations in the paper's 2003–2022 estimation sample.

## Source catalog and screenshot

- Screenshot: [`figures/annual_report_catalog_2024.png`](../figures/annual_report_catalog_2024.png) (provided by the maintainer).
- Eight-row catalog: [`annual_report_catalog_2024_sample.csv`](../examples/real_2024/annual_report_catalog_2024_sample.csv), extracted from the larger supplied workbook. Stock codes are six-character strings.
- PDFs: Follow the source links; annual reports are not mirrored in this repository.

## Source / extracted section pairs

We selected short portions from the supplied **full-report TXT** and its accompanying **extracted MD&A TXT** for Ping An Bank (000001), Vanke A (000002), and Digital China (000034). They are visible in [`report_excerpts/`](../examples/real_2024/report_excerpts/).

**Extraction differences matter:** Vanke's 2024 filing uses a section titled “董事会报告” (Board Report) rather than a literal “管理层讨论与分析” chapter. The uploaded extracted section is included as a **provided output sample**, not proof that the package's default automatic heading detector would classify it correctly without customization. Individual reports may require manual review.

An additional example is [Junhe Pumps, stock code 603617, 2024 annual report](https://www.junhepumps.com/uploads/files/20250425/25a2c74842b20cb5c8ecc461b33be393.pdf) (company-hosted PDF; not copied). The supplied file is a **2025-04-25** version; public announcements also list a subsequent corrected 2024 annual report, so verify the version when using it for measurements.

## Keyword-matching table

[`keyword_screening_output_excerpt.csv`](../examples/real_2024/keyword_screening_output_excerpt.csv) is a faithful CSV conversion of 19 rows from the supplied `提取结果.xlsx` workbook, with source filenames, source-line numbers and candidate text. It contains **4 candidate lines** for Ping An Bank and **15** for Digital China. The uploaded sheet's source-line numbering has been preserved.

A candidate is not a validated security-risk disclosure. “黑客马拉松大赛” describes a hackathon in the Ping An Bank document and illustrates why human review or contextual classification is needed. Mentions of cloud computing and information security may likewise relate to commercial products, innovation or defensive capability rather than an observed incident.

No model labels or published risk estimates are inferred from these lines.

## From demo to full processing

1. Preserve the original PDF link, report fiscal year and file hash in your local data directory.
2. Convert PDF to TXT; check decoding, multi-column order, headers and missing pages.
3. Extract MD&A or equivalent management narrative and log the rule used.
4. Retrieve candidate sentences and manually adjudicate ambiguous phrases.
5. Generate probabilities with a trained, documented Chinese text model before calculating firm-year measures.

The repository includes only brief filing excerpts for illustration; the complete filings should be retrieved at their original sources under applicable terms.
