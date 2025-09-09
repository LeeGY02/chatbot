# sheet.py
import os, json
import gspread
from google.oauth2.service_account import Credentials

# 열 인덱스
COL = {"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"H":8,"K":11,"N":14}

_gc = None  # 전역 클라이언트 (지연 초기화)
def _client():
    """환경변수 검사와 인증을 '사용 시점'에 수행"""
    global _gc
    if _gc is not None:
        return _gc

    SHEET_ID = os.getenv("SHEET_ID", "")
    CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON", "")
    if not SHEET_ID:
        raise RuntimeError("SHEET_ID not set")
    if not CREDS_JSON:
        raise RuntimeError("GOOGLE_CREDS_JSON not set")

    creds = Credentials.from_service_account_info(json.loads(CREDS_JSON),
                                                  scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    _gc = gspread.authorize(creds)
    return _gc

def _worksheet():
    SHEET_ID = os.getenv("SHEET_ID", "")
    SHEET_TITLE = os.getenv("SHEET_TITLE", "가림 2-4 정보")
    gc = _client()
    sh = gc.open_by_key(SHEET_ID)
    if SHEET_TITLE:
        try:
            return sh.worksheet(SHEET_TITLE)
        except gspread.WorksheetNotFound:
            pass
    return sh.get_worksheet(0)

def fetch_all():
    ws = _worksheet()
    values = ws.get_all_values()

    timetable, assessments, exam_scope, notices = [], [], [], []

    # 2행부터 훑기 (1행=헤더)
    for i, row in enumerate(values, start=1):
        if i == 1:
            continue

        def cell(cidx):
            return row[cidx-1] if cidx-1 < len(row) else ""

        a = cell(COL["A"])
        if a and a.endswith("교시"):
            timetable.append({
                "period": a,
                "Mon": cell(COL["B"]),
                "Tue": cell(COL["C"]),
                "Wed": cell(COL["D"]),
                "Thu": cell(COL["E"]),
                "Fri": cell(COL["F"]),
            })

        h = cell(COL["H"]).strip()
        k = cell(COL["K"]).strip()
        n = cell(COL["N"]).strip()
        if h: assessments.append(h)
        if k: exam_scope.append(k)
        if n: notices.append(n)

    return {
        "timetable": timetable,
        "assessments": assessments,
        "examScope": exam_scope,
        "notices": notices
    }

def fetch_day(day_kor: str):
    """요일별(월~금) 3~9행만"""
    ws = _worksheet()
    values = ws.get_all_values()
    day_to_col = {"월": COL["B"], "화": COL["C"], "수": COL["D"], "목": COL["E"], "금": COL["F"]}
    col = day_to_col.get(day_kor)
    if not col:
        return []

    out = []
    for r in range(3, 10):  # 3~9행
        if r-1 >= len(values): break
        row = values[r-1]
        period  = row[COL["A"]-1] if COL["A"]-1 < len(row) else ""
        subject = row[col-1]      if col-1      < len(row) else ""
        if period and period.endswith("교시"):
            out.append({"period": period, "subject": subject})
    return out
