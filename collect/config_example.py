# ──────────────────────────────────────────────────────────────
# collect/config_example.py
# 사용법: cp config_example.py config.py 후 본인 키 입력
# ──────────────────────────────────────────────────────────────

# VWorld Data API (국토정보플랫폼)
# 발급: https://www.vworld.kr/dev/v4dv_apikey_v2.do
VWORLD_KEY = "여기에_VWorld_API_키_입력"

# 공공데이터포털 — 건축HUB (건축물대장 표제부)
# 발급: https://www.data.go.kr → 건축데이터민간개방 API 신청
BUILDING_KEY = "여기에_공공데이터포털_API_키_입력"

# SGIS 통계지리정보서비스 (격자 인구·종사자)
# 발급: https://sgis.kostat.go.kr/developer/html/openApi/api/index.html
SGIS_KEY    = "여기에_SGIS_API_KEY_입력"
SGIS_SECRET = "여기에_SGIS_SECRET_입력"

# ── 분석 구역 설정 ───────────────────────────────────────────
# 판교테크노밸리 — 지구단위계획구역코드 (VWorld)
PANGYO_ZONE_CODE = "4113500001"

# 청라국제업무지구 — VWorld LT_C_UPISUQ153 레이어 명칭
CHEONGNA_ZONE_NAME = "청라국제업무지구 도시개발구역"
