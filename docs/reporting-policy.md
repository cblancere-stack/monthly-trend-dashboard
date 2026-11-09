# 월간 동향보고서 운영 기준

사용자가 자료를 주지 않아도 ChatGPT 예약 작업이 공식자료 조사, 교차 확인, 요약, 월별 파일 작성, GitHub 커밋, Pages 배포를 수행한다. Gemini API는 호출하지 않는다.

## 게시와 보강

- 매월 5일 아침(한국 시간): 전월 보고서 1차 게시. 11월 5일은 10월 보고서이다.
- 매월 7일 아침: 1차판의 결측과 추가 공식 발표를 재확인하고 같은 월 파일을 중간 보강한다.
- 매월 10일 아침: 같은 전월 보고서의 숫자·누락 이슈·해석·출처 보강. 1차 파일이 없으면 최초 발행도 수행한다.
- 9월 제공자료 요약본과 과거 월은 유지한다. 새 월은 `data/summaries/YYYY-MM.json`에 별도 작성한다. 보고서 선택 메뉴는 최신 월을 먼저 표시한다.
- `scripts/report_lifecycle.py`의 `save_summary`로 해당 월 파일과 `summaryReports`를 등록한다. 10일에는 해당 월만 개정하고 최초 게시일·개정 이력을 보존한다.
- 예약 등록은 실제 실행 성공의 보장이 아니다. 실패 시 기존 게시물을 유지하고 원인을 사용자에게 알린다.

## 범위와 날짜

경제·사회·규제·정치, 부동산, 자동차, 항공우주·방산, AI, 휴머노이드·로봇, 2차전지, 에너지·ESG의 8개 분야를 모두 조사한다. 뉴스·정책은 전월 사건을 대상으로 하고, 전월 실적이 다음 달 초 발표되면 작성일 기준 공개된 자료까지 포함한다. 발표일과 실적 기준월을 별도 저장한다. 다음 달 뉴스를 전월 사건으로 둔갑시키지 않는다.

모든 분야에서 기존 지표 항목과 주요 이슈를 유지하며 항목별 문장만 요약한다. 이슈 수를 2~3건으로 자르지 않는다. 동일 사실의 중복만 합친다. `data/report-template.json`의 36개 추적 항목(경제 분야 10개 포함)을 조사한다. 지속적으로 확보할 수 없는 지표는 원지표의 상태와 대체 이유를 남기고 명시적인 `replaces`로 대체한다. 단일 모델 비용을 시장 평균으로, 지수 수익률을 지수 포인트로 표현하지 않는다.

## 결측 처리

- 원래 기관의 표·PDF·다운로드·공개 시계열·공식 재배포를 순서대로 확인한다. 홈페이지 링크만 붙여 수치가 입증됐다고 표시하지 않는다.
- 미발표는 최근 공식 발표값을 실적 기준월과 함께 사용한다. 접근 실패는 다른 공식 배포 경로와 이전 확인값을 확인한다.
- 분기·연간·전망은 주기와 기준 연도·전망 연도를 표시한다. 매월 새 실적처럼 표시하지 않는다.
- 값 자체가 없으면 `dataStatus=not_released|unavailable`, `missingReason`과 `checkedSources`를 기록한다. 0이나 임의 숫자로 채우지 않는다. 근거 없는 예시값을 재사용하지 않는다.
- 비교값이 없으면 전월비를 계산하지 않고 이유를 적는다. `basis`, `meaning`, `impact`, `deltaText`를 비워두지 않는다.
- 일부 지표의 결측 때문에 전 분야의 보고서를 게시하지 않는 방식은 피한다. 10일에는 결측을 모두 재확인한다.

## 표시 형식과 출처

`kind=summary`, `origin=independent`, `phase=initial|enriched`, `month`, `asOf`, `cutoff`, `headline`, `metrics`, `news`, `policies`, `supplements`, `calendar`, `sectorSummaries`를 저장한다. 화면은 기존 작은 글자·카드 디자인과 '동향보고서 요약' 제목을 유지한다. 원문 전체 보존 화면은 추가하지 않는다.

- 첫 화면: 기존과 같은 5개 섹터 요약. `stats`는 원자료 수치와 일치한다.
- 지표: `id`, `category`, `title`, `valueText`, `basis`, `meaning`, `impact`, `deltaText`, `period`, `frequency`, `published`, `source:{name,url}`. 결측이면 위의 사유·확인 경로를 사용한다.
- 뉴스: `id`, `category`, `headline`, `facts`, `analysis`, `track`, `published`, `dateLabel`, `source`. 사실과 해석을 구분한다.
- 정책: `id`, `category`, `headline`, `content`, `analysis`, `published`, `source`. 정책 단계·시행일을 구분한다.
- 심화 분석: `id`, `categories`, `title`, `points`, `source` 또는 `sources`.
- 일정: `date`, `sector`, `categories`, `event`, `watch`, `source`. 보고서 대상 월의 다음 달 일정이며 실행일 이전 날짜도 실제 일자로 표시한다.
- `sectorCoverage`에 8개 분야별 정책·일정 등 해당 항목이 없을 때 확인 범위와 사유를 기록한다. 빈 카드를 억지로 만들지 않는다.

공식 원문 URL과 기준일을 데이터와 화면에 연결한다. '검증 전' 반복 문구를 추가하지 않으며 확인하지 않은 사실을 확인했다고 쓰지 않는다. `validate_summary`와 전체 테스트를 통과한 뒤 게시한다. 최종 결과에 1차/보강 구분, 수록 범위, 남은 결측 사유와 배포 성공 여부를 알린다.

## 요청에 따른 과거 월 재현

사용자가 과거 월을 요청하면 `save_summary(..., historical=True)`로 별도 등록한다. 이 옵션은 기본 예약 발행에는 사용하지 않는다. 현재 월·미래 월에는 적용할 수 없으며 `revisionNote`에 요청 사유를 기록한다. `asOf`·`cutoff`는 당시 자료의 마감일, `firstPublishedAt`·`updatedAt`은 실제 게시일이다. 과거 보고서를 추가해도 최신 월을 기본 선택으로 유지한다. 2026년 8월 보고서는 사용자 확인에 따라 8월 31일을 기준일로 한다.

ROBO는 사용자가 지정한 상장 상품(ROBO Global Robotics and Automation Index ETF)의 월말 종가($)를 사용하고 화면 표시명은 ROBO로 유지한다. 정식 상품명·일반 종가·배당 제외 기준은 자료 출처와 상세 정의에 기록한다. Indxx는 원지수 IAIQP 월말 종가(pt)를 사용한다. 두 항목 모두 현지 마지막 거래일 기준이다. 휴장일에는 해당 월 마지막 거래일로 표시하고 전월의 동일 상품·동일 통화·동일 가격 계열 종가 대비 증감률 = (당월 종가 / 전월 종가 − 1) × 100으로 계산한다. 한국 시간 익월 1일 확정되는 월말 종가도 해당 월 관측값으로 포함한다. 원자료의 관측일과 한국 시간 확인 가능일을 구분하고, ROBO는 일반 종가와 수정 종가·NAV를 혼합하지 않으며, Indxx 원지수는 ETF 가격으로 대체하지 않는다. 두 항목 모두 3개월 수익률을 전월 대비로 표시하지 않는다. 이 예외는 뉴스·정책·통계의 발표일에는 적용하지 않는다. 같은 주소의 PDF가 최신판으로 바뀌었다면 과거 기준일 당시의 공개본과 공개일을 확보한 경우에만 소급 사용한다. 연간·분기 통계와 모델 평가 버전이 달라진 수치는 월간 증감률로 연결하지 않는다. 관련 원문·일정 공지의 발표일도 기준일 검사에 포함한다.


2026-10-28 사용자 최종 확정: ROBO는 ETF 가격 대신 VettaFi Net Total Return 원지수(pt)를 사용한다. 이 규칙이 앞의 ROBO ETF 규칙에 우선한다. 8월 3,395.32pt, 9월 3,377.82pt는 사용자가 제공한 공식 차트 화면을 근거로 한다. 8월 전월비는 7월 동일 계열 값 확보 전까지 제외한다.

## 시장·원자재 지표 조회 절차

검색 결과는 공식 자료의 위치를 찾는 데 사용한다. 공식 페이지에 값이 텍스트로 노출되지 않으면 표·공개 다운로드를 먼저 확인하고, 필요한 경우 브라우저에서 차트 기간을 좁혀 해당 거래일의 그래프 선 위 툴팁을 확인한다. 값·관측일·공개일(원문 미표기 시 확인일과 구분)·계열명·단위·공식 링크·조회 경로를 남긴다. 전월 비교값은 같은 계열에서 별도 확인하며, 전월값 미확보만으로 당월 관측값을 생략하지 않는다.

| 지표 | 조회 경로와 확인 사항 |
|---|---|
| 코스피·나스닥·환율·미 국채 | [KRX](https://data.krx.co.kr/), [Nasdaq/FRED](https://fred.stlouisfed.org/series/NASDAQCOM), [한국은행 ECOS](https://ecos.bok.or.kr/), [미 재무부](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve)에서 양쪽 월의 마지막 거래일 대조. 서울 외환시장 주간 종가와 매매기준율·해외 고시환율 구분. |
| ROBO | [VettaFi 공식 차트](https://www.vettafi.com/indexing/index/robo) → Chart view → Net Total Return(ROBOTR) → 1M 또는 3M → 해당 거래일의 그래프 선 위 툴팁. Table view는 최신 기준일 수준과 기간 수익률 확인용. 월말 pt는 날짜별 툴팁으로 확인. |
| Indxx | [Indxx 공식 지수](https://www.indxx.com/index/indxx-artificial-intelligence-big-data-index) → IAIQP USD Price Return 차트의 날짜별 관측치 또는 공식 시계열. |
| 탄산리튬 | [KOMIS](https://www.komis.or.kr/) 광물가격 조회에서 해당 규격·순도·인도조건·통화·단위를 확인해 일별 표 또는 월별 자료 조회. 중국 도착도(CIF)와 중국 내수 위안화 가격은 별도 계열. |
| 양극재 수출액 | [관세청 수출입무역통계](https://tradedata.go.kr/)에서 품목별 조회. 양극활물질 HS 코드 범위·코드 개정 여부·수출금액 단위를 확인하고 같은 코드로 양월 합산. 코드 확정 근거를 데이터에 저장. |
| 두바이유 | [한국석유공사 Petronet](https://www.petronet.co.kr/) 또는 [에너지경제연구원](https://keei.re.kr/) 재배포의 일별 Dubai USD/배럴. 두 달 같은 출처·계열의 마지막 관측일 확인. |
| LNG | JKM 현물 평가가격과 JKM 선물은 별도 계열. 원 계열 미확보 시 대체 지표를 명시하고, 선물은 거래소·계약월·정산가·USD/MMBtu를 고정. |
| EU 배출권 | [EEX 환경상품](https://www.eex.com/en/market-data/market-data-hub/environmentals) 원자료 우선. EUA 현물·경매·선물 구분, 선물 만기와 EUR/tCO₂ 기준 명시. |
| RE100 기업 수 | [한국에너지공단 K-RE100 등록정보](https://www.data.go.kr/data/15093741/openapi.do)에서 기준일이 붙은 누적 등록기업 수 확인. 원자료를 집계할 경우 중복 제거 단위 기록. 글로벌 RE100 한국 회원 수는 별도. |

미확보 처리 시 확인 URL과 실제로 시도한 메뉴·필터·날짜, 미확보 사유를 남긴다. 차트 조작이나 표 조회를 끝내지 못한 상태를 자료 미공표로 표시하지 않는다.
