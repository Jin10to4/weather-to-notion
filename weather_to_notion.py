# weather_to_notion.py
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from notion_client import Client

# 1. 환경 변수 로드
load_dotenv("env.txt")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NX = os.getenv("NX")
NY = os.getenv("NY")

notion = Client(auth=NOTION_TOKEN)

# 2. 기상청 단기예보 API 호출
def get_weather():
    # 현재 시각에서 발표 시간(매시 정각)으로 조정
    now = datetime.now()
    if now.minute < 45:  # 기상청 API 특성상 45분 전에는 이전 시간 발표자료 사용
        now = now - timedelta(hours=1)

    base_date = now.strftime("%Y%m%d")  # 발표 날짜
    base_time = now.strftime("%H00")    # 발표 시각 (정각)

    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        f"?serviceKey={WEATHER_API_KEY}"
        f"&pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}"
        f"&nx={NX}&ny={NY}"
    )

    response = requests.get(url)
    data = response.json()

    print("API 응답 전체:", data)  # <- 이 줄 추가!

    if response.status_code != 200 or "response" not in data:
        print("날씨 API 오류:", data)
        return None, None

    if response.status_code != 200 or "response" not in data:
        raise Exception(f"날씨 API 오류: {data}")

    items = data['response']['body']['items']['item']
    temp = None
    weather_code = None

    for item in items:
        if item['category'] == 'T1H':  # 기온
            temp = item['fcstValue']
        if item['category'] == 'SKY':  # 하늘 상태 (1맑음, 3구름, 4흐림)
            weather_code = item['fcstValue']

    # SKY 코드 → 텍스트 변환
    weather_desc = {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(weather_code, "알수없음")
    return weather_desc, float(temp)

# 3. 노션에 데이터 추가
def add_weather_to_notion(weather_desc, temp):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    notion.pages.create(
        parent={"database_id": NOTION_DB_ID},
        properties={
            "날짜": {"title": [{"text": {"content": today}}]},
            "날씨": {"rich_text": [{"text": {"content": weather_desc}}]},
            "기온": {"number": temp}
        }
    )
    print(f"노션에 기록 완료: {today} - {weather_desc} ({temp}°C)")

if __name__ == "__main__":
    try:
        weather, temperature = get_weather()
        add_weather_to_notion(weather, temperature)
    except Exception as e:
        print("에러 발생:", e)
