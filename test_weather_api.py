# test_weather_api.py
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. env.txt 로드
load_dotenv("env.txt")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NX = os.getenv("NX")
NY = os.getenv("NY")

def get_weather():
    now = datetime.now()
    if now.minute < 45:
        now -= timedelta(hours=1)
    
    base_date = now.strftime("%Y%m%d")
    base_time = now.strftime("%H00")

    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        f"?serviceKey={WEATHER_API_KEY}"
        f"&pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}"
        f"&nx={NX}&ny={NY}"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code != 200 or "response" not in data:
        print("날씨 API 오류:", data)
        return None, None

    items = data['response']['body']['items']['item']
    temp = None
    weather_code = None

    for item in items:
        if item['category'] == 'T1H':
            temp = item['fcstValue']
        if item['category'] == 'SKY':
            weather_code = item['fcstValue']

    weather_desc = {"1": "맑음", "3": "구름많음", "4": "흐림"}.get(weather_code, "알수없음")
    return weather_desc, temp

if __name__ == "__main__":
    weather, temp = get_weather()
    if weather and temp:
        print(f"현재 날씨: {weather}, 기온: {temp}°C")
    else:
        print("날씨 데이터를 가져오지 못했습니다.")
