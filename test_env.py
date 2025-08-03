# test_env.py
from dotenv import load_dotenv
import os
import requests
from notion_client import Client

print("=== 라이브러리 테스트 시작 ===")

# 1) dotenv 테스트
try:
    load_dotenv(dotenv_path="env.txt")  # 또는 .env
    notion_token = os.getenv("NOTION_TOKEN")
    weather_key = os.getenv("WEATHER_API_KEY")

    print(f"NOTION_TOKEN: {notion_token[:8]}****" if notion_token else "NOTION_TOKEN 없음")
    print(f"WEATHER_API_KEY: {weather_key[:8]}****" if weather_key else "WEATHER_API_KEY 없음")
except Exception as e:
    print("dotenv 테스트 실패:", e)

# 2) requests 테스트
try:
    response = requests.get("https://httpbin.org/get")
    if response.status_code == 200:
        print("requests 라이브러리 정상 작동")
    else:
        print("requests 오류:", response.status_code)
except Exception as e:
    print("requests 테스트 실패:", e)

# 3) notion_client 테스트
try:
    # 토큰이 없는 경우는 스킵
    if notion_token:
        notion = Client(auth=notion_token)
        print("notion_client 라이브러리 정상 작동 (토큰 OK)")
    else:
        print("notion_client 테스트: 토큰 없음 (OK)")
except Exception as e:
    print("notion_client 테스트 실패:", e)

print("=== 테스트 완료 ===")
