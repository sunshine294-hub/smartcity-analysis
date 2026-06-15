#!/bin/bash
# deploy.sh — GitHub Pages 원클릭 배포 스크립트
# 사용법: bash deploy.sh <github-username> <repo-name>
# 예시:  bash deploy.sh gangg smartcity-analysis

set -e

USERNAME=${1:-"your-username"}
REPO=${2:-"smartcity-analysis"}

echo "=== 판교 vs 청라 비교분석 시스템 GitHub Pages 배포 ==="
echo "저장소: https://github.com/${USERNAME}/${REPO}"
echo ""

if ! git rev-parse --is-inside-work-tree &>/dev/null; then
  echo "[1/4] Git 초기화..."
  git init
  git add .
  git commit -m "init: 판교 vs 청라 비교분석 시스템"
  git branch -M main
  git remote add origin "https://github.com/${USERNAME}/${REPO}.git"
else
  echo "[1/4] 기존 Git 저장소 감지됨"
  git add .
  git commit -m "update: $(date '+%Y-%m-%d %H:%M')" || echo "변경사항 없음"
fi

echo "[2/4] GitHub push..."
git push -u origin main

echo "[3/4] 완료!"
echo ""
echo "배포 URL (약 1~2분 후 접근 가능):"
echo "  https://${USERNAME}.github.io/${REPO}/"
echo ""
echo "[4/4] 보고서 PDF URL 업데이트 필요:"
echo "  smartcity_report.pdf 표지 및 부록 A의 [username]을 '${USERNAME}'으로 변경 후 재빌드"
echo "  python3 scripts/build_report_html.py"
