from flask import Flask, render_template, request
import requests
import pandas as pd

app = Flask(__name__)

def get_stocks():
    all_stocks = []
    for sosok, market in [("0", "KOSPI"), ("1", "KOSDAQ")]:
        for page in range(1, 50):
            url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            tables = pd.read_html(res.text)
            df = tables[1]
            df = df.dropna(how="all")
            df = df[df["N"].notna()]
            if len(df) == 0:
                break
            df["시장"] = market
            all_stocks.append(df)
    result = pd.concat(all_stocks, ignore_index=True)
    result = result.drop(columns=["N", "토론실"], errors="ignore")
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    count = 0

    if request.method == "POST":
        per_max = float(request.form.get("per_max") or 9999)
        per_min = float(request.form.get("per_min") or 0)
        roe_min = float(request.form.get("roe_min") or 0)
        cap_min = float(request.form.get("cap_min") or 0)

        df = get_stocks()
        df["PER"] = pd.to_numeric(df["PER"], errors="coerce")
        df["ROE"] = pd.to_numeric(df["ROE"], errors="coerce")
        df["시가총액"] = pd.to_numeric(df["시가총액"], errors="coerce")

        filtered = df[
            (df["PER"] >= per_min) &
            (df["PER"] <= per_max) &
            (df["ROE"] >= roe_min) &
            (df["시가총액"] >= cap_min)
        ]

        count = len(filtered)
        results = filtered[["종목명", "시장", "현재가", "PER", "ROE", "시가총액", "외국인비율"]].to_dict("records")

    return render_template("index.html", results=results, count=count)

if __name__ == "__main__":
    app.run(debug=True)