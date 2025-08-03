import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from notion_client import Client

# 환경변수 로드 (env.txt 경로에 맞게 수정)
load_dotenv("env.txt")

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_DB_ID")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NX = os.getenv("NX")
NY = os.getenv("NY")

notion = Client(auth=NOTION_TOKEN)

def get_base_time_ultrasrt():
    # 초단기 관측용 base_time (10분 전 시점, 10분 단위 절삭)
    now = datetime.now(ZoneInfo("Asia/Seoul")) - timedelta(minutes=10)
    minute = (now.minute // 10) * 10
    base_date = now.strftime("%Y%m%d")
    base_time = f"{now.hour:02d}{minute:02d}"
    return base_date, base_time

def get_base_time_short_term():
    # 단기예보 갱신 시각: 02, 05, 08, 11, 14, 17, 20, 23시 기준
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    base_hours = [2, 5, 8, 11, 14, 17, 20, 23]
    candidates = [h for h in base_hours if h <= now.hour]
    if candidates:
        base_hour = max(candidates)
    else:
        # 0~1시인 경우 전날 23시로 처리
        base_hour = 23
        now = now - timedelta(days=1)
    base_date = now.strftime("%Y%m%d")
    base_time = f"{base_hour:02d}00"
    return base_date, base_time

def get_ultrasrt_weather():
    base_date, base_time = get_base_time_ultrasrt()
    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?serviceKey={WEATHER_API_KEY}"
        f"&pageNo=1&numOfRows=100"
        f"&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}"
        f"&nx={NX}&ny={NY}"
    )
    response = requests.get(url)
    data = response.json()
    print("초단기 관측 API 응답:", data)

    if response.status_code != 200 or "response" not in data:
        raise Exception(f"초단기 관측 API 오류: {data}")

    header = data['response']['header']
    if header['resultCode'] != '00':
        raise Exception(f"초단기 관측 API 오류: {header['resultMsg']}")

    items = data['response']['body']['items']['item']

    weather_data = {
        "기온": None,
        "습도": None,
        "1시간 강수량": None,
        "풍속": None,
        "풍향": None,
        "강수형태": None,
    }

    for item in items:
        cat = item['category']
        val = item['obsrValue']
        if cat == 'T1H':
            weather_data["기온"] = float(val)
        elif cat == 'REH':
            weather_data["습도"] = float(val)
        elif cat == 'RN1':
            weather_data["1시간 강수량"] = float(val)
        elif cat == 'WSD':
            weather_data["풍속"] = float(val)
        elif cat == 'VEC':
            weather_data["풍향"] = float(val)
        elif cat == 'PTY':
            weather_data["강수형태"] = val

    return weather_data

def get_short_term_sky():
    base_date, base_time = get_base_time_short_term()
    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        f"?serviceKey={WEATHER_API_KEY}"
        f"&pageNo=1&numOfRows=1000"
        f"&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}"
        f"&nx={NX}&ny={NY}"
    )
    response = requests.get(url)
    data = response.json()
    print("단기예보 API 응답:", data)

    if response.status_code != 200 or "response" not in data:
        raise Exception(f"단기예보 API 오류: {data}")

    header = data['response']['header']
    if header['resultCode'] != '00':
        raise Exception(f"단기예보 API 오류: {header['resultMsg']}")

    items = data['response']['body']['items']['item']

    # 현재 시각(분 단위 절삭)
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    base_time_min = (now.minute // 30) * 30
    now_str = now.strftime(f"%Y%m%d%H") + f"{base_time_min:02d}"

    sky_code = None

    # 단기예보 SKY 코드 찾기 (오늘 시각 이후의 데이터 중 가장 가까운 시각)
    for item in items:
        if item['category'] == 'SKY' and item['fcstDate'] + item['fcstTime'] >= now_str:
            sky_code = item['fcstValue']
            break

    # SKY 코드 한글 설명
    sky_dict = {
        "1": "맑음",
        "2": "-",
        "3": "구름 많음",
        "4": "흐림"
    }
    sky_desc = sky_dict.get(sky_code, "알수없음")
    return sky_desc

def add_weather_to_notion(weather_data):
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))
    now_str = now_kst.strftime("%Y-%m-%dT%H:%M:%S%z")  # ISO8601 + 타임존

    # 강수형태 코드 → 설명
    pty_dict = {
        "0": "맑음",
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "4": "소나기",
        "5": "빗방울",
        "6": "빗방울/눈날림",
        "7": "눈날림"
    }

    pty_desc = pty_dict.get(weather_data.get("강수형태", "0"), "없음")

    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "날짜": {"date": {"start": now_str}},
            "날씨": {"multi_select": [{"name": pty_desc}]},
            "하늘 상태": {"multi_select": [{"name": weather_data["하늘 상태"]}]},
            "기온": {"number": weather_data["기온"]},
            "습도": {"number": weather_data["습도"]},
            "1시간 강수량": {"number": weather_data["1시간 강수량"]},
            "풍속": {"number": weather_data["풍속"]},
            "풍향": {"number": weather_data["풍향"]},
        }
    }

    print("노션에 보낼 payload:", payload)
    notion.pages.create(**payload)
    print(f"노션 기록 완료: {now_str} - {payload['properties']}")

if __name__ == "__main__":
    try:
        ultrasrt_data = get_ultrasrt_weather()
        sky_desc = get_short_term_sky()
        ultrasrt_data["하늘 상태"] = sky_desc
        add_weather_to_notion(ultrasrt_data)
    except Exception as e:
        print("에러 발생:", e)
