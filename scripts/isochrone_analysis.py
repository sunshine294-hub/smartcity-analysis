#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수도권 지하철 네트워크 등시간권(isochrone) 분석
================================================

출발지(업무지구 핵심역) 2곳:
  (a) 판교       — 신분당선 + 경강선 노드 (statnm=='판교')
  (b) 청라국제도시 — 공항철도 노드 (statnm=='청라국제도시')

데이터 출처:
  /sessions/magical-upbeat-hamilton/mnt/outputs/subway_network/
  - network/nodes.tsv  : 노드 (환승역은 노선별로 분리, EPSG:5179 meter 좌표 포함)
  - network/links.tsv  : 링크 (timeFT/timeTF 초, kind=subway/transfer,
                         transfer 링크에는 도착노선 배차 대기시간이 이미 포함, 비대칭)
  - line_waits.parquet : 노선별 배차간격(초) — 첫 탑승 대기시간으로 사용
  - opening.tsv        : 노선 개통 시점 (시나리오 cutoff 결정)
  (OSM, KRRI 보고서, 사업자 보도자료 기반 수작업 데이터 — README.md 참고)

분석 가정 (보고서 명시 사항):
  * 기준시점 시나리오 3종 (begin/effective_begin 문자열 lexicographic 비교):
      - 'current' : T0 = 2026-05-04 (opening.tsv 의 '현재')
      - 'future'  : T1 = 2032-12-31 (GTX-B/C, 신안산선, 동북선, 위례선,
                    GTX_A 서울역-수서 연결 등 미래 노선 전부 개통 가정)
      - 'pre_gtx' : T2 = 2024-12-17 (GTX_A 개통 2024-12-18 전일, 판교만 분석)
    활성 노드: effective_begin(있으면) 또는 begin <= T.
    활성 링크: begin <= T 이고 양 끝 노드가 모두 활성.
  * 그래프: timeFT(from→to), timeTF(to→from)를 각각 별도의 directed edge 로
    전개한 방향그래프. scipy.sparse.csgraph.dijkstra 사용.
  * 첫 탑승 대기: 가상 출발노드 → 각 출발역 노드 edge 비용 = 해당 노선의
    line_waits.waittm(초). transfer 링크의 대기 정책(waittm 전체 가산)과 일관.
    line_waits 에 없는 노선은 0초.
  * 등시간권 폴리곤 (시간임계 t ∈ {10,20,30,40,50,60}분):
    도달시간 s(분) <= t 인 각 역에 대해 잔여시간 (t-s)분 동안 도보 확산.
      - 도보속도 4 km/h ≒ 67 m/분 (가정)
      - 역 출구 도보권 상한 800 m (가정)
      - 버퍼 반경 = min((t-s)*67, 800) m — EPSG:5179(meter) 평면에서 버퍼
    모든 도달역 버퍼 union → (multi)polygon → simplify(50 m) → WGS84 변환.

산출물 (/sessions/magical-upbeat-hamilton/mnt/outputs/project/data/):
  - isochrones.geojson          전 시나리오 등시간권 FeatureCollection
  - station_times.json          역별 최단 도달시간 (current 시나리오)
  - accessibility_summary.json  시나리오·임계별 도달 역 수 / 폴리곤 면적
"""

import json
import os

import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import Point, mapping
from shapely.ops import transform as shp_transform
from shapely.ops import unary_union

# ---------------------------------------------------------------- 경로/상수
BASE = '/sessions/magical-upbeat-hamilton/mnt/outputs'
NET = os.path.join(BASE, 'subway_network')
OUT = os.path.join(BASE, 'project', 'data')
os.makedirs(OUT, exist_ok=True)

T0 = '2026-05-04'   # current  (opening.tsv '현재')
T1 = '2032-12-31'   # future   (GTX-C 까지 전부 개통 가정)
T2 = '2024-12-17'   # pre_gtx  (GTX_A 개통 2024-12-18 전일)

THRESHOLDS = [10, 20, 30, 40, 50, 60]   # 분
WALK_M_PER_MIN = 67.0                   # 도보 4 km/h ≒ 67 m/분 (가정)
WALK_CAP_M = 800.0                      # 역 출구 도보권 상한 800 m (가정)
SIMPLIFY_M = 50.0                       # 폴리곤 단순화 tolerance (m)

# ---------------------------------------------------------------- 데이터 로드
nodes = pd.read_csv(os.path.join(NET, 'network/nodes.tsv'), sep='\t',
                    dtype={'begin': str, 'effective_begin': str})
nodes['effective_begin'] = nodes['effective_begin'].fillna('')
links = pd.read_csv(os.path.join(NET, 'network/links.tsv'), sep='\t',
                    dtype={'begin': str})
line_waits = pd.read_parquet(os.path.join(NET, 'line_waits.parquet'))
WAIT = dict(zip(line_waits['linenm'], line_waits['waittm'].astype(float)))

V = len(nodes)
# 운영 시작일: effective_begin 이 있으면 그것, 없으면 begin (README 규칙)
nodes['eff'] = nodes['effective_begin'].where(nodes['effective_begin'] != '',
                                              nodes['begin'])

# EPSG:5179 (meter) -> EPSG:4326 (lng/lat) 변환기
TR = Transformer.from_crs('EPSG:5179', 'EPSG:4326', always_xy=True)


def active_sets(T):
    """시점 T 의 활성 노드 boolean mask 와 활성 링크 DataFrame."""
    node_mask = (nodes['eff'] <= T).to_numpy()
    active_ids = set(nodes.loc[node_mask, 'id'])
    lk = links[(links['begin'] <= T)
               & links['fromNode'].isin(active_ids)
               & links['toNode'].isin(active_ids)]
    return node_mask, lk


def shortest_minutes(T, origin_statnm):
    """시점 T 네트워크에서 origin_statnm 역(노선별 복수 노드 가능) 출발
    전 노드 최단시간(분). 가상 출발노드(index V)에서 각 출발역 노드로
    해당 노선 배차간격(waittm 초)짜리 edge 를 걸어 첫 탑승 대기를 반영."""
    node_mask, lk = active_sets(T)

    start_nodes = nodes[(nodes['statnm'] == origin_statnm) & node_mask]
    if start_nodes.empty:
        raise ValueError(f'{origin_statnm}: 시점 {T} 에 활성 노드 없음')

    u = lk['fromNode'].to_numpy()
    v = lk['toNode'].to_numpy()
    # 양방향 directed 전개: timeFT (u→v), timeTF (v→u)
    src = np.concatenate([u, v])
    dst = np.concatenate([v, u])
    cost = np.concatenate([lk['timeFT'].to_numpy(),
                           lk['timeTF'].to_numpy()]).astype(np.float64)
    # 가상 출발노드 V → 출발역 노드들 (cost = 노선 배차간격, 없으면 0)
    s_ids = start_nodes['id'].to_numpy()
    s_cost = np.array([WAIT.get(ln, 0.0) for ln in start_nodes['linenm']],
                      dtype=np.float64)
    src = np.concatenate([src, np.full(len(s_ids), V)])
    dst = np.concatenate([dst, s_ids])
    cost = np.concatenate([cost, s_cost])

    A = csr_matrix((cost, (src, dst)), shape=(V + 1, V + 1))
    sec = dijkstra(A, directed=True, indices=V)[:V]
    sec[~node_mask] = np.inf          # 비활성 노드는 도달 불가 처리
    return sec / 60.0, node_mask      # 분 단위


def isochrone_features(minutes, node_mask, region, scenario):
    """임계별 등시간권 폴리곤 feature 목록과 (임계→{역수, 면적}) 요약."""
    feats, summary = [], {}
    xs = nodes['x_5179'].to_numpy()
    ys = nodes['y_5179'].to_numpy()
    for t in THRESHOLDS:
        reach = node_mask & np.isfinite(minutes) & (minutes <= t)
        idx = np.where(reach)[0]
        # 잔여시간 도보 확산: 반경 = min((t-s)*67m, 800m)
        bufs = [Point(xs[i], ys[i]).buffer(
                    min((t - minutes[i]) * WALK_M_PER_MIN, WALK_CAP_M))
                for i in idx]
        poly = unary_union(bufs).simplify(SIMPLIFY_M)
        area_km2 = poly.area / 1e6           # EPSG:5179 평면 면적
        poly_wgs = shp_transform(TR.transform, poly)
        feats.append({
            'type': 'Feature',
            'properties': {'region': region, 'minutes': t,
                           'scenario': scenario},
            'geometry': mapping(poly_wgs),
        })
        summary[t] = {
            'stations_reached_unique_name':
                int(nodes.loc[reach, 'statnm'].nunique()),
            'station_nodes_reached': int(reach.sum()),
            'polygon_area_km2': round(area_km2, 2),
        }
    return feats, summary


# ---------------------------------------------------------------- 시나리오 실행
SCENARIOS = [
    # (scenario, T, region, origin_statnm)
    ('current', T0, 'pangyo',   '판교'),
    ('current', T0, 'cheongna', '청라국제도시'),
    ('future',  T1, 'pangyo',   '판교'),
    ('future',  T1, 'cheongna', '청라국제도시'),
    ('pre_gtx', T2, 'pangyo',   '판교'),
]

all_features = []
summary = {'assumptions': {
    'walk_speed_m_per_min': WALK_M_PER_MIN,
    'walk_radius_cap_m': WALK_CAP_M,
    'simplify_tolerance_m': SIMPLIFY_M,
    'first_boarding_wait': 'line_waits.waittm(초) 전체를 가상출발 edge 비용으로 가산',
    'crs_buffer': 'EPSG:5179', 'crs_output': 'EPSG:4326',
    'scenario_dates': {'current': T0, 'future': T1, 'pre_gtx': T2},
}, 'scenarios': {}}
minutes_store = {}   # (scenario, region) -> (minutes, node_mask)

for scenario, T, region, statnm in SCENARIOS:
    mins, mask = shortest_minutes(T, statnm)
    minutes_store[(scenario, region)] = (mins, mask)
    feats, summ = isochrone_features(mins, mask, region, scenario)
    all_features.extend(feats)
    unreachable = int((mask & ~np.isfinite(mins)).sum())
    summary['scenarios'].setdefault(scenario, {})[region] = {
        'origin_statnm': statnm, 'cutoff_date': T,
        'active_station_nodes': int(mask.sum()),
        'active_stations_unique_name':
            int(nodes.loc[mask, 'statnm'].nunique()),
        'unreachable_active_nodes': unreachable,
        'by_threshold_min': summ,
    }

with open(os.path.join(OUT, 'isochrones.geojson'), 'w', encoding='utf-8') as f:
    json.dump({'type': 'FeatureCollection', 'features': all_features},
              f, ensure_ascii=False)

# ---------------------------------------------------------------- station_times.json
# current 시나리오 활성역 전체의 역별 최단시간 (노선별 노드 단위 stations +
# 역명 기준 최소시간 통합본 stations_merged)
mins_p, mask_cur = minutes_store[('current', 'pangyo')]
mins_c, _ = minutes_store[('current', 'cheongna')]


def _m(v):
    return round(float(v), 2) if np.isfinite(v) else None


cur_idx = np.where(mask_cur)[0]
st_rows = []
for i in cur_idx:
    r = nodes.iloc[i]
    st_rows.append({'statnm': r['statnm'], 'linenm': r['linenm'],
                    'lng': round(float(r['lng']), 6),
                    'lat': round(float(r['lat']), 6),
                    'min_pangyo': _m(mins_p[i]),
                    'min_cheongna': _m(mins_c[i])})

# 역명 기준 통합: 환승역은 노선별 노드 중 최소시간, 좌표는 노드 평균
df = pd.DataFrame(st_rows)
df['_p'] = mins_p[cur_idx]
df['_c'] = mins_c[cur_idx]
merged = (df.groupby('statnm')
            .agg(lines=('linenm', lambda s: sorted(set(s))),
                 lng=('lng', 'mean'), lat=('lat', 'mean'),
                 _p=('_p', 'min'), _c=('_c', 'min')).reset_index())
st_merged = [{'statnm': r['statnm'], 'lines': r['lines'],
              'lng': round(r['lng'], 6), 'lat': round(r['lat'], 6),
              'min_pangyo': _m(r['_p']), 'min_cheongna': _m(r['_c'])}
             for _, r in merged.iterrows()]

with open(os.path.join(OUT, 'station_times.json'), 'w', encoding='utf-8') as f:
    json.dump({'scenario': 'current', 'cutoff_date': T0,
               'stations': st_rows, 'stations_merged': st_merged},
              f, ensure_ascii=False)


# ---------------------------------------------------------------- 검증
def best_time(minutes, statnm):
    """역명 기준 최소 도달시간 (환승역은 노선별 노드 중 최소)."""
    v = minutes[(nodes['statnm'] == statnm).to_numpy()]
    v = v[np.isfinite(v)]
    return round(float(v.min()), 2) if len(v) else None


validation = {
    'pangyo_to_gangnam_min': best_time(mins_p, '강남'),
    'cheongna_to_seoulstation_min': best_time(mins_c, '서울역'),
    'pangyo_to_cheongna_min': best_time(mins_p, '청라국제도시'),
    'cheongna_to_pangyo_min': best_time(mins_c, '판교'),
    'negative_or_zero_times': int(((mins_p[cur_idx] <= 0).sum())
                                  + ((mins_c[cur_idx] <= 0).sum())),
    'unreachable_active_nodes_pangyo_current':
        int((mask_cur & ~np.isfinite(mins_p)).sum()),
    'unreachable_active_nodes_cheongna_current':
        int((mask_cur & ~np.isfinite(mins_c)).sum()),
}
summary['validation'] = validation

with open(os.path.join(OUT, 'accessibility_summary.json'), 'w',
          encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- 콘솔 리포트
print('=== validation ===')
for k, v in validation.items():
    print(f'  {k}: {v}')
print('=== summary (unique stations reached / polygon area km2) ===')
for sc, regions in summary['scenarios'].items():
    for rg, info in regions.items():
        row = ', '.join(
            f"{t}m:{d['stations_reached_unique_name']}/{d['polygon_area_km2']}"
            for t, d in info['by_threshold_min'].items())
        print(f'  [{sc}/{rg}] active={info["active_station_nodes"]}nodes '
              f'unreach={info["unreachable_active_nodes"]} | {row}')
print('done ->', OUT)
