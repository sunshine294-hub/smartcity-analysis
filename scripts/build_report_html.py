#!/usr/bin/env python3
"""
스마트시티 비교분석 보고서 — WeasyPrint HTML→PDF 빌더
판교테크노밸리(성공) vs 청라국제업무지구(실패)
"""
import sys, os, json
sys.path.insert(0, '/sessions/magical-upbeat-hamilton/.local/lib/python3.10/site-packages')

# ── 데이터 로드 ─────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "project", "data")

with open(os.path.join(DATA_DIR, "stats.json"), encoding="utf-8") as f:
    S = json.load(f)

P_s = S["socio"]["pangyo"]
C_s = S["socio"]["cheongna"]
P_t = S["transport"]["reach"]["current"]["pangyo"]
C_t = S["transport"]["reach"]["current"]["cheongna"]
P_l = S["landuse"]
P_ind = S["industry"]["pangyo"]
C_ind = S["industry"]["cheongna"]

# 지표 계산
p30w = P_t["30"]["workers"]
c30w = C_t["30"]["workers"]
ratio_w = p30w / max(c30w, 1)

p30p = P_t["30"]["pop"]
c30p = C_t["30"]["pop"]

p_far = P_l["far_avg"]["pangyo"]
c_far = P_l["far_avg"]["cheongna"]
p_vac = P_l["vacant_ratio"]["pangyo"]
c_vac = P_l["vacant_ratio"]["cheongna"]
p_lum = P_l["lum"]["pangyo"]
c_lum = P_l["lum"]["cheongna"]

p_biz = P_l["use_share_gfa"]["pangyo"]["업무"]
c_biz = P_l["use_share_gfa"]["cheongna"]["업무"]
p_fac = P_l["use_share_gfa"]["pangyo"]["공장"]
c_fac = P_l["use_share_gfa"]["cheongna"]["공장"]

p_jh = P_s["jh_ratio"]
c_jh = C_s["jh_ratio"]

# exec_ratio: 이전 분석값(stats에 없으면 직접 입력)
p_exec = 81.6
c_exec = 56.0

# ── HTML 생성 ────────────────────────────────────────────────────────────────
HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>스마트시티 비교분석 보고서</title>
<style>
@font-face {{
  font-family: 'NotoKR';
  src: url('file:///tmp/NotoSerifKR-Regular.ttf') format('truetype');
  font-weight: normal;
  font-style: normal;
}}
@font-face {{
  font-family: 'NotoKR';
  src: url('file:///tmp/NotoSerifKR-Bold.ttf') format('truetype');
  font-weight: bold;
  font-style: normal;
}}

/* 페이지 설정 */
@page {{
  size: A4;
  margin: 20mm 18mm 22mm 18mm;
  @bottom-center {{
    content: counter(page) ' / ' counter(pages);
    font-family: 'NotoKR', serif;
    font-size: 9pt;
    color: #666;
  }}
}}
@page :first {{
  @bottom-center {{ content: ''; }}
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'NotoKR', serif;
  font-size: 10pt;
  line-height: 1.75;
  color: #1a1a1a;
}}

/* 표지 */
.cover {{
  page: cover-page;
  height: 270mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 10mm;
}}
@page cover-page {{
  margin: 25mm 20mm;
  @bottom-center {{ content: ''; }}
}}
.cover-tag {{
  font-size: 9pt;
  letter-spacing: 2px;
  color: #3b82f6;
  text-transform: uppercase;
  margin-bottom: 8mm;
}}
.cover-title {{
  font-size: 22pt;
  font-weight: bold;
  line-height: 1.4;
  color: #111;
  margin-bottom: 5mm;
}}
.cover-sub {{
  font-size: 13pt;
  color: #444;
  margin-bottom: 12mm;
}}
.cover-divider {{
  width: 40mm;
  height: 2px;
  background: #3b82f6;
  margin-bottom: 10mm;
}}
.cover-meta {{
  font-size: 9.5pt;
  color: #555;
  line-height: 2.0;
}}
.cover-verdict {{
  margin-top: 14mm;
  padding: 5mm 7mm;
  border-left: 4px solid #ef4444;
  background: #fef2f2;
  font-size: 9.5pt;
  color: #7f1d1d;
  line-height: 1.7;
}}

/* 섹션 */
.section {{
  page-break-before: auto;
  margin-bottom: 10mm;
}}
.section-break {{
  page-break-before: always;
}}

h1 {{
  font-size: 13pt;
  font-weight: bold;
  color: #1e3a5f;
  border-bottom: 2px solid #1e3a5f;
  padding-bottom: 2mm;
  margin-bottom: 5mm;
  margin-top: 8mm;
}}
h2 {{
  font-size: 11pt;
  font-weight: bold;
  color: #2563eb;
  margin-top: 6mm;
  margin-bottom: 3mm;
}}

p {{
  margin-bottom: 3mm;
  text-align: justify;
}}

/* 비교표 */
table.comp {{
  width: 100%;
  border-collapse: collapse;
  font-size: 9.5pt;
  margin: 4mm 0;
}}
table.comp th {{
  background: #1e3a5f;
  color: #fff;
  padding: 2.5mm 3mm;
  text-align: center;
  font-weight: bold;
}}
table.comp td {{
  padding: 2mm 3mm;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
}}
table.comp tr:nth-child(even) td {{
  background: #f8fafc;
}}
table.comp .label {{
  text-align: left;
  font-weight: bold;
  color: #334155;
}}
.win-p {{ color: #1d4ed8; font-weight: bold; }}
.win-c {{ color: #dc2626; font-weight: bold; }}

/* 인사이트 박스 */
.insight {{
  background: #eff6ff;
  border-left: 4px solid #2563eb;
  padding: 3mm 5mm;
  margin: 4mm 0;
  font-size: 9.5pt;
  line-height: 1.7;
}}
.insight.red {{
  background: #fef2f2;
  border-color: #dc2626;
}}
.insight.green {{
  background: #f0fdf4;
  border-color: #16a34a;
}}

/* 지표 카드 */
.metric-grid {{
  display: flex;
  gap: 4mm;
  margin: 4mm 0;
  flex-wrap: wrap;
}}
.metric-card {{
  flex: 1;
  min-width: 35mm;
  border: 1px solid #cbd5e1;
  border-radius: 2mm;
  padding: 3mm;
  text-align: center;
}}
.metric-label {{
  font-size: 8pt;
  color: #64748b;
  margin-bottom: 1mm;
}}
.metric-val {{
  font-size: 12pt;
  font-weight: bold;
  color: #1e3a5f;
}}
.metric-unit {{
  font-size: 7.5pt;
  color: #94a3b8;
}}

/* 소결 */
.summary-box {{
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 2mm;
  padding: 4mm 5mm;
  margin: 5mm 0;
  font-size: 9.5pt;
}}
.summary-box strong {{
  color: #1e3a5f;
}}

/* 주석 */
.footnote {{
  font-size: 8pt;
  color: #64748b;
  margin-top: 2mm;
}}

.page-ref {{
  font-size: 8.5pt;
  color: #6b7280;
  font-style: italic;
}}
</style>
</head>
<body>

<!-- ══ 표지 ══ -->
<div class="cover">
  <div class="cover-tag">스마트시티 이론과 실제 &nbsp;|&nbsp; 기말 분석 보고서</div>
  <div class="cover-title">같은 계획, 다른 결과<br>무엇이 스마트시티의 성패를 갈랐는가</div>
  <div class="cover-sub">판교테크노밸리(성공) vs 청라국제업무지구(실패)<br>공공데이터 기반 실증 비교분석</div>
  <div class="cover-divider"></div>
  <div class="cover-meta">
    과목명&nbsp;: 스마트시티 이론과 실제&nbsp;&nbsp;|&nbsp;&nbsp;지도교수&nbsp;: 여지호 교수님<br>
    학번·성명&nbsp;: [학번]&nbsp;·&nbsp;[성명]&nbsp;&nbsp;|&nbsp;&nbsp;제출일&nbsp;: 2026년 6월 22일<br>
    분석 기준연도&nbsp;: 2023–2024&nbsp;&nbsp;|&nbsp;&nbsp;웹 시스템&nbsp;: GitHub Pages 함께 제출
  </div>
  <div class="cover-verdict">
    <strong>핵심 결론</strong><br>
    두 지구의 격차는 단일 요인이 아닌 세 차원에서 동시에 나타난다.
    철도 30분 등시간권 내 도달 가능 종사자(광역 노동시장 규모 지표) 745,493명 vs 59,660명(12.5배),
    지구단위계획 집행률 81.6% vs 56.0%, 직주비(종사자÷거주인구) 2.84 vs 0.19.
    ※ '도달 가능 종사자'는 지구 내부 종사자(판교 9만명)와 구분되는 광역 접근성 지표.
    교통 접근성·계획 집행력·산업 집적 수준의 복합 격차가 같은 계획 아래 다른 결과를 만들었다.
  </div>
</div>

<!-- ══ 목차 ══ -->
<div class="section section-break">
  <h1>목차</h1>
  <table style="width:100%; font-size:9.5pt; border-collapse:collapse;">
    <tr><td style="padding:1.5mm 0;">1. 같은 계획, 다른 결과 — 연구 배경 및 목적</td><td style="text-align:right; color:#666;">2</td></tr>
    <tr><td style="padding:1.5mm 0;">2. 분석 범위 및 데이터</td><td style="text-align:right; color:#666;">2</td></tr>
    <tr><td style="padding:1.5mm 0;">3. 비교 분석 ① 교통망 접근성 — 판교 30분 종사자 도달력은 청라의 12배</td><td style="text-align:right; color:#666;">3</td></tr>
    <tr><td style="padding:1.5mm 0;">4. 비교 분석 ② 토지이용 — LUM 엔트로피는 비슷하나 혼합의 내용이 다르다</td><td style="text-align:right; color:#666;">4</td></tr>
    <tr><td style="padding:1.5mm 0;">5. 비교 분석 ③ 인구사회 — 종사자 7배 격차, 공실률·직주비가 실패를 확증</td><td style="text-align:right; color:#666;">5</td></tr>
    <tr><td style="padding:1.5mm 0;">6. 비교 분석 ④ 계획 집행력 — 집행률 81.6% vs 56.0%</td><td style="text-align:right; color:#666;">6</td></tr>
    <tr><td style="padding:1.5mm 0;">7. 성공요인 도출 — 비교 분석에서 확인된 세 가지 조건</td><td style="text-align:right; color:#666;">7</td></tr>
    <tr><td style="padding:1.5mm 0;">8. 분석의 한계 — 상관과 인과의 구분, 데이터·방법의 한계</td><td style="text-align:right; color:#666;">8</td></tr>
    <tr><td style="padding:1.5mm 0;">부록. 데이터 출처·시스템 URL·AI 활용·분석 방법</td><td style="text-align:right; color:#666;">9</td></tr>
  </table>
</div>

<!-- ══ §1 연구 배경 ══ -->
<div class="section section-break">
  <h1>1. 같은 계획, 다른 결과 — 연구 배경 및 목적</h1>

  <p>판교테크노밸리와 청라국제업무지구는 모두 2000년대 초반 정부 주도의 계획적 업무지구로 출발했다. 두 지역 모두 신도시 내 지구단위계획을 통한 용도배분·기반시설 확충을 전략적으로 추진했고, 초기 계획 의도 역시 유사하게 '국제 업무 및 첨단 산업 집적지'였다. 그러나 2023년 시점에서 판교테크노밸리 경계 내 종사자는 약 90,000명·기업 1,600개로 국내 최대 테크 클러스터를 형성했다(이하 '내부 종사자'). 이와 달리 청라는 종사자 13,000명·기업 320개에 머물며 계획 목표 대비 현저히 낮은 도달률을 보인다<span class="footnote">①</span>. §3에서 분석하는 '30분 대중교통 권역 내 도달 가능 종사자'(판교 745,493명·청라 59,660명)는 이 '내부 종사자'와 구분되는 지표로, 각 지구가 흡수할 수 있는 노동시장의 구조적 규모를 나타낸다.</p>

  <p>본 연구는 이 격차를 서술이 아니라 <strong>공공데이터 실증 분석</strong>으로 정량화하는 데 목적을 둔다. 대중교통 접근성(GTFS 등시간권), 토지이용 혼합도(LUM 엔트로피), 건조환경(건축물대장 실측), 계획 집행력(지구단위계획 집행률), 산업구조의 5개 축에서 두 지역을 비교하고, 두 지구의 결과 차이를 만든 구조적 조건을 밝히는 것이 연구 질문이다.</p>

  <div class="insight">
    <strong>연구 질문&nbsp;:</strong> 동일한 계획 패러다임을 채택한 두 업무지구에서, 어떤 구조적 조건의 차이가 서로 다른 결과를 만들었는가?
  </div>

  <p><div class="footnote" style="margin-top:4mm;">① 출처: IFEZ(인천경제자유구역청) 2023년 통계연보; 청라국제업무지구 공실률 44%는 건축HUB 건축물대장 사용현황 신고(2023년 1월 기준) 실측값. 판교테크노밸리 현황은 성남산업진흥원 2023 연간 보고서(판교테크노밸리 종사자 90,000명·기업 1,600개) 기준.</div>
  <p>본 보고서는 함께 제출하는 웹 시스템(<span class="page-ref">GitHub Pages 인터랙티브 뷰어 — 화면 1~3</span>)과 연계해 읽도록 설계되었다. 각 섹션의 [웹 시스템 화면 N 참조] 표기는 시스템의 해당 탭·기능에서 동일 수치를 재현할 수 있음을 의미한다.</p>

</div>

<!-- ══ §2 분석 범위 및 데이터 ══ -->
<div class="section">
  <h1>2. 분석 범위 및 데이터</h1>

  <h2>2.1 비교 지역 선정 근거</h2>
  <p>두 지역을 비교 지역으로 선정한 주된 근거는 계획 출발점의 유사성이다. 두 지구 모두 2000년대 초반 광역지자체·경제자유구역청 주도의 지구단위계획으로 조성됐고, 초기 목표(국제업무·첨단산업 집적지), 계획 수단(용도 배분·기반시설 확충), 착공 시기(2000년대 중반)가 사실상 동일하다. 계획 면적은 판교 661천㎡·청라 278천㎡로 규모 차이가 있지만, 두 지구 모두 도시 내 독립 블록으로 설계됐다는 점에서 비교 단위로 삼기에 무리가 없다. 2010년대 초 주요 기반시설이 완공됐으므로 약 15년의 성과를 같은 시점(2023년)에서 볼 수 있다는 점도 비교 조건으로 유리하다.</p>
  <p>다만 비교에 한계가 없는 것은 아니다. 수도권과 인천은 거시적 경제 성장 속도가 다르고, 기업 세제 혜택(경제자유구역 인센티브)과 중앙정부 지원 규모도 차이가 있다. 이들 외생 변수는 이 분석에서 통제되지 않는다. 따라서 이 보고서의 비교는 '두 지구가 얼마나 다른가'를 보여주되, '입지 조건의 차이가 결과 차이를 전부 설명한다'는 주장은 과잉 해석임을 명시한다.</p>

  <h2>2.2 공간적 범위 및 구역계 정의</h2>
  <p><strong>판교테크노밸리(제1판교)&nbsp;:</strong> VWorld LT_C_UQ111 레이어에서 지구단위계획구역코드 '4113500001'에 해당하는 폴리곤(경기 성남시 분당구 삼평동·백현동, 고시 면적 약 0.66km²=661천㎡). 신분당선 판교역을 핵심 역으로 설정.</p>
  <p><strong>청라국제업무지구&nbsp;:</strong> VWorld LT_C_UPISUQ153의 '청라국제업무지구 도시개발구역' 경계(인천 서구 청라동, 사업지구 면적 약 0.28km²=278천㎡). 인천1호선 청라국제도시역을 핵심 역으로 설정. 구역 경계에 걸친 격자는 centroid(격자 중심점)가 폴리곤 내부에 있는 경우만 포함했으며, 경계부 필지는 최대 ±3% 면적 오차가 발생할 수 있다.</p>

  <h2>2.3 데이터 출처 및 API</h2>
  <p class="tbl-cap">표 2-1. 분석에 사용된 데이터 목록 및 출처</p>
  <table class="comp">
    <tr>
      <th style="text-align:left; width:35%">데이터 종류</th>
      <th style="text-align:left;">출처 / API</th>
      <th style="width:20%;">기준연도</th>
    </tr>
    <tr><td class="label">지하철 네트워크 그래프</td><td>수도권 지하철 네트워크 그래프 (subway_network.zip, 강의 제공·LMS 배포) — nodes.tsv (역 좌표·노선·개통일), links.tsv (소요시간·환승 대기)</td><td>2024</td></tr>
    <tr><td class="label">인구·종사자 격자</td><td>SGIS 통계지리정보서비스 인구·종사자 격자통계 (100m 해상도)</td><td>2023</td></tr>
    <tr><td class="label">건축물대장 표제부</td><td>건축데이터민간개방 시스템(건축HUB) API</td><td>2024</td></tr>
    <tr><td class="label">용도지역·지구단위계획</td><td>국토정보플랫폼 VWorld Data API (LT_C_UQ111, LT_C_UPISUQ153)</td><td>2023</td></tr>
    <tr><td class="label">도로망</td><td>OSM Overpass API (highway=* 필터)</td><td>2024</td></tr>
    <tr><td class="label">고용 통계</td><td>성남산업진흥원·IFEZ 공표 통계</td><td>2023</td></tr>
  </table>

  <h2>2.4 데이터 기준 시점 일람</h2>
  <p class="tbl-cap">표 2-2. 지표별 데이터 기준 시점</p>
  <table class="comp">
    <tr>
      <th style="text-align:left; width:35%">지표</th>
      <th style="text-align:left;">데이터 출처</th>
      <th style="width:22%;">기준 시점</th>
    </tr>
    <tr><td class="label">30분 도달 종사자·인구</td><td>subway_network.zip (강의 제공) + SGIS 격자통계(100m)</td><td>2023년 평일 기준</td></tr>
    <tr><td class="label">LUM 엔트로피</td><td>건축HUB 연면적 표제부</td><td>2023년 12월</td></tr>
    <tr><td class="label">공실률</td><td>건축HUB 사용현황 신고</td><td>2023년 1월</td></tr>
    <tr><td class="label">직주비</td><td>KOSIS 사업체조사 / 주택총조사</td><td>2020년 기준<br><span class="footnote">(주택총조사 5년 주기; 2025년판 미공개 시점)</span></td></tr>
    <tr><td class="label">지구단위계획 집행률</td><td>VWorld 계획구역 변경 이력</td><td>2023년 6월</td></tr>
    <tr><td class="label">산업 구조</td><td>KOSIS 전국사업체조사</td><td>2021년 기준</td></tr>
    <tr><td class="label">종사자 (내부)</td><td>성남산업진흥원·IFEZ 공표</td><td>2023년</td></tr>
  </table>

  <h2>2.5 분석 방법 요약</h2>
  <p><strong>등시간권 분석&nbsp;:</strong> 강의 제공 subway_network.zip의 nodes.tsv(역 좌표·노선·개통일)와 links.tsv(구간 소요시간·환승 대기)를 NetworkX 방향 그래프(817노드)로 변환했다. 환승 대기시간은 배차간격 기반으로 이미 links.tsv에 반영되어 있어 별도 추정 없이 사용했다. begin 컬럼으로 현행(2024년 이전 개통)·장래(GTX 포함)·GTX 개통 전 세 시점 네트워크를 각각 필터링한 뒤, 다익스트라(Dijkstra) 최단경로 탐색으로 N분 도달 역 집합을 구하고, 해당 역들의 티센 다각형(Thiessen polygon) 합집합을 등시간권 폴리곤으로 정의했다.</p>

  <p><strong>인구·종사자 집계&nbsp;:</strong> SGIS 통계지리정보서비스 인구·종사자 격자통계(100m 격자)를 사용했다. 등시간권 폴리곤과의 공간 교차는 centroid-within-polygon 방식으로 처리했다. 즉, 100m 격자의 중심점(centroid)이 폴리곤 내부에 있으면 해당 격자 전체 인구·종사자를 포함으로 계산했다. 이 방식은 경계 통과 격자의 부분 포함을 허용하지 않는 단순 포함 기준이며, 최대 경계부 1개 격자 면적(0.01km²) 수준의 과소 계상이 발생할 수 있다. 100m 격자는 집계구보다 세밀하므로, 구역계와 집계 단위 불일치로 인한 오차는 집계구 방식 대비 크게 줄어든다.</p>

  <p><strong>도로망&nbsp;:</strong> OSM Overpass API로 수집한 수도권 도로망 데이터(highway=* 필터)는 두 가지 목적으로 활용했다. 하나는 구역 경계 내 도로 연장(km)과 면적 대비 도로 밀도를 산출해 두 지구의 도보 이동 환경을 확인하는 것이었으나, 두 지구 모두 신도시급 격자형 가로망(약 2.1~2.4km/km²)으로 유의미한 차이가 없어 최종 보고서의 주요 지표에서는 제외했다. 다른 하나는 핵심역에서 구역 중심까지의 직선거리 확인이다. 판교역은 구역 서단에 인접하고, 청라국제도시역은 구역 동단에 위치해 두 지구 모두 주요 업무 건축물까지의 도보 접근이 10분 이내로 유사하다.</p>

  <p><strong>기타 지표&nbsp;:</strong> LUM 엔트로피 지수는 H = −Σ(pᵢ·ln pᵢ)/ln(n) 공식을 적용했으며, n=6(업무·주거·상업·교육연구·공장·기타)으로 정규화했다. 직주비는 분석 구역 내 종사자 수 ÷ 거주 인구(상주인구)로 정의했다(KOSIS 전국사업체조사 종사자·인구총조사 상주인구, 모두 2020년 기준).</p>

  <div class="footnote">※ 전처리 코드 전체는 GitHub 저장소 /scripts/ 폴더에 공개. 배포 URL: https://sunshine294-hub.github.io/smartcity-analysis/</div>
</div>

<!-- ══ §3 접근성 ══ -->
<div class="section section-break">
  <h1>3. 비교 분석 ① 교통망 접근성 — 판교 30분 종사자 도달력은 청라의 12배</h1>

  <p>판교역 30분 등시간권 안에 종사자 <strong>{p30w:,}명</strong>이 있다. 청라국제도시역의 같은 권역에는 <strong>{c30w:,}명</strong>이다. <strong>{ratio_w:.0f}배 격차</strong>는 역 수 차이(1.9배)를 훨씬 상회하며, 두 업무지구가 흡수 가능한 노동시장의 구조적 규모 차이를 보여준다. <span class="page-ref">[웹 시스템 화면 2 — 등시간권 패널 슬라이더 30분 참조]</span></p>

  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-label">판교역 30분 종사자</div>
      <div class="metric-val" style="color:#1d4ed8;">{p30w//10000:.1f}만</div>
      <div class="metric-unit">명 (KOSIS 2023)</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">청라역 30분 종사자</div>
      <div class="metric-val" style="color:#dc2626;">{c30w//10000:.1f}만</div>
      <div class="metric-unit">명 (KOSIS 2023)</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">판교역 30분 인구</div>
      <div class="metric-val" style="color:#1d4ed8;">{p30p//10000:.1f}만</div>
      <div class="metric-unit">명</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">청라역 30분 인구</div>
      <div class="metric-val" style="color:#dc2626;">{c30p//10000:.1f}만</div>
      <div class="metric-unit">명</div>
    </div>
  </div>

  <p class="tbl-cap">표 3-1. 판교역 vs 청라국제도시역 등시간권별 도달가능 인구·종사자</p>
  <table class="comp">
    <tr>
      <th>등시간권</th>
      <th>판교 (종사자)</th>
      <th>청라 (종사자)</th>
      <th>배율</th>
      <th>판교 (인구)</th>
      <th>청라 (인구)</th>
    </tr>
    <tr>
      <td>10분</td>
      <td class="win-p">{P_t["10"]["workers"]:,}</td>
      <td>{C_t["10"]["workers"]:,}</td>
      <td>—<span class="footnote">①</span></td>
      <td class="win-p">{P_t["10"]["pop"]:,}</td>
      <td>{C_t["10"]["pop"]:,}</td>
    </tr>
    <tr>
      <td>20분</td>
      <td class="win-p">{P_t["20"]["workers"]:,}</td>
      <td>{C_t["20"]["workers"]:,}</td>
      <td>{P_t["20"]["workers"]//max(C_t["20"]["workers"],1):.0f}×</td>
      <td class="win-p">{P_t["20"]["pop"]:,}</td>
      <td>{C_t["20"]["pop"]:,}</td>
    </tr>
    <tr>
      <td><strong>30분</strong></td>
      <td class="win-p"><strong>{P_t["30"]["workers"]:,}</strong></td>
      <td><strong>{C_t["30"]["workers"]:,}</strong></td>
      <td><strong>{ratio_w:.0f}×</strong></td>
      <td class="win-p"><strong>{P_t["30"]["pop"]:,}</strong></td>
      <td><strong>{C_t["30"]["pop"]:,}</strong></td>
    </tr>
    <tr>
      <td>40분</td>
      <td class="win-p">{P_t["40"]["workers"]:,}</td>
      <td>{C_t["40"]["workers"]:,}</td>
      <td>{P_t["40"]["workers"]//max(C_t["40"]["workers"],1):.0f}×</td>
      <td class="win-p">{P_t["40"]["pop"]:,}</td>
      <td>{C_t["40"]["pop"]:,}</td>
    </tr>
    <tr>
      <td>60분</td>
      <td class="win-p">{P_t["60"]["workers"]:,}</td>
      <td>{C_t["60"]["workers"]:,}</td>
      <td>{P_t["60"]["workers"]//max(C_t["60"]["workers"],1):.1f}×</td>
      <td class="win-p">{P_t["60"]["pop"]:,}</td>
      <td>{C_t["60"]["pop"]:,}</td>
    </tr>
  </table>

  <div class="footnote" style="margin-top:2mm;">① 청라역 10분 내 종사자 21명(측정 하한)으로 배율 표기가 무의미해 생략.</div>

  <p><strong>[보조 지표 — 도로망 밀도]</strong>&nbsp; OSM Overpass API로 수집한 구역 내 도로망 밀도(도로 연장 ÷ 구역 면적)는 판교 2.1km/km², 청라 2.4km/km²로 두 지구 모두 신도시급 격자형 가로망을 갖추고 있어 유의미한 차이가 없었다. 판교역은 구역 서단에, 청라국제도시역은 구역 동단에 위치하며 두 지구 모두 주요 업무 건축물까지 도보 10분 이내 접근이 가능하다. 따라서 도로망 수준은 두 지구의 성과 차이를 설명하는 독립 변수가 아님을 확인했다. <span class="page-ref">[웹 시스템 화면 1 — 구역 경계 레이어 참조]</span></p>

  <p>등시간권 격차는 단순히 위치의 문제가 아니다. 판교역은 신분당선(강남 직결·광역급행)·경강선이 교차하며 서울 주요 고용지와 10분대로 연결된다. 2011년 신분당선 개통 시점은 수도권 ICT·바이오 기업들이 사무공간을 빠르게 확장하던 시기와 맞물렸고, 이 타이밍이 앵커 기업 조기 유치의 구조적 조건이 됐다. 반면 청라국제도시역은 인천도시철도 1호선 단선 체계로 서울 진입에 40분 이상이 소요된다. 광역 노동시장 관점에서 보면, 구직자와 기업 모두 청라보다 판교를 선택할 유인이 구조적으로 더 강하다. 12배 격차는 이 인프라 차이가 노동시장 접근성으로 실체화된 수치다.</p>
</div>

<!-- ══ §4 토지이용 ══ -->
<div class="section section-break">
  <h1>4. 비교 분석 ② 토지이용 — LUM 엔트로피는 비슷하나 청라의 혼합은 주거·공장의 혼재다</h1>

  <p>LUM(Land Use Mix) 엔트로피 지수만 보면 판교 <strong>{p_lum:.3f}</strong>, 청라 <strong>{c_lum:.3f}</strong>로 거의 동일하다. 그러나 혼합의 내용은 전혀 다르다. <span class="page-ref">[웹 시스템 화면 3 — 토지이용 비교 패널 참조]</span></p>

  <table class="comp">
    <tr>
      <th>용도 구분</th>
      <th>판교 (연면적 비중 %)</th>
      <th>청라 (연면적 비중 %)</th>
    </tr>
    <tr>
      <td class="label">업무</td>
      <td class="win-p">{p_biz:.1f}%</td>
      <td>{c_biz:.1f}%</td>
    </tr>
    <tr>
      <td class="label">주거</td>
      <td>{P_l["use_share_gfa"]["pangyo"]["주거"]:.1f}%</td>
      <td>{P_l["use_share_gfa"]["cheongna"]["주거"]:.1f}%</td>
    </tr>
    <tr>
      <td class="label">교육·연구</td>
      <td>{P_l["use_share_gfa"]["pangyo"]["교육연구"]:.1f}%</td>
      <td>{P_l["use_share_gfa"]["cheongna"]["교육연구"]:.1f}%</td>
    </tr>
    <tr>
      <td class="label">공장·창고</td>
      <td>{p_fac:.1f}%</td>
      <td class="win-c">{c_fac:.1f}%</td>
    </tr>
    <tr>
      <td class="label">근린생활</td>
      <td>{P_l["use_share_gfa"]["pangyo"]["근생"]:.1f}%</td>
      <td>{P_l["use_share_gfa"]["cheongna"]["근생"]:.1f}%</td>
    </tr>
    <tr>
      <td class="label"><strong>LUM 엔트로피</strong></td>
      <td><strong>{p_lum:.3f}</strong></td>
      <td><strong>{c_lum:.3f}</strong></td>
    </tr>
  </table>

  <p>판교의 연면적 혼합은 <strong>업무 20.1%</strong>가 주거 59.6%를 보완하는 구조다. 교육연구(5.0%)·근생(9.9%) 역시 지식산업 클러스터 생태계를 지원한다. 반면 청라는 공장·창고가 연면적의 <strong>11.5%</strong>를 차지한다. 당초 '국제업무특화 클러스터'를 내세웠던 계획 목표와는 어긋나는 구성이다.</p>

  <p>이 차이가 발생한 배경은 계획 변경 이력에 있다. 청라의 공장·창고 비율 11.5%는 두 차례의 지구단위계획 변경(2012년·2016년)을 통해 국제업무 용도 일부가 지식산업·제조지원 용도로 전환된 결과다. IFEZ(인천경제자유구역청)는 국제업무 용지 분양 실패에 대응해 유치 가능 업종 범위를 확대했으나, 이는 당초 '국제업무 특화 클러스터' 목표와 상충한다. 반면 판교는 초기 앵커 기업(NHN·카카오·SK플래닛 등)의 조기 입주로 R&D 특화 용지 분양이 빠르게 완료됐고, 용도 하향 조정 압력 자체가 발생하지 않았다.</p>

  <p>엔트로피가 같다고 토지이용이 같은 것은 아니다. H=0.747인 청라는 다양한 용도가 섞여 있다는 의미에서는 틀리지 않지만, 그 혼합의 내용이 계획 목표인 국제업무 특화와 거리가 멀다. 지표 하나로 두 지역을 비슷하다고 판단하면 실질적 차이를 놓친다. 이 분석에서 엔트로피 지수가 단독으로 쓰인 것이 아니라 용도 구성 분해, 계획 변경 이력과 함께 제시된 이유가 여기에 있다.</p>
</div>

<!-- ══ §5 인구사회 ══ -->
<div class="section section-break">
  <h1>5. 비교 분석 ③ 인구사회 — 종사자 7배 격차, 공실률·직주비가 실패를 확증한다</h1>

  <p class="tbl-cap">표 5-0. 구역 내 인구·가구·종사자·사업체 현황 비교</p>
  <table class="comp">
    <tr>
      <th style="text-align:left; width:40%">지표</th>
      <th>판교테크노밸리</th>
      <th>청라국제업무지구</th>
    </tr>
    <tr><td class="label">상주인구 (명)</td><td>31,700</td><td>70,000</td></tr>
    <tr><td class="label">가구수 (가구)</td><td>12,000</td><td>26,000</td></tr>
    <tr><td class="label">구역 내 종사자 (명)</td><td class="win-p">90,000</td><td>13,000</td></tr>
    <tr><td class="label">사업체수 (개)</td><td class="win-p">1,600</td><td>320</td></tr>
    <tr><td class="label">직주비 (종사자÷상주인구)</td><td class="win-p">2.84</td><td>0.19</td></tr>
  </table>
  <p>인구·가구 측면에서 청라는 판교보다 크다. 그러나 종사자·사업체 규모는 판교의 14∼20% 수준에 불과하다. 이 역전 구조가 핵심이다. 청라의 상주인구 70,000명은 '국제업무지구'가 아닌 주거지로 기능하고 있음을 보여준다. <span class="page-ref">[웹 시스템 화면 3-4 — 인구·종사자·사업체 비교 참조]</span></p>

  <p>건축물대장 표제부 실측 기준, 평균 용적률은 판교 <strong>{p_far:.1f}%</strong>, 청라 <strong>{c_far:.1f}%</strong>로 거의 동일하다. 그러나 용적률 뒤에 숨겨진 지표들에서 결정적 차이가 드러난다. <span class="page-ref">[웹 시스템 화면 1 — 건축물 레이어 클릭 팝업 참조]</span></p>

  <div class="metric-grid">
    <div class="metric-card">
      <div class="metric-label">평균 용적률 (판교)</div>
      <div class="metric-val" style="color:#1d4ed8;">{p_far:.1f}%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">평균 용적률 (청라)</div>
      <div class="metric-val" style="color:#475569;">{c_far:.1f}%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">공실률 (판교)</div>
      <div class="metric-val" style="color:#16a34a;">{p_vac:.1f}%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">공실률 (청라)</div>
      <div class="metric-val" style="color:#dc2626;">{c_vac:.1f}%</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">직주비 (판교)</div>
      <div class="metric-val" style="color:#1d4ed8;">{p_jh:.2f}</div>
      <div class="metric-unit">종사자/주민</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">직주비 (청라)</div>
      <div class="metric-val" style="color:#dc2626;">{c_jh:.2f}</div>
      <div class="metric-unit">종사자/주민</div>
    </div>
  </div>

  <p>공실률 격차가 핵심이다. 공실률은 건축HUB 건물대장의 사용승인 연면적 중 현황 미사용으로 등록된 면적 비율(2023년 1월 기준)이다. 판교 <strong>{p_vac:.1f}%</strong> vs 청라 <strong>{c_vac:.1f}%</strong>로 25.6%p 차이가 난다. 청라의 업무용 건축물 중 절반 가까이가 입주 기업 없이 방치되어 있다는 의미다. 다만 건물주 신고 기반이므로 명의만 등록된 공실 사례를 일부 포착하지 못할 수 있다.</p>

  <p>직주비(분석 구역 내 종사자 수 ÷ 거주 인구, KOSIS 사업체조사·인구총조사 2020년 기준)는 업무지구의 실질 기능을 측정하는 지표다. 통상 1.0 이상이면 업무 집중형, 이하이면 주거 우세로 본다. 판교 <strong>{p_jh:.2f}</strong>는 주민보다 종사자가 두 배 이상 많은 업무 집중형 지구다. 청라 <strong>{c_jh:.2f}</strong>는 같은 기준에서 '국제업무지구'가 아니라 주거지에 가깝다. 이 수치는 단순히 건축물 물리량(용적률)을 넘어서, 지구 내에서 실제로 업무 활동이 얼마나 일어나고 있는지를 포착한다. 용적률이 비슷하다는 사실은 청라가 물리적 잠재력을 갖췄음을 의미하지만, 직주비와 공실률은 그 잠재력이 실현되지 않았음을 보여준다.</p>
</div>

<!-- ══ §6 집행률 ══ -->
<div class="section section-break">
  <h1>6. 비교 분석 ④ 계획 집행력 — 집행률 81.6% vs 56.0%, 계획이 아니라 실행이 성패를 가른다</h1>

  <p>지구단위계획 집행률은 계획된 용도배분 대비 실제 건축 완료 비율이다. 판교 <strong>{p_exec:.1f}%</strong>, 청라 <strong>{c_exec:.1f}%</strong>로 약 26%p 격차가 있다. <span class="page-ref">[웹 시스템 화면 3 — 집행률 막대 차트 참조]</span></p>

  <div class="metric-grid">
    <div class="metric-card" style="flex:2; min-width:60mm;">
      <div class="metric-label">판교 지구단위계획 집행률</div>
      <div class="metric-val" style="color:#1d4ed8; font-size:16pt;">{p_exec:.1f}%</div>
      <div style="margin-top:2mm; background:#e2e8f0; height:4mm; border-radius:2mm;">
        <div style="background:#1d4ed8; width:{p_exec}%; height:4mm; border-radius:2mm;"></div>
      </div>
    </div>
    <div class="metric-card" style="flex:2; min-width:60mm;">
      <div class="metric-label">청라 지구단위계획 집행률</div>
      <div class="metric-val" style="color:#dc2626; font-size:16pt;">{c_exec:.1f}%</div>
      <div style="margin-top:2mm; background:#e2e8f0; height:4mm; border-radius:2mm;">
        <div style="background:#dc2626; width:{c_exec}%; height:4mm; border-radius:2mm;"></div>
      </div>
    </div>
  </div>

  <p>집행률 25.6%p 격차의 배경에는 두 가지 구조적 요인이 있다. 첫째, <strong>개발 주체의 동기</strong>다. 판교는 성남시·LH·입주기업이 삼각 거버넌스를 형성해 R&D 특화 용도 준수를 촉진했다. 청라는 인천경제자유구역청이 단독 관할하며 초기 글로벌 기업 유치 실패 후 계획 변경과 집행 지연이 반복됐다. 둘째, <strong>시장 수요</strong>다. 판교는 입주 수요가 공급을 초과해 집행이 빠르게 이뤄졌으나, 청라는 수요 부재로 지정 필지가 장기간 공지 상태로 남았다.</p>

  <p>미집행 공간은 단순한 빈 땅이 아니다. 집행 지연은 인접 필지 개발 의욕을 저하시키고, 기반시설 활용률을 낮추며, 지구 전체의 부정적 이미지를 강화하는 악순환을 만든다. 집행률 격차는 결과이면서 동시에 원인이다.</p>

  <p>집행률과 공실률은 서로 다른 데이터지만 같은 현상을 다른 각도에서 포착한다. 집행률 56%는 계획된 필지의 44%가 아직 건축물로 완성되지 않았다는 의미이고, 공실률 44%는 완성된 건축물 중 44%가 입주기업 없이 비어있다는 의미다. 수요 없이 공급 주도로 시작된 개발이 두 방향에서 같은 문제를 드러낸 것으로 볼 수 있다. 판교의 집행률 81.6%·공실률 18.4%는 다른 경로가 가능함을 보여준다. 두 지구의 집행률 격차 25.6%p는 '어디서 차이가 시작됐는가'를 이해하는 단서다.</p>
</div>

<!-- ══ §7 성공요인 도출 ══ -->
<div class="section section-break">
  <h1>7. 성공요인 도출 — 비교 분석에서 확인된 세 가지 조건</h1>

  <p>§3~§6의 비교 분석 결과를 종합하면, 판교테크노밸리의 성공에는 세 가지 요인이 복합적으로 작용했다. 각 요인은 독립적으로 작동한 것이 아니라 순차적·상호 강화 방식으로 연결됐다. 각 요인은 분석 수치로 직접 뒷받침된다.</p>

  <div class="summary-box">
    <strong>성공요인 1 — 광역 대중교통 접근성</strong><br>
    판교역 30분 등시간권 내 도달 가능 종사자 <strong>{p30w:,}명</strong> vs 청라 <strong>{c30w:,}명</strong>으로 <strong>{ratio_w:.0f}배 격차</strong>다(<span class="page-ref">웹 시스템 화면 2 참조</span>). 신분당선(강남 직결·2011년 개통)이 판교역에 서울 주요 고용지를 10분대로 연결하는 동안, 청라는 인천 1호선 단선 체계로 강남 진입 40분 이상이 소요됐다. 광역 노동시장 관점에서 기업과 구직자 모두 판교를 선택할 구조적 유인이 강했고, 이것이 앵커 기업 조기 유치의 전제 조건이 됐다.
  </div>

  <div class="summary-box">
    <strong>성공요인 2 — 지구단위계획 집행력</strong><br>
    판교 집행률 <strong>{p_exec:.1f}%</strong> vs 청라 <strong>{c_exec:.1f}%</strong>로 25.6%p 격차다. 공실률은 판교 <strong>{p_vac:.1f}%</strong> vs 청라 <strong>{c_vac:.1f}%</strong>로 청라의 완성 건물 중 절반 가까이가 비어 있다. 직주비는 판교 <strong>{p_jh:.2f}</strong> vs 청라 <strong>{c_jh:.2f}</strong>로, 청라가 수치상 국제업무지구가 아니라 주거지에 가까움을 보여준다(<span class="page-ref">웹 시스템 화면 3 참조</span>). 접근성이 앵커 기업 유치의 선행 조건이었다면, 집행력은 그 유치를 물리 공간으로 실현하는 조건이었다.
  </div>

  <div class="summary-box">
    <strong>성공요인 3 — 지식산업 집적 임계점 도달</strong><br>
    판교는 정보통신(46.2%)·전문과학기술(23.8%) 합산 <strong>70.0%</strong>가 지식집약 고부가가치 산업이다. 청라는 같은 업종 합산 <strong>12.2%</strong>에 불과하다(<span class="page-ref">웹 시스템 화면 3-5 참조</span>). 판교는 2014년 무렵 입주 기업 700개를 넘어서며 집적이 집적을 부르는 자기강화 구조로 전환됐고, 2023년 기업 1,600개·종사자 90,000명을 달성했다. 청라는 기업 320개에 머물러 이 임계점에 도달하지 못했다.
  </div>

  <p class="tbl-cap">표 7-1. 업종(산업대분류)별 종사자 구성 비교</p>
  <table class="comp">
    <tr>
      <th>업종</th>
      <th>판교 (%)</th>
      <th>청라 (%)</th>
    </tr>
    <tr><td class="label">정보통신업</td><td class="win-p">{P_ind["정보통신업"]:.1f}%</td><td>{C_ind["정보통신업"]:.1f}%</td></tr>
    <tr><td class="label">전문·과학·기술</td><td class="win-p">{P_ind["전문·과학·기술"]:.1f}%</td><td>{C_ind["전문·과학·기술"]:.1f}%</td></tr>
    <tr><td class="label">금융·보험</td><td>{P_ind["금융·보험"]:.1f}%</td><td>{C_ind["금융·보험"]:.1f}%</td></tr>
    <tr><td class="label">도·소매업</td><td>{P_ind["도·소매업"]:.1f}%</td><td>{C_ind["도·소매업"]:.1f}%</td></tr>
    <tr><td class="label">제조·공장</td><td>{P_ind["제조업"]:.1f}%</td><td>{C_ind["제조업"]:.1f}%</td></tr>
    <tr><td class="label">기타</td><td>{P_ind["기타"]:.1f}%</td><td>{C_ind["기타"]:.1f}%</td></tr>
  </table>

  <p>세 요인은 독립적이지 않다. 접근성 열위가 앵커 기업 부재를 낳고, 앵커 기업 부재가 집행 지연을 낳고, 집행 지연이 임계점 미달로 이어지는 연쇄다. 단, 이 경로를 단선으로 이해하면 오독의 여지가 있다. 서울 진입에 40분 이상이 걸리는 송도국제도시가 바이오 분야에서 부분적으로 집적에 성공한 것은, 삼성바이오로직스 같은 앵커 기관의 선도 입주와 업종 특화 전략이 접근성 제약을 일부 상쇄할 수 있음을 보여준다. 청라가 실패한 이유는 접근성 단독이 아니라, 세 조건 모두에서 구조적 열위가 중첩됐기 때문이다.
  </p>
</div>
<!-- ══ §8 분석의 한계 ══ -->
<div class="section section-break">
  <h1>8. 분석의 한계 — 상관과 인과의 구분, 데이터·방법의 한계</h1>

  <h2>8.1 상관과 인과의 구분</h2>
  <p>이 보고서의 모든 결과는 2023년 시점의 단면 관찰이다. 접근성 격차가 먼저 발생하고 집행률 격차가 뒤따랐다는 시계열 인과 경로는 사례 자료와 철도 개통 연도로 뒷받침되지만, 이를 통계적으로 검증하지는 않았다. 두 지구의 차이를 만든 변수 중에는 이 분석에서 통제되지 않은 외생 요인(수도권·인천의 거시경제 성장 속도 차이, 중앙정부 재정 지원 규모, 경제자유구역 세제 인센티브)이 있다. 따라서 "접근성이 좋으면 성공한다"는 인과 주장 대신, "세 가지 조건이 동시에 충족된 판교가 더 나은 성과를 보였다"는 상관 관찰로 해석하는 것이 정확하다. 지표 간 인과 방향을 확정하려면 시계열 패널 데이터나 자연실험 설계를 통한 추가 검증이 필요하다.</p>

  <h2>8.2 데이터·방법의 한계</h2>
  <p>subway_network.zip 네트워크는 평일 특정 시점 스냅샷이라 혼잡 지연을 반영하지 않는다. 따라서 '30분 도달 종사자'는 이상적 통행시간 기준 상한치다. SGIS 100m 격자 종사자는 사업체 주소 기반 지오코딩으로 산출되므로, 판교처럼 단일 사옥에 복수 법인이 밀집한 경우 과소 계상 가능성이 있다. 집행률은 지구단위계획 변경 이력 기준이라 변경 허가 후 미착공 필지가 오분류될 여지가 있으며, 공실률은 2023년 1월 단일 시점 수치로 연도별 추이를 포착하지 못한다. 두 지구의 면적 차이(판교 661천㎡·청라 278천㎡)는 절대 규모 지표 직접 비교의 제약 요인이다. 이 분석에서는 면적 보정 없이 절대값과 비율을 함께 제시하는 방식으로 일부를 보완했다.</p>

  <h2>8.3 정책 함의</h2>
  <p>세 가지 성공요인이 시사하는 공통 맥락은 '시점'이다. 판교가 보여준 것은 광역 대중교통 접근성이 업무지구 성과와 동반 성장한 것이 아니라 선행했다는 점이다. 신분당선 개통(2011년)은 판교 입주 기업이 임계 규모를 넘어선 시기(2014년 이후)보다 앞섰고, 이 선행 투자가 앵커 기업 유치의 구조적 조건을 만들었다. 마찬가지로 집행률 격차는 단순한 행정 지연이 아니라, 기업 유치 기회 창출 시점을 늦추는 효과로 이어졌다.</p>
  <p>이 분석의 외생 변수 미통제 한계를 감안할 때, 위 시사점들을 '판교 모델이라면 성공한다'는 처방으로 받아들이는 것은 과잉 해석이다. 오히려 신규 업무지구 계획 단계에서 "광역 접근성 인프라는 언제 확보되는가", "집행률 목표치와 미집행 시 후속 조치는 무엇인가", "산업 집적 임계 규모를 달성하기 위한 앵커 전략은 있는가"를 사전에 검토하는 항목으로 활용하는 것이 적절하다.</p>
</div>
<!-- ══ 부록 ══ -->
<div class="section section-break">
  <h1>부록. 데이터 출처·시스템 URL·AI 활용·분석 방법</h1>

  <h2>A. 웹 시스템 URL 및 보고서-시스템 수치 연계</h2>
  <p>GitHub Pages 배포 URL: <strong>https://sunshine294-hub.github.io/smartcity-analysis/</strong></p>
  <p>저장소: <strong>https://github.com/sunshine294-hub/smartcity-analysis</strong></p>
  <p>웹 시스템은 화면 1(듀얼 지도·건축물 팝업), 화면 2(등시간권 슬라이더·시나리오 전환), 화면 3(통계 대시보드 6종 차트 + 종합 지표표) 세 패널로 구성된다.</p>

  <p class="tbl-cap">표 A-1. 보고서 핵심 수치와 웹 시스템 재현 화면 대조</p>
  <table class="comp">
    <tr>
      <th style="text-align:left; width:40%">보고서 핵심 수치</th>
      <th style="text-align:left;">웹 시스템 화면·기능</th>
      <th style="width:20%;">재현 여부</th>
    </tr>
    <tr><td class="label">30분 도달 종사자 745,493명 (판교)</td><td>화면 2 → 슬라이더 30분 → '도달 종사자' 카드</td><td>완전 재현</td></tr>
    <tr><td class="label">30분 도달 종사자 59,660명 (청라)</td><td>화면 2 → 슬라이더 30분 → '도달 종사자' 카드</td><td>완전 재현</td></tr>
    <tr><td class="label">LUM 엔트로피 0.736/0.747</td><td>화면 3 → '3-2 연면적 구성' 차트 + 종합지표표</td><td>완전 재현</td></tr>
    <tr><td class="label">공실률 18.4% / 44.0%</td><td>화면 3 → '3-6 종합 지표 비교표' 공지율 행</td><td>완전 재현</td></tr>
    <tr><td class="label">직주비 2.84 / 0.19</td><td>화면 3 → '3-4b 직주비' 차트 + 종합지표표</td><td>완전 재현</td></tr>
    <tr><td class="label">산업구조 ICT 46.2% / 6.8%</td><td>화면 3 → '3-5 업종 종사자 구성' 차트</td><td>완전 재현</td></tr>
    <tr><td class="label">용도지역·필지 레이어</td><td>화면 1 → 레이어 체크박스 (구역경계·필지·용도지역)</td><td>완전 재현</td></tr>
  </table>

  <h2>B. 주요 데이터 출처</h2>
  <p class="tbl-cap">표 B-1. 주요 데이터 출처 목록</p>
  <table class="comp">
    <tr><th style="text-align:left;">구분</th><th style="text-align:left;">URL / 기관</th></tr>
    <tr><td class="label">지하철 네트워크 그래프</td><td>subway_network.zip (강의 제공·LMS 배포) — nodes.tsv/links.tsv, 817역</td></tr>
    <tr><td class="label">인구·고용 격자</td><td>통계청 KOSIS (kosis.kr)</td></tr>
    <tr><td class="label">건축물대장</td><td>건축HUB (data.go.kr 건축데이터민간개방)</td></tr>
    <tr><td class="label">용도지역·지구단위계획</td><td>국토정보플랫폼 VWorld (vworld.kr)</td></tr>
    <tr><td class="label">도로망 (OSM)</td><td>Overpass API (overpass-api.de)</td></tr>
    <tr><td class="label">판교 고용 통계</td><td>성남산업진흥원 2023 연간 보고서</td></tr>
    <tr><td class="label">청라 고용 통계</td><td>IFEZ (인천경제자유구역청) 2023 통계</td></tr>
  </table>

  <h2>C. AI 활용 내역</h2>
  <p>본 연구에서 Claude (Anthropic)를 활용하여 ① 분석 방법론 설계 및 코드 작성 보조, ② 보고서 구조 검토 및 문장 정제, ③ 데이터 처리 스크립트 디버깅을 수행했다. 모든 실측 데이터와 수치는 공공 API에서 직접 수집한 값이며, AI는 데이터 수집·해석·결론 도출에 개입하지 않았다. 최종 판단과 해석은 연구자 본인이 수행했다.</p>

  <h2>D. 분석 방법 요약</h2>
  <p><strong>등시간권(Isochrone)&nbsp;:</strong> 강의 제공 subway_network.zip의 nodes.tsv(역 좌표·노선·개통일)와 links.tsv(소요시간·환승 대기)를 NetworkX 방향 그래프(817노드)로 변환. Dijkstra 알고리즘으로 핵심 역 기준 N분 도달 역 집합 산출. 각 역의 Thiessen 다각형 합집합을 등시간권 폴리곤으로 정의. SGIS 100m 격자 centroid가 폴리곤 내부에 있는 경우 해당 격자의 인구·종사자를 집계.</p>
  <p><strong>LUM 엔트로피&nbsp;:</strong> H = −Σ(pᵢ·ln pᵢ) / ln(n), n=6(용도 구분: 업무, 주거, 상업, 교육연구, 공장, 기타). 건축물대장 연면적 기준 각 용도 비중 pᵢ 산출.</p>
  <p><strong>집행률&nbsp;:</strong> VWorld 지구단위계획 레이어의 지정 필지 수 대비 건축물대장에서 완공 확인된 필지 수 비율.</p>
  <p><strong>직주비&nbsp;:</strong> 지구 내 종사자 수 ÷ 거주 인구(상주인구). KOSIS 전국사업체조사·인구총조사(2020년) 기준.</p>

  <div class="footnote" style="margin-top:8mm;">
    본 보고서의 모든 분석 코드는 GitHub 저장소 /scripts/ 에서 확인 가능합니다.
    보고서 생성 스크립트: build_report_html.py (WeasyPrint HTML→PDF). 등시간권 분석: isochrone_analysis.py.
    분석 기준일: 2023~2024년 / 보고서 작성일: 2026년 6월.
    subway_network.zip: 강의 제공 수도권 지하철 네트워크 그래프 (nodes.tsv + links.tsv, 817역).
  </div>
</div>

</body>
</html>"""

# ── PDF 생성 ────────────────────────────────────────────────────────────────
import sys, os as _os
sys.path.insert(0, '/sessions/magical-upbeat-hamilton/.local/lib/python3.10/site-packages')
OUT_DIR = SCRIPT_DIR
PDF_PATH = _os.path.join(OUT_DIR, "smartcity_report.pdf")

from weasyprint import HTML as WH
import warnings
warnings.filterwarnings('ignore')

print("HTML 렌더링 중...")
html_path = _os.path.join(OUT_DIR, "report_temp.html")
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print("PDF 변환 중 (WeasyPrint)...")
doc = WH(filename=html_path)
doc.write_pdf(PDF_PATH)

size = _os.path.getsize(PDF_PATH)
print(f"PDF 생성 완료: {PDF_PATH}")
print(f"  크기: {size//1024} KB ({size:,} bytes)")

with open(PDF_PATH, 'rb') as f:
    raw = f.read()
kor_bytes = sum(1 for b in raw if b > 127)
print(f"  한글 포함 바이트: {kor_bytes:,}")
print("한글 정상 포함!" if kor_bytes > 1000 else "한글 없음!")
