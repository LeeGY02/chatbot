# app.py
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# .env 로드 (SHEET_ID, SHEET_TITLE, GOOGLE_CREDS_JSON)
load_dotenv()

from sheet import fetch_all, fetch_day
from kakao import (
    simple_text,
    to_timetable_text,
    to_day_text,
    list_to_text,
    day_quick_replies,
)

app = Flask(__name__)

def extract_intent(body: dict) -> str:
    """
    카카오 오픈빌더가 보내는 케이스 모두 지원:
    - 블록 '스킬 파라미터' → action.params.intent
    - 버튼 라벨/사용자 발화 → userRequest.utterance
    - 수동 테스트 바디 → body.intent
    """
    try:
        return (
            body.get("action", {}).get("params", {}).get("intent")
            or body.get("userRequest", {}).get("utterance")
            or body.get("intent")
            or ""
        ).strip()
    except Exception:
        return ""

def is_day(s: str) -> bool:
    return s in ("월","화","수","목","금") or any(d + "요일" in s for d in ("월","화","수","목","금"))

def norm_day(s: str) -> str:
    for d in ("월","화","수","목","금"):
        if s == d or (d + "요일") in s:
            return d
    return ""

@app.get("/")
def health():
    return "OK"

@app.route("/skill", methods=["POST", "GET"])
def skill():
    try:
        # 1) 요청 파싱
        body = request.get_json(silent=True) or {}
        # 디버그 로그 (오픈빌더 테스트 시 콘솔에서 확인)
        try:
            print("[KAKAO REQ] headers=", dict(request.headers))
            print("[KAKAO REQ] body=", body)
        except Exception:
            pass

        # 2) intent 추출
        intent = extract_intent(body)
        print("[KAKAO REQ] intent=", intent)

        # 3) 요일(월~금) 처리: 해당 요일 3~9행
        if is_day(intent):
            d = norm_day(intent)
            items = fetch_day(d)
            return jsonify(simple_text(to_day_text(d, items), day_quick_replies())), 200

        # 4) 전체 데이터 로드
        data = fetch_all()

        if "시간표" in intent:
            return jsonify(simple_text(to_timetable_text(data["timetable"]), day_quick_replies())), 200
        if "수행" in intent:
            return jsonify(simple_text(list_to_text("📝 수행평가", data["assessments"]))), 200
        if "시험" in intent:
            return jsonify(simple_text(list_to_text("📖 시험범위", data["examScope"]))), 200
        if "공지" in intent:
            return jsonify(simple_text(list_to_text("📢 기타 공지", data["notices"]))), 200

        # 5) 기본 가이드
        text = (
            "메뉴를 선택해줘! (시간표/수행평가/시험범위/공지)\n"
            "또는 요일(월~금)을 보내면 해당 요일 시간표(3~9행)를 보여줄게."
        )
        return jsonify(simple_text(text, day_quick_replies())), 200

    except Exception as e:
        # 어떤 예외든 카카오 포맷으로 200 반환 (오픈빌더는 200을 기대)
        print("[ERROR]", e)
        return jsonify(simple_text(f"오류가 발생했어.\n{e}")), 200

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

    
@app.get("/ping")
def ping():
    return jsonify({"version":"2.0","template":{"outputs":[{"simpleText":{"text":"pong"}}]}}), 200

