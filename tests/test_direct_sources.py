from pathlib import Path
import sys
import unittest
from datetime import date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from direct_sources import parse_smp,parse_aa,parse_robo,parse_motir,update_metric,collect_direct

class AdapterTests(unittest.TestCase):
 def test_integrated_smp_not_mainland(self):
  html='<table><tr><th rowspan="2">육지 SMP</th><td>25년</td><td>999</td></tr><tr><td>26년</td><td>998</td></tr><tr><th rowspan="2">통합 SMP</th><td>25년</td><td>10</td><td>11</td></tr><tr><td>26년</td><td>12</td><td>13</td></tr></table>'
  self.assertEqual(parse_smp(html,'2026-02'),13)
  with self.assertRaises(ValueError):parse_smp(html,'2026-03')
 def test_robo_price_return_not_net_total_return(self):
  day,value,ytd=parse_robo('Index fact sheet as of September 30, 2026 Net Total Return -5.2% 19.8% 17.1% Price Return -5.4% 19.2% 16.3%')
  self.assertEqual(str(day),'2026-09-30');self.assertEqual(value,-5.4);self.assertEqual(ytd,16.3)
 def test_exact_aa_model_and_cost_column(self):
  html='<table><tr><th>Model</th><th>Intelligence</th><th>Cost per Task USD</th></tr><tr><td>GPT-6.1 Sol (high)</td><td>50</td><td>$0.32</td></tr><tr><td>GPT-6.1 Sol (max)</td><td>52</td><td>$0.72</td></tr></table>'
  self.assertEqual(parse_aa(html),.72)
  with self.assertRaises(ValueError):parse_aa(html.replace('Cost per Task USD','Price per million tokens'))
 def test_motir_rounding_units_and_publication(self):
  text='<p>2026년 9월 자동차산업 동향 등록일 2026-10-19</p><p>자동차 수출이 금액 기준으로 전년 동월 대비 5.5% 감소한 60.5억 달러, 내수는 13.5만대, 생산은 34.7만대로 집계되었다.</p>'
  published,period,values=parse_motir(text,'auto')
  self.assertEqual(period,'2026-09');self.assertEqual(values,dict(auto_exports=60.5,auto_domestic=13.5,auto_production=34.7))
  with self.assertRaises(ValueError):parse_motir(text.replace('등록일 2026-10-19',''),'auto')
 def test_revision_and_new_period_drop_stale_yoy(self):
  m=dict(current=1,period='2026-08',reportedChange=5,reportedChangeLabel='전년 대비',previous=.5,previousPeriod='2026-07',comparable=True,source={'name':'x','url':'https://example.com'})
  revised=update_metric(m,2,'2026-08','https://example.com','x')
  self.assertFalse(revised['comparable']);self.assertNotIn('reportedChange',revised)
  advanced=update_metric(m,3,'2026-09','https://example.com','x')
  self.assertEqual(advanced['previous'],1);self.assertNotIn('reportedChange',advanced)
 def test_reviewed_release_fallback_cannot_become_next_month_data(self):
  old=dict(id='exports',current=1209.4,period='2026-09',source={'name':'산업통상부','url':'https://www.motir.go.kr/kor/article/ATCL3f49a5a8c/172254/view'})
  def read(url,domains):
   if url==old['source']['url']:return '<p>2026년 9월 수출입 동향 등록일 2026-10-01 수출은 83.5% 증가한 1,209.4억 달러</p>','text/html'
   return '<html>목록에 해당 제목 없음</html>','text/html'
  updates,issues=collect_direct([old],'2026-10',date(2026,10,28),date(2026,10,28),read)
  self.assertEqual(len(updates),1);self.assertFalse(issues)
  updates,issues=collect_direct([old],'2026-11',date(2026,11,30),date(2026,11,30),read)
  self.assertFalse(updates)
if __name__=='__main__':unittest.main()
