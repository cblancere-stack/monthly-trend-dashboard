import copy
from datetime import date
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from update_report import default_month,host_matches,month_bounds,validate_metric_proposal,validate_news,validate_report

class ReportTests(unittest.TestCase):
    def test_all_published_reports_and_index(self):
        index=json.loads((ROOT/"data/index.json").read_text())
        self.assertEqual(len({x["month"] for x in index["reports"]}),len(index["reports"]))
        for entry in index["reports"]:
            path=ROOT/entry["path"]
            self.assertTrue(path.resolve().is_relative_to((ROOT/"data/reports").resolve()))
            report=json.loads(path.read_text());self.assertEqual(entry["month"],report["month"]);validate_report(report)
    def test_month_boundary(self):
        self.assertEqual(default_month(date(2026,11,1)),"2026-10")
        self.assertEqual(default_month(date(2027,1,3)),"2026-12")
        self.assertEqual(month_bounds("2026-10",date(2026,10,28))[1],date(2026,10,28))
        with self.assertRaises(ValueError):month_bounds("2027-01",date(2026,10,28))
    def test_fake_host(self):
        self.assertFalse(host_matches("https://kbthink.com.evil.example/data",["kbthink.com"]))
        self.assertFalse(host_matches("http://kbthink.com/",["kbthink.com"]))
        self.assertFalse(host_matches("https://user:password@kbthink.com/",["kbthink.com"]))
    def metric(self):return copy.deepcopy(json.loads((ROOT/"data/reports/2026-10.json").read_text())["metrics"][0])
    def proposal(self):
        old=self.metric();text="9월 전국 주택 매매가격은 전월 대비 0.34% 상승했다."
        return old,text,{"id":"sale","source":old["source"],"current":.34,"previous":None,"period":"2026-09","published":"2026-10-15","unit":"%","scope":old["scope"],"evidenceCurrent":text}
    def test_value_mismatch_rejected(self):
        old,text,p=self.proposal();p["current"]=9.9
        with self.assertRaises(ValueError):validate_metric_proposal(p,old,text,date(2026,10,28))
    def test_wrong_provider_rejected(self):
        old,text,p=self.proposal();p["source"]={"name":"다른 기관","url":"https://www.reb.or.kr/"}
        with self.assertRaises(ValueError):validate_metric_proposal(p,old,text,date(2026,10,28))
    def test_future_publication_rejected(self):
        old,text,p=self.proposal();p["published"]="2026-11-15"
        with self.assertRaises(ValueError):validate_metric_proposal(p,old,text,date(2026,10,28))
    def test_unsupported_previous_not_invented(self):
        old,text,p=self.proposal();p.update(previous=8.88,previousPeriod="2026-08",evidencePrevious="not in source")
        result=validate_metric_proposal(p,old,text,date(2026,10,28))
        self.assertIsNone(result["previous"]);self.assertFalse(result["comparable"])
    def test_zero_not_missing(self):
        old,text,p=self.proposal();text="9월 전국 주택 매매가격 변동률은 0.00%로 보합이다.";p.update(current=0,evidenceCurrent=text)
        self.assertEqual(validate_metric_proposal(p,old,text,date(2026,10,28))["current"],0)
    def test_repeat_collection_preserves_verified_comparison(self):
        old,text,p=self.proposal()
        result=validate_metric_proposal(p,old,text,date(2026,10,28))
        self.assertEqual(result["previous"],old["previous"])
        self.assertTrue(result["comparable"])
    def test_revision_requires_comparison_evidence(self):
        old,text,p=self.proposal();p["current"]=.35
        text="9월 전국 주택 매매가격은 전월 대비 0.35% 상승했다."
        p["evidenceCurrent"]=text
        result=validate_metric_proposal(p,old,text,date(2026,10,28))
        self.assertIsNone(result["previous"])
    def test_news_unsupported_number_rejected(self):
        text="October 21, 2026. We released 3 new models for enterprise customers."
        n={"id":"n","category":"ai","published":"2026-10-21","headline":"출시","tag":"AI","stage":"공식 발표","track":"제공 범위","source":{"name":"Anthropic","url":"https://claude.com/resources/articles/claude-duet"},"facts":["모델 100개 출시"],"evidence":[text],"analysis":["선택 폭 확대 가능"]}
        with self.assertRaises(ValueError):validate_news(n,date(2026,10,1),date(2026,10,28),text)
    def test_no_placeholder_examples(self):
        metrics={x["id"]:x for x in json.loads((ROOT/"data/reports/2026-10.json").read_text())["metrics"]}
        for key in ("robo","indxx"):
            self.assertIsNone(metrics[key]["current"]);self.assertFalse(metrics[key]["comparable"])
    def test_extended_industry_coverage(self):
        report=json.loads((ROOT/"data/reports/2026-10.json").read_text())
        self.assertEqual({n["category"] for n in report["news"]},{"macro","realestate","mobility","defense","ai","robotics","battery","energy"})
        metrics={m["id"]:m for m in report["metrics"]}
        self.assertEqual(metrics["aa_cost_sol"]["scope"],"단일 모델 · GPT-6.1 Sol (max)")
        self.assertFalse(metrics["aa_cost_sol"]["comparable"])
        self.assertEqual(metrics["robo_return"]["unit"],"%")
        self.assertEqual(metrics["humanoid_sales"]["frequency"],"annual")
    def test_dedicated_metrics_cannot_be_changed_by_generated_proposals(self):
        report=json.loads((ROOT/"data/reports/2026-10.json").read_text())
        m=next(m for m in report["metrics"] if m["id"]=="aa_cost_sol")
        with self.assertRaises(ValueError):validate_metric_proposal({"id":m["id"]},m,"",date(2026,10,28))
if __name__=="__main__":unittest.main()
