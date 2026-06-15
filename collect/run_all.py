#!/usr/bin/env python3
"""
collect/run_all.py
판교·청라 공간데이터 일괄 수집 스크립트
실행 전: collect/config.py에 API 키 입력 필수

출력: data_out/ 폴더
  - landuse_pangyo.geojson / landuse_cheongna.geojson  (VWorld 용도지역)
  - parcels_pangyo.geojson / parcels_cheongna.geojson  (건축HUB)
  - regions.geojson                                     (구역 경계)
  - grid_pop.csv / grid_workers.csv                     (KOSIS 격자 — 수동 다운로드)
"""
import os, sys

try:
    import config
except ImportError:
    print("[오류] config.py가 없습니다.")
    print("  cp collect/config_example.py collect/config.py 후 API 키를 입력하세요.")
    sys.exit(1)

print("수집 스크립트 실행 준비 완료.")
print(f"  VWorld KEY: {'설정됨' if config.VWORLD_KEY != '여기에_VWorld_API_키_입력' else '미설정'}")
print(f"  건축HUB KEY: {'설정됨' if config.BUILDING_KEY != '여기에_공공데이터포털_API_키_입력' else '미설정'}")
print(f"  SGIS KEY: {'설정됨' if config.SGIS_KEY != '여기에_SGIS_API_KEY_입력' else '미설정'}")
print()
print("[안내] 실제 수집 구현은 scripts/isochrone_analysis.py 참조.")
print("       KOSIS 격자 데이터는 https://mdis.kostat.go.kr 에서 수동 다운로드 필요.")
