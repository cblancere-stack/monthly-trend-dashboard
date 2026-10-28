"""Month-end observations preserve each configured instrument and price series."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from report_lifecycle import validate_summary
class MarketCloseTests(unittest.TestCase):
 def setUp(self):
  self.report=json.loads((ROOT/'data/summaries/2026-08.json').read_text())
  self.template=json.loads((ROOT/'data/report-template.json').read_text())
 def test_archived_closes_and_monthly_changes_match_both_reports(self):
  archive=json.loads((ROOT/'data/market-closes.json').read_text())
  values={x['date']:x['close'] for x in archive['observations']}
  for path in ['data/summaries/2026-08.json','data/summary-report.json']:
   report=json.loads((ROOT/path).read_text())
   metric=next(x for x in report['metrics'] if x['id']=='provided-m-7-25')
   close=metric['marketClose']
   self.assertEqual(close['seriesCode'],'IAIQP')
   self.assertEqual(metric['numericValue'],values[close['date']])
   self.assertEqual(close['previousClose'],values[close['previousDate']])
   self.assertAlmostEqual(close['changePct'],(close['close']/close['previousClose']-1)*100)
   self.assertIn('pt',metric['valueText'])
 def test_robo_close_and_change_are_consistent_in_both_months_and_overview(self):
  archive=json.loads((ROOT/'data/market-closes-robo.json').read_text())
  values={x['date']:x['close'] for x in archive['observations']}
  for path in ['data/summaries/2026-08.json','data/summary-report.json']:
   report=json.loads((ROOT/path).read_text())
   metric=next(m for m in report['metrics'] if m['id']=='provided-m-7-24')
   close=metric['marketClose']
   self.assertEqual(metric['title'],'ROBO')
   self.assertEqual(close['instrumentType'],'ETF')
   self.assertEqual(metric['numericValue'],values[close['date']])
   expected=(values[close['date']]/values[close['previousDate']]-1)*100
   self.assertAlmostEqual(close['changePct'],expected)
   self.assertIn(f'{expected:.2f}%',metric['deltaText'])
   self.assertNotIn('3개월',metric['deltaText'])
   self.assertNotIn('missingReason',metric)
   stats=[stat for group in report['sectorSummaries'] for stat in group['stats'] if 'ROBO' in stat[0]]
   self.assertEqual(stats,[['ROBO · 월말 종가',metric['valueText']]])
   self.assertFalse(any(x['id']==metric['id'] for x in report.get('researchAudit',{}).get('missingMetrics',[])))
 def test_next_day_market_close_allowed_but_news_still_rejected(self):
  validate_summary(self.report,self.template)
  self.report['news'][0]['published']='2026-09-01'
  with self.assertRaises(ValueError):validate_summary(self.report,self.template)
 def test_exception_rejects_wrong_series_or_delayed_publication(self):
  for change in [{'seriesCode':'AIQ'},{'currency':'EUR'}]:
   report=copy.deepcopy(self.report)
   next(m for m in report['metrics'] if m['id']=='provided-m-7-25')['marketClose'].update(change)
   with self.assertRaises(ValueError):validate_summary(report,self.template)
  metric=next(m for m in self.report['metrics'] if m['id']=='provided-m-7-25')
  metric['published']='2026-09-02'
  with self.assertRaises(ValueError):validate_summary(self.report,self.template)
if __name__=='__main__':unittest.main()
