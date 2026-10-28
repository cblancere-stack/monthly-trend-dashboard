"""Keep topic coverage while changing the reading experience, not the topic count."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SummaryReportTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.summary=json.loads((ROOT/'data/summary-report.json').read_text())
  cls.original=json.loads((ROOT/'data/provided-report.json').read_text())
 def test_all_topic_ids_retained(self):
  for key in ['metrics','news','policies']:
   self.assertEqual([x['id'] for x in self.summary[key]],[x['id'] for x in self.original[key]])
 def test_each_issue_has_short_structured_summary(self):
  for n in self.summary['news']:
   self.assertTrue(n['facts']);self.assertTrue(n['analysis']);self.assertTrue(n['track'])
   self.assertLess(sum(map(len,n['facts']))+len(n['analysis'])+len(n['track']),290)
   self.assertNotIn('originalLines',n)
 def test_policies_only_need_content_and_analysis(self):
  for n in self.summary['policies']:
   self.assertTrue(n['content']);self.assertTrue(n['analysis']);self.assertNotIn('originalLines',n)
 def test_reading_payload_excludes_original_deck(self):
  self.assertNotIn('slides',self.summary);self.assertNotIn('coverage',self.summary)
  for group in self.summary['sectorSummaries']:self.assertNotIn('image',group)
  self.assertNotIn('original-slides',(ROOT/'index.html').read_text())
  self.assertNotIn('providedReports',json.loads((ROOT/'data/index.json').read_text()))
 def test_all_calendar_entries_remain_reachable(self):
  self.assertEqual(len(self.summary['calendar']),20)
  for item in self.summary['calendar']:self.assertTrue(item['categories'])
if __name__=='__main__':unittest.main()
