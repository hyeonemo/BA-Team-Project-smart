"""연령대별 검색 패턴 확인 (갤럭시북 신학기 가설 검증용, 수동 실행 전용).
가설: 갤럭시북은 연초(2~3월)·2학기(8~9월)에 대학생(19~24세) 수요로 검색이 오른다.
방법: 같은 키워드를 연령대별로 따로 받아, 신학기 달(2·3·8·9월)의 평균이 나머지 달 평균의 몇 배인지(신학기 지수) 비교한다.
 - 갤럭시북: 19~24세 지수가 다른 연령대보다 확실히 높으면 가설 지지
 - 대조군(갤럭시 Z플립·갤럭시 버즈): 언팩·출시 영향이 커서 19~24세 지수가 높지 않아야 한다
주의: 데이터랩은 요청마다 최대값=100으로 맞추므로 '같은 요청 안의 기간끼리' 비교하는 지수만 쓴다(연령대 간 절대 수준 비교 금지).
"""
import os, sys, json, time, urllib.request, urllib.error, datetime as dt
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))
KW = ["갤럭시북", "대학생 노트북", "노트북", "갤럭시 Z플립", "갤럭시 버즈"]   # 앞 3개: 가설 대상, 뒤 2개: 대조군
AGES = {"전체": None, "19~24세": ["3"], "25~34세": ["4", "5"], "35~49세": ["6", "7", "8"], "50세 이상": ["9", "10", "11"]}
SEMESTER = [2, 3, 8, 9]

def call(body):
    cid, sec = os.environ["NAVER_CLIENT_ID"], os.environ["NAVER_CLIENT_SECRET"]
    req = urllib.request.Request(CFG["api_base"] + "/search-trend/v1/search", data=json.dumps(body).encode(), method="POST",
        headers={"X-NCP-APIGW-API-KEY-ID": cid, "X-NCP-APIGW-API-KEY": sec, "Content-Type": "application/json"})
    last = None
    for i in range(6):
        try:
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code} {e.read().decode()[:200]}"
            server_side = '"errorCode":5' in last.replace(" ", "")
            if e.code < 500 and e.code != 429 and not server_side: break
        except Exception as e:
            last = repr(e)
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"데이터랩 호출 실패: {last}")

def fetch(kw, ages, end):
    body = {"startDate": CFG["start_date"], "endDate": end, "timeUnit": "date", "keywordGroups": [{"groupName": kw, "keywords": [kw]}]}
    if ages: body["ages"] = ages
    r = call(body)
    s = pd.Series({p["period"]: p["ratio"] for p in r["results"][0]["data"]}); s.index = pd.to_datetime(s.index)
    return s.sort_index()

def main():
    end = (dt.date.today() - dt.timedelta(days=1)).isoformat()
    data = {}
    for kw in KW:
        for g, ages in AGES.items():
            data[(kw, g)] = fetch(kw, ages, end); time.sleep(0.3)
    df = pd.DataFrame(data); df.index.name = "date"
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    df.to_csv(os.path.join(ROOT, "data", "age_probe.csv"))
    rows = []
    for (kw, g), s in df.items():
        m = s.index.month.isin(SEMESTER)
        rows.append({"키워드": kw, "연령대": g, "신학기 지수": round(s[m].mean() / s[~m].mean(), 2) if s[~m].mean() else None})
    idx = pd.DataFrame(rows).pivot(index="키워드", columns="연령대", values="신학기 지수")[list(AGES)].loc[KW]
    mon = {}
    for kw in KW[:1]:
        for g in ["19~24세", "35~49세"]:
            s = df[(kw, g)]; mon[f"{kw} {g}"] = (s.groupby(s.index.month).mean() / s.mean()).round(2)
    monthly = pd.DataFrame(mon); monthly.index.name = "월"
    out = ["[신학기 지수] 신학기 달(2·3·8·9월) 평균 ÷ 나머지 달 평균 (1.0이면 계절 차이 없음)", idx.to_string(), "",
           "[월별 상대 수준] 월 평균 ÷ 전체 평균 (갤럭시북)", monthly.to_string(), "",
           "[해석 기준] 갤럭시북 19~24세 지수가 다른 연령대보다 뚜렷이 높고 대조군(Z플립·버즈)에서는 그렇지 않으면 '신학기 학생 수요' 가설 지지."]
    txt = "\n".join(out); print(txt)
    open(os.path.join(ROOT, "data", "age_probe_summary.txt"), "w", encoding="utf-8").write(txt)

if __name__ == "__main__":
    main()
