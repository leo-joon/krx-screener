def get_stocks():
    all_stocks = []
    for sosok, market in [("0", "KOSPI"), ("1", "KOSDAQ")]:
        for page in range(1, 20):  # 50 → 20으로 줄임
            try:
                url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={sosok}&page={page}"
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=headers, timeout=10)
                tables = pd.read_html(StringIO(res.text))
                df = tables[1]
                df = df.dropna(how="all")
                df = df[df["N"].notna()]
                if len(df) == 0:
                    break
                df["시장"] = market
                all_stocks.append(df)
            except:
                break
    result = pd.concat(all_stocks, ignore_index=True)
    result = result.drop(columns=["N", "토론실"], errors="ignore")
    return result