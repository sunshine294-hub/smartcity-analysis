# 데이터로 진단하는 업무지구의 성공과 실패
## 판교테크노밸리 vs 청라국제업무지구 비교분석 시스템

가천대학교 스마트시티학과 | 스마트시티 이론과 실제 기말과제 | 2026

---

## 시스템 개요

수도권 지하철 GTFS 네트워크·공공 공간데이터 6종을 활용해  
**판교테크노밸리(성공)**와 **청라국제업무지구(실패)**를 정량 비교하는  
GitHub Pages 정적 웹 시스템입니다.

**배포 URL**: `https://<your-id>.github.io/<repo-name>/`  
**원클릭 배포**: `bash deploy.sh <your-id> <repo-name>`  
**분석 보고서**: `smartcity_report.pdf` (저장소 루트)  
> 배포 완료 후 `smartcity_report.pdf` 표지·부록 A의 `sunshine294-hub`을 실제 GitHub ID로 교체하고 `python3 scripts/build_report_html.py`로 재빌드하세요.

---

## 분석 데이터 출처 및 기준월

| 데이터 | 출처 | 기준 |
|--------|------|------|
| 수도권 지하철 네트워크 그래프 | 강의 제공 `subway_network.zip` | 2024년 운영 기준 |
| 토지이용계획(용도지역) | VWorld Data API `LT_C_UQ111` | 2024년 |
| 지구단위계획 | VWorld Data API `LT_C_UPISUQ153` | 2024년 |
| 건축물대장 | 건축HUB `getBrTitleInfo` | 2024년 |
| 도로망 | OpenStreetMap Overpass API | 2024년 6월 |
| 인구 100m 격자 | 통계청 인구총조사 `다사` 격자 | 2024년 |
| 종사자 100m 격자 | 통계청 전국사업체조사 `다사` 격자 | 2023년 |

---

## 디렉토리 구조

```
.
├── index.html              # 메인 웹 시스템 (3화면)
├── assets/
│   ├── app.js              # 지도·차트·등시간권 로직
│   ├── iso_logic.js        # 등시간권 폴리곤 교차 계산
│   └── style.css           # 스타일
├── data/
│   ├── stats.json          # 핵심 지표 (실측값)
│   ├── isochrones.geojson  # 등시간권 폴리곤 (current/future/pre_gtx)
│   ├── landuse_pangyo.geojson      # 판교 용도지역 (VWorld 실측)
│   ├── landuse_cheongna.geojson    # 청라 용도지역 (VWorld 실측)
│   ├── parcels_pangyo.geojson      # 판교 건축물 (건축HUB 실측)
│   ├── parcels_cheongna.geojson    # 청라 건축물 (건축HUB 실측)
│   ├── regions.geojson             # 구역 경계
│   ├── accessibility_summary.json  # 등시간권 역·면적 집계
│   └── station_times.json          # 역별 최단소요시간
├── scripts/                # 데이터 전처리 스크립트 (Python)
│   ├── build_report_html.py        # 보고서 HTML→PDF 빌더 (WeasyPrint)
│   ├── isochrone_analysis.py       # GTFS → 다익스트라 → 등시간권
│   └── generate_placeholders.py   # 스키마 정의 참조용
├── collect/                # 공공 API 데이터 수집 스크립트
│   ├── config_example.py           # API 키 설정 템플릿 (복사 후 config.py로 사용)
│   └── run_all.py                  # VWorld·건축HUB·SGIS 일괄 수집
├── deploy.sh               # GitHub Pages 원클릭 배포 스크립트
└── README.md
```

---

## GitHub Pages 배포 절차

```bash
# 1. Git 저장소 초기화
git init
git add .
git commit -m "initial commit: 판교 vs 청라 비교분석 시스템"

# 2. GitHub 원격 연결 및 push
git remote add origin https://github.com/<your-id>/<repo-name>.git
git branch -M main
git push -u origin main
```

3. GitHub 레포지토리 → **Settings → Pages → Source: "Deploy from a branch"**  
   Branch: `main` / `(root)` → Save  
4. 약 1~2분 후 `https://<your-id>.github.io/<repo-name>/` 에서 접근 가능

---

## 데이터 전처리 재현 방법

### 환경 설정
```bash
# 전체 의존 패키지 설치 (Python 3.10+)
pip install geopandas shapely pyproj requests reportlab \
            scipy pandas numpy openpyxl networkx weasyprint
```

### API 키 설정 (`collect/config.py`)

> `collect/` 폴더에 `config_example.py`와 `run_all.py`가 포함되어 있습니다.  
> **config.py는 API 키를 담으므로 절대 GitHub에 push하지 마세요** (`.gitignore`에 추가 권장).

```bash
# config_example.py 를 복사해 수정
cp collect/config_example.py collect/config.py
```
```python
# collect/config.py 내용 예시
VWORLD_KEY   = "여기에_VWorld_API_키_입력"    # https://www.vworld.kr/dev/v4dv_apikey_v2.do
BUILDING_KEY = "여기에_공공데이터포털_API_키"  # https://www.data.go.kr
SGIS_KEY     = "여기에_SGIS_API_KEY_입력"     # https://sgis.kostat.go.kr
SGIS_SECRET  = "여기에_SGIS_SECRET_입력"
```

### 1. 수도권 지하철 네트워크 분석 (등시간권)
```bash
cd scripts/
python isochrone_analysis.py
# 출력: data/isochrones.geojson, data/accessibility_summary.json
# 소요: 약 3~5분 (817 노드, 다익스트라)
```

판교역(node_id: 1146)과 청라국제도시역(node_id: 557)을 출발점으로  
10/20/30/40/50/60분 등시간권을 산출합니다.  
`begin` 컬럼으로 시점별 운영 네트워크 필터링(current=2024, pre_gtx=GTX 개통 전).

### 2. 공간데이터 수집 (사용자 PC에서 실행)
```bash
# collect/ 폴더의 스크립트 — API 키 필요 (config.py에 입력)
python collect/run_all.py
# 출력: data_out/ 폴더 (VWorld·건축HUB·OSM 데이터)
```

API 키 발급:
- VWorld: https://www.vworld.kr/dev/v4dv_apikey_v2.do
- 건축HUB: https://www.data.go.kr (공공데이터포털)
- SGIS: https://sgis.kostat.go.kr/developer/html/openApi/api/index.html

### 3. 인구·종사자 격자 데이터 (통계청)
```
통계청 마이크로데이터 포털 → 인구·사업체 격자 → 100M 수도권
파일명 규칙: 2024년_인구_다사_100M.csv / 2023년_종사자_다사_100M.csv
격자코드 변환: col = X//100 - 9000, row = Y//100 - 19000
              → grid_id = f"다사{col:03d}{row:03d}"
```

공간 교차(등시간권 폴리곤 × 격자 중심점 within 검사)로  
도달가능 인구·종사자를 산출합니다 (geopandas `within` 메서드).

---

## 핵심 지표 (data/stats.json)

| 지표 | 판교TV | 청라IBC | 비율 |
|------|--------|---------|------|
| 30분 도달 인구 | 536,696명 | 110,476명 | 4.9배 |
| 30분 도달 종사자 | 745,493명 | 59,660명 | **12.5배** |
| 30분 도달 역수 | 48개 | 25개 | 1.9배 |
| 지구단위계획 집행률 | 81.6% | 56.0% | — |
| 직주비 | 2.84 | 0.19 | — |
| LUM 엔트로피 (용도지역) | 0.736 | 0.747 | — |

---

## 구역계 정의

- **판교테크노밸리(제1판교)**: 경기도 성남시 분당구 삼평동·백현동·판교동  
  지구단위계획 고시 면적 661,000 m² / 출처: 성남시 도시계획정보서비스
- **청라국제업무지구**: 인천광역시 서구 청라1·2·3동 (국제업무단지 블록 B1·B2·B9·B10·C1·C2·M5·M6)  
  IFEZ 사업지구 경계 면적 278,000 m² / 출처: 인천경제자유구역청 사업개요

---

## AI 활용 내역

본 프로젝트는 **Claude Fable 5 (Anthropic)**를 활용하여 개발했습니다.

- 데이터 수집 스크립트 작성 (VWorld API, 건축HUB, OSM Overpass, SGIS)
- 등시간권 분석 알고리즘 구현 (다익스트라, 폴리곤 공간 교차)
- 웹 시스템 UI/UX 구현 (Leaflet, Chart.js)
- 분석 보고서 초안 작성 (reportlab PDF)

모든 수치·출처는 원데이터로 검증했습니다.  
분석의 해석과 결론은 제출자가 직접 작성했습니다.
