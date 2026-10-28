"""Create the explicitly dated starting snapshots. Never run from scheduled workflows."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def source(name, url):
    return {"name": name, "url": url}

KB = "https://kbthink.com/realestate/insights/research/"
MOLIT = source("국토교통부", "https://www.korea.kr/briefing/pressReleaseView.do?newsId=156783581")
def metric(id, title, category, src, period, current, previous, previous_period, unit, digits, meaning, impact, **kwargs):
    return dict(id=id,title=title,category=category,source=src,period=period,current=current,
                previous=previous,previousPeriod=previous_period,unit=unit,digits=digits,
                signed=unit=="%",deltaType="pp" if unit=="%" else "percent",
                comparable=current is not None and previous is not None,
                status="verified" if current is not None else "unverified",fresh=True,
                scope="전국 · 전체 주택" if category=="realestate" else "글로벌",
                meaning=meaning,impact=impact,**kwargs)

def base_metrics():
    return [
      metric("sale","주택 매매가격 변동률","realestate",source("KB국민은행",KB+"261015-2.html"),"2026-09",.34,.27,"2026-08","%",2,"전국 주택 매매가격의 월간 변화율. 가격 방향과 상승 속도를 추적합니다.","전국 상승폭은 확대됐지만, 매입 판단은 지역별 거래 흐름과 함께 확인할 필요가 있습니다."),
      metric("transactions","주택 매매거래량","realestate",MOLIT,"2026-08",48359,63185,"2026-07","건",0,"신고된 주택 매매 건수로 실제 거래 활동과 시장 유동성을 추적합니다.","거래 부진이 이어지면 부동산 매각과 투자금 회수에 시간이 더 걸릴 수 있습니다."),
      metric("rent","주택 전세가격 변동률","realestate",source("KB국민은행",KB+"261015-4.html"),"2026-09",.32,.30,"2026-08","%",2,"전국 주택 전세가격의 월간 변화율. 임대시장 수급 변화를 추적합니다.","신규·갱신 계약의 보증금 부담과 지역별 임대 수요를 함께 점검할 필요가 있습니다."),
      metric("unsold_completed","준공 후 미분양","realestate",MOLIT,"2026-08",28080,29152,"2026-07","호",0,"완공 이후에도 팔리지 않은 주택 수. 완공 주택의 재고 위험을 추적합니다.","재고 감소는 긍정적이나 지역·사업별 분양대금 회수 위험은 별도로 확인해야 합니다."),
      metric("arena","Arena AI 응답 평가점수","ai",source("Arena", "https://arena.ai/leaderboard/chat/text"),"2026-10-22",1517,None,None,"pt",0,"블라인드 비교 평가에 기반한 Text Overall 응답 선호도. 절대적인 지능 점수는 아닙니다.","업무 적합성은 응답 선호도 외에 정확도·비용·보안 조건을 함께 평가해야 합니다.",note="Gemini 4 Argon (High) · 1,517 ±7점. 전월 원자료 미확인."),
      metric("aa_cost","Artificial Analysis AI 비용","ai",source("Artificial Analysis","https://artificialanalysis.ai/trends"),None,None,None,None,"USD/task",2,"고정된 성능 기준을 충족하는 AI의 평가 과제당 비용. 토큰 단가·총소유비용과 구분합니다.","성능 문턱·평가 버전이 같아야 비용 하락을 비교할 수 있습니다.",note="성능 기준별 원자료 연결 대기. 단일 모델 가격을 시장 평균으로 대체하지 않습니다."),
      metric("robo","ROBO 로봇·자동화 지수","robotics",source("VettaFi","https://www.vettafi.com/indexing/index/robo"),None,None,None,None,"pt",1,"글로벌 로봇·자동화 상장기업의 주가 흐름. 휴머노이드 생산량이나 직접 자금 유입을 뜻하지 않습니다.","관련 산업에 대한 시장 평가와 투자 기대의 변화를 보여줍니다.",note="같은 수익률 유형의 월말 원지수 값 연결 대기. ETF 가격으로 대체하지 않습니다."),
      metric("indxx","Indxx AI·빅데이터 지수","ai",source("Indxx","https://www.indxx.com/index/indxx-artificial-intelligence-big-data-index"),None,None,None,None,"pt",2,"AI 소프트웨어·서비스·하드웨어 관련 상장기업의 시장 평가를 추적합니다.","주가 변화는 기대를 반영하며 실제 설비투자·수주 실적과 구분해 읽어야 합니다.",note="기준일이 확인된 최신 원지수 값 연결 대기. 과거 페이지 값을 최신값으로 사용하지 않습니다.")
    ]

def news(id, category, tag, date, stage, headline, facts, analysis, track, src):
    return dict(id=id,category=category,tag=tag,published=date,stage=stage,headline=headline,
                facts=facts,analysis=analysis,track=track,source=src,review="manual",verification="source_reviewed")

oct_news = [
 news("re-sale","realestate","매매시장","2026-10-15","통계 발표","수도권 중심 가격 상승 확대, 지역별 온도 차는 지속",["9월 전국 주택 매매가격 +0.34%. 8월 +0.27%보다 상승폭 확대.","수도권 +0.68%, 5개 광역시 +0.01%, 기타 지방 +0.04%.","수원 영통구 +3.96%, 서울 노원구 +2.32% 등 일부 지역에서 높은 상승률."],["전국 평균 상승을 모든 지역의 시장 회복으로 확대 해석하기는 어렵습니다.","대상지의 실제 거래가격과 거래 빈도를 함께 확인할 필요가 있습니다."],"10월 가격 변화, 지역별 거래량, 고가·중저가 지역의 차별화",source("KB경영연구소",KB+"261015-2.html")),
 news("re-rent","realestate","전세시장","2026-10-15","통계 발표","전셋값 상승폭 확대, 매물 부족과 이사 수요가 부담",["9월 전국 전세가격 +0.32%. 전월 +0.30% 대비 상승폭 확대.","수도권 +0.56%, 서울 +0.64%, 경기 +0.59%.","KB전세가격전망지수는 9월 120.7."],["입주물량 감소와 계약갱신 증가는 신규 전세 매물 공급을 제약할 수 있습니다.","정비사업 이주 수요가 겹치는 지역은 임대가격 부담이 커질 가능성이 있습니다."],"전세 매물, 정비사업 이주, 신규 입주물량",source("KB경영연구소",KB+"261015-4.html")),
 news("re-presales","realestate","분양시장","2026-10-15","통계 발표","분양 2.4만 호로 증가했지만 청약경쟁률은 하락",["9월 전국 아파트 분양 약 2.4만 호, 전월 대비 +25.2%.","수도권 분양은 전월 대비 -5.5%, 비수도권은 +88.1%.","전국 1순위 청약경쟁률은 8월 2.9대 1에서 9월 1.8대 1로 하락."],["분양물량 증가가 수요 회복을 의미하지는 않습니다.","입지·분양가에 따라 실제 계약과 자금 회수 결과가 달라질 수 있습니다."],"신규 단지 계약률, 미분양, 할인·분양조건",source("KB경영연구소",KB+"261015-6.html")),
 news("re-finance","realestate","주택금융","2026-10-15","통계 발표","주담대 금리 4.66%, 대출 증가 둔화 속 차입 부담",["8월 신규취급 주택담보대출 금리 4.66%, 전월 대비 +0.18%p.","9월 은행권 주택담보대출 잔액 955.5조 원, 월 증가액 2.9조 원.","9월 전세자금대출 잔액 161.2조 원, 전월 대비 0.9조 원 감소."],["금리 상승은 매수자의 구매 여력을 제약할 수 있습니다.","차입 투자에서는 매입가격과 함께 보유기간의 금융비용을 점검해야 합니다."],"신규 대출금리, 은행 취급 여건, 대출 증가액",source("KB경영연구소",KB+"261015-7.html")),
 news("ai-duet","ai","AI 에이전트","2026-10-21","연구 프리뷰","Claude Duet, 질문에 답하는 AI에서 먼저 챙기는 비서로",["Anthropic이 연결된 앱을 확인하고 필요한 사항을 먼저 알리는 Claude Duet 공개.","미국 Pro·Max 가입자 대상 대기명단 방식의 연구 프리뷰로 시작.","모바일·웹에서 제공하며, 사용자 대신 행동하기 전 확인하는 방식 제시."],["문서 작성 지원에서 정보 확인과 후속 업무 실행까지 서비스 범위가 확대됩니다.","업무 완수율뿐 아니라 실행 권한·오작동·승인 절차도 평가해야 합니다."],"국내 제공 여부, 연결 앱, 실행 권한, 업무당 비용",source("Anthropic","https://claude.com/resources/articles/claude-duet")),
 news("ai-cloud","ai","기업용 AI","2026-10-21","비공개 프리뷰","Google Cloud에 OpenAI 모델, 기업의 모델 선택권 확대",["Google Cloud 모델 가든에 GPT-6 Astra·GPT-6.1 Sol·GPT-6 Luna 도입 발표.","일부 기업 고객 대상 비공개 프리뷰로 시작.","Marketplace 통합 청구와 기존 클라우드 약정 사용 지원."],["기업은 업무별 성능·속도·비용에 따라 모델을 선택할 수 있습니다.","모델 선택 폭이 넓어져도 데이터 보관·접근 권한·계약 검토는 필요합니다."],"정식 출시, 국내 제공 지역, 가격·데이터 보관 조건",source("Google Cloud","https://cloud.google.com/blog/products/ai-machine-learning/google-cloud-brings-openai-models-to-customers")),
 news("robot-tesla","robotics","Optimus","2026-10-21","기업 실적 발표","Tesla, Optimus 초기 생산 개시…상용성 검증은 별도",["3분기 실적자료에서 프리몬트 Optimus 생산 개시 발표.","해당 라인에서 제품 수준의 로봇을 생산했다고 회사 측 설명.","생산능력 표에는 초기 증산 단계로 기재하고 연간 생산능력 수치는 미제시."],["생산 개시와 외부 고객 납품·현장 생산성 확보는 구분해야 합니다.","목표 생산량보다 실제 납품·가동·작업 성공률 확인이 중요합니다."],"생산·납품 대수, 고객 확보, 현장 가동시간·유지보수",source("Tesla IR","https://assets-ir.tesla.com/tesla-contents/IR/TSLA-Q3-2026-Update.pdf")),
 news("robot-agco","robotics","제조현장 실증","2026-10-20","상업적 협약","AGCO·Agility, 부품 분류·적재 공정에 Digit 실증 추진",["AGCO와 Agility가 미국 캔자스주 헤스턴 공장 실증을 위한 협약 체결.","2027년 실증 시작 예정. 부품 분류·적재와 운반용 상자 배치 등을 검토.","Agility는 기존 Digit의 실제 운영 경험을 누적 65,000시간 이상이라고 발표."],["제조업 적용은 구체적인 반복 작업 중심으로 확대되는 흐름입니다.","회사 누적 운영시간은 해당 공장 성과나 산업 전체 실적이 아닙니다."],"실증 개시, 투입 대수, 처리량, 사람 개입 빈도",source("Agility Robotics","https://www.agilityrobotics.com/content/agco-and-agility-robotics-advance-smart-manufacturing-with-humanoid-robot-pilot-in-hesston-kansas-facility"))
]

def main():
    directory = ROOT/"data/reports"
    directory.mkdir(parents=True,exist_ok=True)
    metrics = base_metrics()
    for m in metrics:
        if m["id"] in ("transactions","unsold_completed"):
            m["fresh"] = False
    report = dict(schemaVersion=1,month="2026-10",cutoff="2026-10-26",reviewedAt="2026-10-26",provisional=True,
                  headline="수도권 가격 상승과 거래 관망세의 공존. AI는 업무 실행으로, 휴머노이드는 생산·현장 실증으로.",metrics=metrics,news=oct_news)
    (directory/"2026-10.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    september = json.loads(json.dumps(report))
    september.update(month="2026-09",cutoff="2026-09-30",reviewedAt="2026-09-30",provisional=False,
                     headline="주택가격 상승폭은 둔화, 거래량은 감소. 지역별 수요와 재고 위험을 구분해 확인할 필요.")
    september["metrics"] = september["metrics"][:4]
    for m in september["metrics"]:
        m["fresh"] = True
        if m["id"]=="sale":m.update(current=.27,previous=.29,period="2026-08",previousPeriod="2026-07",source=source("KB국민은행",KB+"260916-2.html"),impact="가격 상승은 이어지지만 상승 속도는 둔화했습니다. 지역별 거래 확인이 필요합니다.")
        if m["id"]=="rent":m.update(current=.30,previous=.34,period="2026-08",previousPeriod="2026-07",source=source("KB국민은행",KB+"260916-4.html"))
    september["news"] = [
      news("re-sale-sep","realestate","매매가격·거래","2026-09-30","통계 발표","8월 가격 상승과 거래 감소, 시장 흐름 차별화",["KB 기준 8월 전국 주택 매매가격 +0.27%, 수도권 +0.59%, 서울 +0.75%.","국토교통부 기준 8월 주택 매매거래 48,359건, 전월 대비 -23.5%."],["가격 상승을 거래 회복으로 확대 해석하지 않아야 합니다."],"지역별 실거래가격·거래 빈도",MOLIT),
      news("re-rent-sep","realestate","전세시장","2026-09-16","통계 발표","전세 상승폭 둔화에도 수도권 임차 부담 지속",["8월 전국 전세가격 +0.30%, 수도권 +0.53%, 서울 +0.68%.","KB전세가격전망지수는 8월 120.5."],["전국 상승폭은 둔화했지만 수도권 전세가격 상승 압력은 지속됩니다."],"전세 매물·이사철 수요",source("KB경영연구소",KB+"260916-4.html")),
      news("re-supply-sep","realestate","공급·미분양","2026-09-30","공식 통계","미분양 재고와 준공 감소가 동시에 진행",["8월 말 전체 미분양 69,134호, 전월 대비 +1.3%.","준공 후 미분양 28,080호, 전월 대비 -3.7%.","1~8월 누적 준공은 전년 동기 대비 -27.2%."],["미분양과 준공 후 미분양은 구분하고 입지별 공급을 살펴야 합니다."],"재고 해소·준공·착공",MOLIT),
      news("re-finance-sep","realestate","주택금융","2026-09-16","통계 발표","8월 주담대 증가, 거래와 대출의 시차 확인 필요",["8월 은행권 주택담보대출 잔액 952.5조 원, 월 증가액 4.0조 원.","8월 전세자금대출 잔액 162.1조 원, 전월 대비 0.7조 원 감소."],["대출 증가에는 앞선 거래의 잔금·입주자금 수요가 반영됩니다."],"금리·대출 증가액·입주",source("KB경영연구소",KB+"260916-7.html"))
    ]
    (directory/"2026-09.json").write_text(json.dumps(september,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    index=dict(schemaVersion=1,reports=[dict(month="2026-10",label="2026년 10월 · 잠정",path="data/reports/2026-10.json"),dict(month="2026-09",label="2026년 9월",path="data/reports/2026-09.json")])
    (ROOT/"data/index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
