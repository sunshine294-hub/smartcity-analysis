#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
placeholder 데이터 생성기 (실데이터 수집 전 개발용)
=====================================================
생성 파일 (모두 meta.placeholder=true):
  data/regions.geojson
  data/landuse_pangyo.geojson, data/landuse_cheongna.geojson
  data/parcels_pangyo.geojson,  data/parcels_cheongna.geojson
  data/stats.json   (단, transport.reach 의 stations/area_km2 는
                     data/accessibility_summary.json 실측치를 주입 — placeholder 아님)

실데이터(collect/ 수집 결과)가 준비되면 같은 스키마로 파일만 교체하면 된다.
교체 시 meta.placeholder=false 로 두면 UI의 '표본 데이터' 배지가 사라진다.
"""
import json, math, random, os, datetime

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DATA = os.path.join(BASE, 'data')

random.seed(20260613)

REGIONS = {
    'pangyo': {
        'name': '판교테크노밸리(제1판교)',
        'bbox': (127.092, 37.395, 127.112, 37.410),
        'area_m2': 661000,      # 공식 고시 면적(판교TV 공식 개요) — 실측치
        'source': '경계 geometry는 placeholder(대략 위치 사각형). 면적은 판교TV 공식 개요(661천m2). 추후 지구단위계획(도시지원시설용지) 폴리곤으로 교체',
    },
    'cheongna': {
        'name': '청라국제업무지구',
        'bbox': (126.630, 37.530, 126.660, 37.550),
        'area_m2': 278000,      # 공식 고시 면적(IFEZ 프로젝트 15) — 실측치
        'source': '경계 geometry는 placeholder(대략 위치 사각형). 면적은 IFEZ 공식 사업개요(278천m2, B1·B2·B9·B10·C1·C2·M5·M6). 추후 IFEZ 지구단위계획 블록 디졸브로 교체',
    },
}

def rect_coords(x0, y0, x1, y1):
    return [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]

def cell_area_m2(bbox):
    x0, y0, x1, y1 = bbox
    lat = (y0 + y1) / 2
    dx = (x1 - x0) * 111320 * math.cos(math.radians(lat))
    dy = (y1 - y0) * 110540
    return round(dx * dy)

def fc(features, note=''):
    return {
        'type': 'FeatureCollection',
        'meta': {
            'placeholder': True,
            'generated': datetime.date.today().isoformat(),
            'note': note or '표본(placeholder) 데이터 — 실데이터 수집 후 동일 스키마로 교체 예정',
        },
        'features': features,
    }

# ---------------------------------------------------------------- regions
def make_regions():
    feats = []
    for rid, r in REGIONS.items():
        x0, y0, x1, y1 = r['bbox']
        feats.append({
            'type': 'Feature',
            'properties': {'region': rid, 'name': r['name'],
                           'area_m2': r['area_m2'], 'source': r['source']},
            'geometry': {'type': 'Polygon', 'coordinates': rect_coords(x0, y0, x1, y1)},
        })
    return fc(feats)

# ---------------------------------------------------------------- landuse
LANDUSE = {
    'pangyo': [   # (zone, 세로 밴드 비율) — 합계 1.0
        ('일반상업지역', 0.125), ('준주거지역', 0.098), ('제3종일반주거지역', 0.224),
        ('준공업지역', 0.252), ('자연녹지지역', 0.301),
    ],
    'cheongna': [
        ('일반상업지역', 0.187), ('준주거지역', 0.123), ('제2종일반주거지역', 0.256),
        ('제3종일반주거지역', 0.164), ('자연녹지지역', 0.270),
    ],
}

def make_landuse(rid):
    x0, y0, x1, y1 = REGIONS[rid]['bbox']
    feats, cur = [], x0
    for zone, share in LANDUSE[rid]:
        nx = cur + (x1 - x0) * share
        feats.append({'type': 'Feature', 'properties': {'zone': zone},
                      'geometry': {'type': 'Polygon', 'coordinates': rect_coords(cur, y0, nx, y1)}})
        cur = nx
    return fc(feats)

# ---------------------------------------------------------------- parcels
# 판교: 고밀 업무·연구 위주 / 청라: 미개발 다수(공지) + 일부 주거·근생
USE_W = {
    'pangyo':   [('업무', 0.52), ('근생', 0.14), ('주거', 0.10), ('교육연구', 0.16), ('기타', 0.08)],
    'cheongna': [('주거', 0.28), ('업무', 0.24), ('근생', 0.26), ('교육연구', 0.06), ('기타', 0.16)],
}
SKIP = {'pangyo': 0.12, 'cheongna': 0.55}      # 공지(미개발) 비율 표현
MAIN_USE = {'업무': '업무시설', '주거': '공동주택', '근생': '제2종근린생활시설',
            '교육연구': '교육연구시설', '기타': '문화및집회시설'}
FAR_RANGE = {'업무': (250, 480), '주거': (180, 300), '근생': (150, 350),
             '교육연구': (120, 250), '기타': (80, 200)}

def pick_use(rid):
    r, acc = random.random(), 0.0
    for g, w in USE_W[rid]:
        acc += w
        if r <= acc:
            return g
    return '기타'

def make_parcels(rid):
    x0, y0, x1, y1 = REGIONS[rid]['bbox']
    mx, my = (x1 - x0) * 0.05, (y1 - y0) * 0.07
    x0, y0, x1, y1 = x0 + mx, y0 + my, x1 - mx, y1 - my
    nx, ny = 10, 6
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    prefix = '판교' if rid == 'pangyo' else '청라'
    feats = []
    for j in range(ny):
        for i in range(nx):
            if random.random() < SKIP[rid]:    # 공지/미개발 — 필지 미생성
                continue
            g = pick_use(rid)
            cx0 = x0 + i * dx + dx * 0.12
            cy0 = y0 + j * dy + dy * 0.12
            cx1 = x0 + (i + 1) * dx - dx * 0.12
            cy1 = y0 + (j + 1) * dy - dy * 0.12
            land = cell_area_m2((cx0, cy0, cx1, cy1))
            far = random.uniform(*FAR_RANGE[g])
            bcr = random.uniform(35, 60)
            floors = max(2, int(far / bcr * 100 / 18)) + random.randint(0, 8)
            feats.append({
                'type': 'Feature',
                'properties': {
                    'name': f'{prefix} {chr(65 + j)}-{i + 1} ({MAIN_USE[g]})',
                    'main_use': MAIN_USE[g],
                    'use_group': g,
                    'gfa_m2': round(land * far / 100),
                    'land_m2': land,
                    'far': round(far, 1),
                    'bcr': round(bcr, 1),
                    'floors': floors,
                },
                'geometry': {'type': 'Polygon', 'coordinates': rect_coords(cx0, cy0, cx1, cy1)},
            })
    return fc(feats)

# ---------------------------------------------------------------- stats.json
def make_stats():
    with open(os.path.join(DATA, 'accessibility_summary.json'), encoding='utf-8') as f:
        acc = json.load(f)

    reach = {}
    for sc, regions in acc['scenarios'].items():
        reach[sc] = {}
        for rid, body in regions.items():
            reach[sc][rid] = {}
            for m, v in body['by_threshold_min'].items():
                reach[sc][rid][m] = {
                    'pop': None,        # 미산출 — SGIS 집계구 수집 후 산출·교체
                    'workers': None,    # 미산출
                    'stations': v['stations_reached_unique_name'],   # 실측 (placeholder 아님)
                    'area_km2': v['polygon_area_km2'],               # 실측 (placeholder 아님)
                }

    # 누적 접근성 곡선 placeholder (로지스틱 형태 표본값, 0~60분 5분 간격)
    def curve(pop60, wk60, mid, steep):
        pts = []
        for m in range(0, 61, 5):
            f = 1 / (1 + math.exp(-(m - mid) / steep))
            f0 = 1 / (1 + math.exp(mid / steep))
            f = max(0.0, (f - f0) / (1 - f0))
            pts.append({'min': m, 'pop': round(pop60 * f / 1000) * 1000,
                        'workers': round(wk60 * f / 1000) * 1000})
        return pts

    return {
        'meta': {
            'pop_year': 2025, 'comp_year': 2023,
            'generated': datetime.date.today().isoformat(),
            'placeholder': True,
            'note': 'socio·industry·landuse·curve는 표본값. transport.reach의 stations·area_km2만 accessibility_summary.json 실측치(pop·workers는 null=미산출).',
        },
        'landuse': {
            'zone_share': {rid: {z: round(s * 100, 1) for z, s in LANDUSE[rid]} for rid in REGIONS},
            'use_share_gfa': {
                'pangyo':   {'업무': 58.2, '주거': 12.5, '근생': 11.4, '교육연구': 12.6, '기타': 5.3},
                'cheongna': {'업무': 30.5, '주거': 26.2, '근생': 24.4, '교육연구': 4.1, '기타': 14.8},
            },
            'lum': {'pangyo': 0.58, 'cheongna': 0.66},
            'far_avg': {'pangyo': 312.0, 'cheongna': 214.0},
            'vacant_ratio': {'pangyo': 4.2, 'cheongna': 62.5},
        },
        'transport': {
            'reach': reach,
            'curve': {
                'pangyo':   curve(9_480_000, 5_210_000, 42, 9),
                'cheongna': curve(6_730_000, 3_080_000, 47, 9),
            },
        },
        'socio': {
            'pangyo':   {'pop': 3_800, 'hh': 1_600, 'workers': 66_800, 'corps': 1_196, 'jh_ratio': 17.6},
            'cheongna': {'pop': 2_100, 'hh': 850,  'workers': 3_100,  'corps': 140,   'jh_ratio': 1.5},
        },
        'industry': {
            'pangyo':   {'정보통신업': 46.2, '전문·과학·기술서비스업': 23.8, '제조업': 11.4,
                         '금융·보험업': 6.2, '도매·소매업': 5.1, '숙박·음식점업': 0.0, '기타': 7.3},
            'cheongna': {'정보통신업': 6.8, '전문·과학·기술서비스업': 5.4, '제조업': 0.0,
                         '금융·보험업': 38.4, '도매·소매업': 18.5, '숙박·음식점업': 12.2, '기타': 18.7},
        },
    }

def main():
    out = {
        'regions.geojson': make_regions(),
        'landuse_pangyo.geojson': make_landuse('pangyo'),
        'landuse_cheongna.geojson': make_landuse('cheongna'),
        'parcels_pangyo.geojson': make_parcels('pangyo'),
        'parcels_cheongna.geojson': make_parcels('cheongna'),
        'stats.json': make_stats(),
    }
    for fn, obj in out.items():
        p = os.path.join(DATA, fn)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
        print('wrote', fn)

if __name__ == '__main__':
    main()
