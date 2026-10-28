"""Coverage requirements from the supplied September deck, not editorial limits."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from update_report import validate_report

class ProvidedReportTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=json.loads((ROOT/'data/provided-report.json').read_text())
 def test_macro_keeps_all_ten_metrics(self):
  metrics=[m for m in self.report['metrics'] if m['category']=='macro']
  self.assertEqual(len(metrics),10)
  for title in ['수출액','코스피','원/달러 환율','한은 경제전망','산업활동','한·미 기준금리','美 10년물 국채금리','美 PCE 물가','나스닥 종합지수','국제유가 (WTI)']:self.assertIn(title,[m['title'] for m in metrics])
 def test_macro_eighteen_issues_and_four_policies(self):
  self.assertEqual(sum(n['category']=='macro' for n in self.report['news']),18)
  self.assertEqual(sum(n['category']=='macro' for n in self.report['policies']),4)
  for page in range(11,20):self.assertEqual(sum(n['sourceSlide']==page for n in self.report['news']),2)
 def test_full_deck_and_original_images_are_preserved(self):
  self.assertEqual([s['page'] for s in self.report['slides']],list(range(1,46)))
  self.assertEqual(len(self.report['metrics']),36);self.assertEqual(len(self.report['news']),58)
  self.assertEqual(len(self.report['policies']),8);self.assertEqual(len(self.report['calendar']),20)
  slide3=next(s for s in self.report['slides'] if s['page']==3)
  self.assertEqual(len(slide3['images']),5)
  for slide in self.report['slides']:
   self.assertTrue(slide['paragraphs'])
   for image in slide.get('images',[]):self.assertTrue((ROOT/image).is_file())
 def test_five_overview_panels_cover_every_industry(self):
  self.assertEqual(len(self.report['sectorSummaries']),5)
  categories={cat for s in self.report['sectorSummaries'] for cat in s['categories']}
  self.assertEqual(categories,{s['id'] for s in json.loads((ROOT/'data/sectors.json').read_text())})
 def test_supplied_values_are_not_marked_independently_verified(self):
  for m in self.report['metrics']:self.assertEqual(m['verification'],'provided_unverified')
  for m in self.report['metrics']:
   if m['sourceSlide']==7:self.assertIn('활용 보류',m['reviewNote'])
 def test_official_report_has_no_arbitrary_news_cap(self):
  report=copy.deepcopy(json.loads((ROOT/'data/reports/2026-10.json').read_text()))
  original=next(n for n in report['news'] if n['category']=='macro')
  for i in range(20):
   extra=copy.deepcopy(original);extra['id']='extra-'+str(i);report['news'].append(extra)
  validate_report(report)
if __name__=='__main__':unittest.main()
