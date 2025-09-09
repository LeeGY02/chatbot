def simple_text(text: str, quick_replies=None) -> dict:
    qrs = quick_replies or []
    base = [{"label": "메인으로", "action": "block", "blockId": "BLOCK_MAIN"}]
    return {
        "version": "2.0",
        "template": {
            "outputs": [{"simpleText": {"text": text}}],
            "quickReplies": qrs + base
        }
    }

def day_quick_replies():
    return [
        {"label": "월", "action": "message", "messageText": "월"},
        {"label": "화", "action": "message", "messageText": "화"},
        {"label": "수", "action": "message", "messageText": "수"},
        {"label": "목", "action": "message", "messageText": "목"},
        {"label": "금", "action": "message", "messageText": "금"},
    ]

def to_timetable_text(tt_rows):
    if not tt_rows:
        return "시간표가 없어요."
    z = lambda v: (v or "").strip() or "-"
    lines = ["📅 이번 주 시간표"]
    for r in tt_rows:  # dict: period, Mon..Fri
        lines.append(
            f'{r["period"]}  월:{z(r["Mon"])}  화:{z(r["Tue"])}  수:{z(r["Wed"])}  목:{z(r["Thu"])}  금:{z(r["Fri"])}'
        )
    return "\n".join(lines)

def to_day_text(day_kor: str, items):
    if not items:
        return f"{day_kor}요일 시간표가 없어요."
    z = lambda v: (v or "").strip() or "-"
    lines = [f"📅 {day_kor}요일 시간표 (3~9행)"]
    for it in items:  # dict: period, subject
        lines.append(f'{it["period"]} {z(it["subject"])}')
    return "\n".join(lines)

def list_to_text(title: str, arr):
    if not arr:
        return f"등록된 {title}가 없어요."
    return f"{title}\n- " + "\n- ".join(arr)
