from flask import Flask, request
import subprocess
import traceback
from latlon_to_xy import dfs_xy_conv  # 🧭 추가

app = Flask(__name__)

@app.route("/")
def home():
    return "서버 실행 중"

@app.route("/run", methods=["GET"])
def run_script():
    print("📩 위치 기반 요청 받음!")

    try:
        # 위치값 받기
        lat = request.args.get("lat")
        lon = request.args.get("lon")

        print("📍 받은 위치 좌표:")
        print("Latitude:", lat)
        print("Longitude:", lon)

        if lat and lon:
            coords = dfs_xy_conv(float(lat), float(lon))
            nx = str(coords["x"])
            ny = str(coords["y"])
        else:
            nx = "64"
            ny = "91"

        print(f"🧭 변환된 좌표: nx={nx}, ny={ny}")

        # 파라미터를 넘기며 실행
        result = subprocess.run(
            ["python3", "weather_to_notion_ultrasrt.py", nx, ny],
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ 스크립트 실행 완료")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        return result.stdout or "실행 완료"

    except subprocess.CalledProcessError as e:
        print("❌ CalledProcessError 발생")
        return f"스크립트 실행 실패: {e.stderr}", 500

    except Exception as e:
        print("❌ 일반 예외 발생")
        traceback.print_exc()
        return f"서버 에러: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
