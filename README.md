# 월간 동향 대시보드

부동산 4건 · AI 2건 · 휴머노이드 2건과 대표 지표를 공개하는 한국어 웹 대시보드.

예정 공개 주소: **https://cblancere-stack.github.io/monthly-trend-dashboard/**

## 처음 한 번만 설정하기

1. 압축을 풀고 안의 파일·폴더를 저장소 **Add file → Upload files** 화면에 끌어다 놓습니다. 폴더 자체가 아니라 `index.html`이 저장소 최상단에 있어야 합니다.
2. `.github/workflows`도 반드시 올립니다. Windows 탐색기에서 보이지 않으면 **보기 → 표시 → 숨긴 항목**을 켜세요. 브라우저 업로드가 실패하면 GitHub Desktop으로 저장소를 열고 파일 복사 → Commit → Push 하세요.
3. **Settings → Pages → Build and deployment → Source → GitHub Actions**를 선택합니다.
4. **Actions → Deploy dashboard to GitHub Pages → Run workflow**를 실행합니다.
5. 성공하면 위 공개 주소에 접속합니다. Pages 설정 전에는 배포가 실패할 수 있습니다.

## 뉴스까지 자동 갱신하려면

Google AI Studio에서 발급한 Gemini API 키를 아래 위치에 직접 등록하세요. 키를 대화나 공개 저장소에 적지 않습니다.

**Settings → Secrets and variables → Actions → Secrets → New repository secret**

| 이름 | 값 |
| --- | --- |
| `GEMINI_API_KEY` | Google AI Studio API 키 |

모델 기본값은 `gemini-flash-latest`입니다. 지원하지 않는 계정이면 **Variables**에 `GEMINI_MODEL`로 Google Search grounding을 지원하는 사용 가능한 모델 ID를 지정하세요. API·검색 사용은 계정별 한도·별도 과금이 적용될 수 있으며 ChatGPT 구독과 별개입니다.

**Actions → Collect and publish monthly report → Run workflow**, `month`에 `2026-10`을 입력해 실제 수집과 비용을 먼저 확인하세요.

## 갱신 일정

- 매월 1~3일 한국 시간 오전 9시 17분에 전월 보고서를 수집·검증·배포합니다.
- 발표 지연·실패에 대응해 2·3일 재시도합니다. 수동 실행은 원하는 월을 지정할 수 있습니다.
- 예약 작업은 지연될 수 있습니다. 공개 저장소는 60일 무활동 시 예약 작업이 중지될 수 있으므로 월간 커밋이 생성되는지 확인하세요.
- `data/status.json`에 실행일·키 연결 여부·오류 종류를 기록합니다. 비밀키나 API 응답 원문은 저장하지 않습니다.
- 저장소 Actions 실패 알림을 확인하세요. 소스 수집 실패 시 기존 값은 보존됩니다.

## 자동화 범위와 제약

| 항목 | 현재 구현 |
| --- | --- |
| 화면·월 선택·필터·PDF 인쇄 | 즉시 사용 가능 |
| KB 매매·전세 변동률 | 해당 월 발간일과 공식 원문 숫자 수집. 페이지 구조 변경 시 보류 |
| 거래량·준공 후 미분양 | Gemini 검색으로 공식 통계를 찾고 별도 PDF/HTML 취득 후 근거 대조. 접근 실패 시 기존 값 유지 |
| 뉴스 4/2/2 | Gemini 키 연결 시 공식 발표 검색. 발표일·원문 발췌·숫자가 대조된 카드만 반영 |
| Arena | 공식 평가 부문·날짜·숫자가 확인될 때 갱신. 전월값 없으면 비교 제외 |
| ROBO·Indxx | 날짜가 확인된 원지수만 허용. ETF/CFD 가격 대체 금지. 라이선스/API·안정적인 과거값 경로 연결 전 빈칸이 남을 수 있음 |
| Artificial Analysis 비용 | **전용 수집기 미연결.** 고정 성능 문턱·평가 버전의 과거값 확보 필요. 단일 모델 가격을 시장 지표로 대체하지 않음 |

모든 지표가 완전 자동화됐다고 가정하지 않습니다. 수집 실패 시 해당 기준월의 이전 값, 미확인 값은 ‘확인 대기’를 표시합니다. 시작 데이터는 출처를 확인한 2026년 9월과 **10월 26일 기준 10월 잠정본**입니다. 10월 말 확정본이 아닙니다.

생성형 AI의 문맥 해석은 완벽하지 않습니다. 발췌·숫자 대조는 근거의 존재를 검증하며 모든 해석의 정확성을 보증하지 않습니다. 자동 뉴스는 ‘자동 작성 · 원문 대조 필요’로 표시합니다. 중요한 내용은 원문을 검토하세요.

## 운영 원칙

- 보고서 월은 발표 기준, 실적 집계월은 별도 표시합니다.
- 월간 변동률 `%`와 변동률 차이 `%p`를 구분합니다.
- 같은 기관·범위·단위·수익률 유형·평가 버전을 유지합니다.
- 반올림 증감률로 전월값을 역산하지 않습니다.
- 기업의 계획·목표와 실제 생산·납품 실적을 구분합니다.
- 기존 뉴스는 자동 교체하지 않고 부족한 수만 채웁니다. 정정은 해당 월 JSON과 Git 이력에 남깁니다.
- 자료의 외부 재배포·상업 이용 조건을 기관별로 확인하고 원문 출처를 유지하세요.

## 개발·검증

Python 3.12 이상에서 실행:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/update_report.py --month 2026-10 --check-only
```

`--check-only`는 파일을 덮어쓰지 않습니다. 키가 없으면 KB 직접 수집만 시도합니다. 화면은 정적 서버 또는 Pages에서 확인하세요. `index.html`을 파일로 직접 열면 JSON 로딩이 차단될 수 있습니다.

초기 제작 검증: 화면·분야 필터·월 선택 및 데이터 검증 테스트를 확인했습니다. 제작 환경의 외부 사이트 직접 접속 제한으로 KB 실시간 수집은 완료하지 못했고, Gemini API 키가 없어 검색 API 실행은 미검증입니다. 배포 후 위 수동 실행으로 실제 동작을 확인해야 합니다.

| 경로 | 용도 |
| --- | --- |
| `index.html`, `assets/` | 공개 화면 |
| `data/index.json` | 월별 목록 |
| `data/reports/YYYY-MM.json` | 수치·뉴스·출처 |
| `scripts/update_report.py` | 수집·근거 대조 |
| `tests/test_data.py` | 날짜·잘못된 숫자·출처 변경 방지 테스트 |
| `.github/workflows/` | 배포·월간 갱신 |

공개 사이트에는 화면과 데이터만 배포합니다. 키는 GitHub Actions Secrets에만 저장합니다.

`scripts/seed_initial.py`는 초기 스냅샷을 다시 만들 때만 수동 실행하며 예약 작업에서 실행하지 않습니다.
