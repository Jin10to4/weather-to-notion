from flask import Flask, request
import subprocess
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return "서버 실행 중"

@app.route("/run", methods=["POST"])
def run_script():
    print("📩 단축어에서 POST 요청 받음!")

    try:
        result = subprocess.run(
            ["python3", "weather_to_notion_ultrasrt.py"],
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
        print("Return code:", e.returncode)
        print("Output:", e.output)
        print("Error output:", e.stderr)
        return f"스크립트 실행 실패: {e.stderr}", 500

    except Exception as e:
        print("❌ 일반 예외 발생")
        traceback.print_exc()
        return f"서버 에러: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
