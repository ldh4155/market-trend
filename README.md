# Market Trend

네이버 DataLab API를 활용해 국내 주식 시장 섹터 및 종목별 검색 트렌드를 조회하고 시각화하는 웹 애플리케이션입니다.

## 주요 기능

- **섹터 트렌드**: 반도체, IT/소프트웨어, 금융, 바이오/제약 등 8개 섹터의 검색량 추이 비교
- **종목 트렌드**: 선택한 섹터 내 주요 기업들의 검색량 추이 비교
- **기간/단위 설정**: 조회 기간(시작일~종료일) 및 집계 단위(일/주/월) 커스터마이징
- **차트 시각화**: 검색량 순위 및 시계열 라인 차트 제공

## 기술 스택

### Backend

| 기술 | 버전 |
|------|------|
| Python | 3.x |
| FastAPI | 0.136.0 |
| Uvicorn | 0.46.0 |
| Pydantic | 2.13.3 |
| pydantic-settings | 2.14.0 |
| httpx | 0.28.1 |
| python-dotenv | 1.2.2 |

### Frontend

| 기술 | 버전 |
|------|------|
| React | 19.2.5 |
| TypeScript | 6.0.3 |
| Vite | 8.0.10 |
| React Router DOM | 7.14.2 |
| Axios | 1.15.2 |
| Recharts | 3.8.1 |

## 프로젝트 구조

```
market-trend/
├── be/                         # 백엔드 (Python/FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   └── router.py       # API 엔드포인트 정의
│   │   ├── core/
│   │   │   └── config.py       # 환경변수 설정 (Pydantic Settings)
│   │   ├── data/
│   │   │   └── sectors.py      # 섹터/종목 정적 데이터
│   │   ├── schemas/
│   │   │   └── trend.py        # 요청/응답 Pydantic 스키마
│   │   ├── services/
│   │   │   ├── trend_service.py    # 트렌드 집계 비즈니스 로직
│   │   │   └── naver_datalab.py    # 네이버 DataLab API 연동
│   │   └── main.py             # FastAPI 앱 초기화 및 CORS 설정
│   ├── .env                    # 환경변수 (API 키 등, git 미포함)
│   └── requirements.txt        # Python 의존성
│
└── fe/                         # 프론트엔드 (React/TypeScript)
    ├── src/
    │   ├── components/
    │   │   ├── SectorTab.tsx       # 섹터 검색 탭 UI
    │   │   ├── CompanyTab.tsx      # 종목 검색 탭 UI
    │   │   ├── TrendChart.tsx      # 라인 차트 컴포넌트
    │   │   └── DateRangeForm.tsx   # 날짜/단위 선택 폼
    │   ├── pages/
    │   │   └── Home.tsx            # 메인 페이지 (탭 전환)
    │   ├── api.ts                  # Axios API 클라이언트
    │   ├── types.ts                # TypeScript 타입 정의
    │   ├── App.tsx                 # 루트 컴포넌트
    │   └── main.tsx                # 앱 진입점
    ├── vite.config.ts          # Vite 설정 (API 프록시 포함)
    └── package.json            # npm 의존성
```

## 시작하기

### 사전 요구사항

- Python 3.x
- Node.js 18+
- 네이버 DataLab API 키 ([발급 링크](https://developers.naver.com/apps/#/list))
- 한국투자증권 open-api 신청 후 app-key, app-secret 발급

### 백엔드 설정

```bash
cd be

# 가상환경 생성 및 활성화
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate     # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env  # 아래 환경변수 항목 참고
```

### 프론트엔드 설정

```bash
cd fe
npm install
```

### 환경변수

`be/.env` 파일을 생성하고 아래 값을 입력합니다.

```env
APP_NAME=Market Trend API
DEBUG=true
NAVER_DATALAB_CLIENT_ID=<네이버_클라이언트_ID>
NAVER_DATALAB_CLIENT_SECRET=<네이버_클라이언트_시크릿>

KIS_APP_KEY=<한국투자증권 App-Key>
KIS_APP_SECRET=<한국투자증권 App-Secret>
```


## API 엔드포인트

모든 서버 API는 `/api/*` 경로로 제공됩니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/health` | 서버 상태 확인 |
| GET | `/api/trends/sectors/list` | 전체 섹터 목록 조회 |
| POST | `/api/trends/sectors` | 섹터별 검색 트렌드 조회 |
| POST | `/api/trends/companies` | 종목별 검색 트렌드 조회 |
| GET | `/api/new-highs/weekly` | 주간 신고가 교집합 조회 |
| GET | `/api/new-highs/30d` | 최근 30일 신고가 반복 종목 조회 |
