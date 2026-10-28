import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from publish_monthly import register_summary
class PublicationTests(unittest.TestCase):
 def setUp(self):
  self.index={'summaryReports':[{'id':'summary-2026-09-v5','path':'data/summary-report.json'}]}
  self.report={'month':'2026-10','cutoff':'2026-10-31','news':[{'id':'official'}]}
  self.status={'geminiSucceeded':True,'acceptedNewsUpdates':2,'acceptedMetricUpdates':0}
 def test_completed_run_becomes_default_and_retains_history(self):
  self.assertTrue(register_summary(self.index,self.report,self.status))
  self.assertEqual(self.index['summaryReports'][0]['month'],'2026-10')
  self.assertEqual(self.index['summaryReports'][1]['path'],'data/summary-report.json')
 def test_rerun_replaces_same_month_without_duplicate(self):
  register_summary(self.index,self.report,self.status);register_summary(self.index,self.report,self.status)
  self.assertEqual(len(self.index['summaryReports']),2)
 def test_no_key_or_failed_research_does_not_publish(self):
  self.status['geminiSucceeded']=False
  self.assertFalse(register_summary(self.index,self.report,self.status))
 def test_no_new_accepted_evidence_does_not_publish(self):
  self.status['acceptedNewsUpdates']=0
  self.assertFalse(register_summary(self.index,self.report,self.status))
 def test_incomplete_month_not_automatically_exposed(self):
  self.report['cutoff']='2026-10-28'
  self.assertFalse(register_summary(self.index,self.report,self.status))
 def test_empty_news_does_not_publish(self):
  self.report['news']=[]
  self.assertFalse(register_summary(self.index,self.report,self.status))
if __name__=='__main__':unittest.main()
