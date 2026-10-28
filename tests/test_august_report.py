"""Historical report checks: chronology, preserved tracking slots, and sources."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from report_lifecycle import validate_summary
class AugustReportTests(unittest.TestCase):
 def setUp(self):
  self.report=json.loads((ROOT/'data/summaries/2026-08.json').read_text())
  self.template=json.loads((ROOT/'data/report-template.json').read_text())
 def test_historical_report_covers_all_sectors_and_preserves_indicator_slots(self):
  validate_summary(self.report,self.template)
  self.assertEqual(self.report['cutoff'],'2026-08-31')
  self.assertGreater(self.report['firstPublishedAt'],self.report['cutoff'])
  for sector in self.template['sectors']:
   self.assertGreaterEqual(sum(n['category']==sector['id'] for n in self.report['news']),4)
 def test_unavailable_values_are_explained_without_example_numbers(self):
  for m in self.report['metrics']:
   if m.get('dataStatus')=='unavailable':
    self.assertNotIn('numericValue',m)
    self.assertTrue(m['checkedSources']);self.assertTrue(m['displayNote'])
  self.assertFalse(any(m['valueText'] in ['185.4 pt','2,450 pt','1,350 pt','$1.80'] for m in self.report['metrics']))
 def test_period_and_announcement_are_not_confused(self):
  metrics={m.get('replaces',m['id']):m for m in self.report['metrics']}
  self.assertEqual(metrics['provided-m-5-12']['period'],'2026-07')
  self.assertEqual(metrics['provided-m-5-12']['published'],'2026-08-31')
  self.assertEqual(metrics['provided-m-4-7']['period'],'2026-08-28')
  self.assertAlmostEqual(metrics['provided-m-6-23']['numericValue'],5330/21075*100,places=1)
  self.assertTrue(all(n['published'].startswith('2026-08') for n in self.report['news']))
 def test_index_retains_september_first_and_august_selectable(self):
  index=json.loads((ROOT/'data/index.json').read_text())['summaryReports']
  paths=[e['path'] for e in index]
  self.assertIn('data/summary-report.json',paths)
  self.assertLess(paths.index('data/summary-report.json'),paths.index('data/summaries/2026-08.json'))
  self.assertTrue(any(e['path']=='data/summaries/2026-08.json' for e in index))
