import csv
import tempfile
import unittest
from pathlib import Path
from digirisk.mda import extract_mda, batch_extract
from digirisk.lexicon import load_terms, batch_match
from digirisk.score import risk_score, aggregate
from digirisk.annotation import reconcile
from digirisk.io import write_rows, read_rows

R=Path(__file__).resolve().parents[1]

class PipelineTests(unittest.TestCase):
    def test_extract_mda_and_no_toc(self):
        src=(R/'data/example/fictional_2020.txt').read_text(encoding='utf8')
        x=extract_mda(src,minimum_chars=60)
        self.assertIn('数据泄露', x['text'])
        self.assertNotIn('以上为演示数据',x['text'])
    def test_no_section_is_flagged(self):
        self.assertEqual(extract_mda('这是简短的无章节测试')['status'],'needs_manual_review')
    def test_full_toy_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)
            audit=batch_extract(R/'data/example',dest/'mda',minimum_chars=60)
            self.assertEqual(sum(x['status']=='automatic_unverified' for x in audit),2)
            count=batch_match(dest/'mda',R/'data/lexicon/digital_risk_seed_keywords.csv',
                              dest/'candidates.csv',R/'data/example/file_metadata.csv')
            self.assertGreaterEqual(count,4)
            queue_path=dest/'queue.csv'
            from digirisk.annotation import annotation_queue
            self.assertEqual(annotation_queue(dest/'candidates.csv',queue_path),count)
            for row in read_rows(dest/'candidates.csv'):
                self.assertEqual(row['firm_id'],'999999')
    def test_formula_and_floor(self):
        rows=[{'predicted_label':'risk','prob_risk':'0.93'},
              {'predicted_label':'mitigation','prob_mitigation':'0.92'},
              {'predicted_label':'mitigation','prob_mitigation':'0.85'}]
        self.assertAlmostEqual(risk_score(rows),.045)
        self.assertEqual(risk_score([{'predicted_label':'risk','prob_risk':'0.15'},
                                     {'predicted_label':'mitigation','prob_mitigation':'0.90'}]),0.)
    def test_aggregated_sample(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'index.csv'
            self.assertEqual(aggregate(R/'data/example/illustrative_scored_sentences.csv',out),2)
            rows=list(read_rows(out))
            self.assertAlmostEqual(float(rows[0]['digi_risk_exposure']),.045)
            self.assertEqual(rows[0]['firm_id'],'999999')
            self.assertEqual(rows[0]['year'],'2020')
    def test_repeated_chapter_headers_are_not_terminal(self):
        report = ('第三章 管理层讨论与分析\n' + '经营情况稳定。'*80
                  + '\n第三章 管理层讨论与分析\n' + '信息安全得到加强。'*80
                  + '\n第四章 公司治理\n' + 'Should not appear')
        extraction=extract_mda(report,minimum_chars=150)
        self.assertIn('信息安全得到加强',extraction['text'])
        self.assertNotIn('Should not appear',extraction['text'])
    def test_zero_fill_only_for_reviewed_mda(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/'universe.csv'
            write_rows(f,[{'firm_id':'000001','year':'2022','mda_verified':'true'}],
                       ['firm_id','year','mda_verified'])
            out=Path(tmp)/'out.csv'
            aggregate(R/'data/example/illustrative_scored_sentences.csv',out,f)
            rows=list(read_rows(out))
            added=[r for r in rows if r['firm_id']=='000001'][0]
            self.assertEqual(added['digi_risk_exposure'],'0.0')
            write_rows(f,[{'firm_id':'000001','year':'2022','mda_verified':'false'}],
                       ['firm_id','year','mda_verified'])
            with self.assertRaises(ValueError):
                aggregate(R/'data/example/illustrative_scored_sentences.csv',out,f)
    def test_disagreement_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'in.csv',Path(tmp)/'out.csv'
            write_rows(a,[{'model_a':'risk','model_b':'mitigation','human_review':'',
                            'firm_id':'A'}],['model_a','model_b','human_review','firm_id'])
            self.assertEqual(reconcile(a,b),(1,1))
            self.assertEqual(list(read_rows(b))[0]['review_status'],'needs_human_review')

if __name__=='__main__':unittest.main()
