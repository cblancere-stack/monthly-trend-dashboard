import copy,json,sys,tempfile,unittest
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from report_lifecycle import save_summary,validate_summary
class LifecycleTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  (self.root/'data').mkdir();self.template=json.loads((ROOT/'data/report-template.json').read_text())
  (self.root/'data/report-template.json').write_text(json.dumps(self.template))
  (self.root/'data/summary-report.json').write_text('September must remain unchanged')
  (self.root/'data/index.json').write_text(json.dumps({'summaryReports':[{'id':'summary-2026-09-v5','path':'data/summary-report.json'}]}))
  source={'name':'기관','url':'https://www.bok.or.kr/official-release'}
  self.report={'kind':'summary','origin':'independent','month':'2026-10','asOf':'2026-11-05','cutoff':'2026-11-05','headline':'월간 변화','metrics':[{**m,'valueText':'1','basis':'10월 실적 · 11월 5일 발표','meaning':'정의','impact':'영향','deltaText':'전월과 동일','frequency':'monthly','period':'2026-10','published':'2026-11-05','source':source} for m in self.template['requiredMetricSlots']],'news':[],'policies':[],'supplements':[],'calendar':[],'sectorSummaries':self.template['overviewGroups'],'sectorCoverage':{s['id']:'공식자료 조사 범위 기록' for s in self.template['sectors']}}
 def test_initial_then_enrichment_retains_september_and_first_publication(self):
  path=save_summary(self.root,self.report,date(2026,11,5));self.assertEqual(json.loads(path.read_text())['phase'],'initial')
  self.report['asOf']='2026-11-10';save_summary(self.root,self.report,date(2026,11,10))
  saved=json.loads(path.read_text());self.assertEqual(saved['firstPublishedAt'],'2026-11-05');self.assertEqual(saved['phase'],'enriched');self.assertEqual(len(saved['revisions']),2)
  self.assertEqual((self.root/'data/summary-report.json').read_text(),'September must remain unchanged')
  entries=json.loads((self.root/'data/index.json').read_text())['summaryReports'];self.assertEqual(len(entries),2);self.assertEqual(entries[0]['month'],'2026-10')
 def test_tenth_can_publish_if_fifth_failed(self):
  self.report['asOf']='2026-11-10';path=save_summary(self.root,self.report,date(2026,11,10));self.assertEqual(json.loads(path.read_text())['firstPublishedAt'],'2026-11-10')
 def test_cannot_silently_drop_indicators(self):
  self.report['metrics'].pop()
  with self.assertRaises(ValueError):validate_summary(self.report,self.template)
 def test_missing_value_requires_reason_and_checked_sources(self):
  m=self.report['metrics'][0];m.update(dataStatus='not_released',valueText='최근 발표 확인 중');m.pop('source')
  with self.assertRaises(ValueError):validate_summary(self.report,self.template)
  m.update(missingReason='당월 통계 미발표',checkedSources=['https://www.bok.or.kr/'])
  validate_summary(self.report,self.template)
 def test_future_source_rejected(self):
  self.report['metrics'][0]['published']='2026-11-11'
  with self.assertRaises(ValueError):validate_summary(self.report,self.template)
 def test_failure_leaves_history_untouched(self):
  self.report['month']='2026-09'
  with self.assertRaises(ValueError):save_summary(self.root,self.report,date(2026,11,5))
  self.assertEqual((self.root/'data/summary-report.json').read_text(),'September must remain unchanged')
 def test_historical_publication_is_explicit_and_preserves_latest(self):
  r=copy.deepcopy(self.report);r.update(month='2026-08',asOf='2026-08-31',cutoff='2026-08-31',revisionNote='Requested historical report')
  for m in r['metrics']:m.update(period='2026-07',published='2026-08-20')
  with self.assertRaises(ValueError):save_summary(self.root,r,date(2026,10,28))
  path=save_summary(self.root,r,date(2026,10,28),historical=True)
  saved=json.loads(path.read_text());self.assertEqual(saved['firstPublishedAt'],'2026-10-28');self.assertEqual(saved['cutoff'],'2026-08-31');self.assertEqual(saved['publicationMode'],'historical')
  entries=json.loads((self.root/'data/index.json').read_text())['summaryReports'];self.assertEqual(entries[0]['path'],'data/summary-report.json')
  self.assertEqual((self.root/'data/summary-report.json').read_text(),'September must remain unchanged')
 def test_historical_mode_cannot_publish_current_month_or_future_cutoff(self):
  r=copy.deepcopy(self.report);r.update(month='2026-10',asOf='2026-10-28',revisionNote='Historical request')
  with self.assertRaises(ValueError):save_summary(self.root,r,date(2026,10,28),historical=True)
  r.update(month='2026-08',asOf='2026-10-29')
  with self.assertRaises(ValueError):save_summary(self.root,r,date(2026,10,28),historical=True)
 def test_calendar_and_related_citations_cannot_leak_future_information(self):
  r=copy.deepcopy(self.report);r['calendar']=[{'source':{'name':'主催','url':'https://example.com/event','published':'2026-11-06'}}]
  with self.assertRaises(ValueError):validate_summary(r,self.template)
  r=copy.deepcopy(self.report);r['metrics'][0]['sources']=[{'name':'기관','url':'https://example.com/release','published':'2026-11-06'}]
  with self.assertRaises(ValueError):validate_summary(r,self.template)
if __name__=='__main__':unittest.main()
