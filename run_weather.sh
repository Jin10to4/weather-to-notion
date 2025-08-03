#!/bin/bash
# 가상환경 활성화
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate notion-env

echo ">>> Notion-env 환경 활성화 완료"

# 테스트 실행
# python test_env.py

# 단기 파일 실행 - 실패
# python weather_to_notion.py

# 초단기 파일 실행
python weather_to_notion_ultrasrt.py