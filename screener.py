import requests
import pandas as pd

def get_stocks(market_code, market_name):
    print(f"📡 {market_name} 데이터 불러오는 중...")
    all_stocks = []
    
    for page in range(1, 50):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok={market_code}&page={page}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        res = requests.get(url, headers=headers)
        tables = pd.read_html(res.text)
        
        df = tables[1]
        df = df.dropna(how="all")
        df = df[df["N"].notna()]
        
        if len(df) == 0:
            break
            
        all_stocks.append(df)
        print(f"  {page}페이지 완료... ({len(df)}개)")
    
    result = pd.concat(all_stocks, ignore_index=True)
    result = result.drop(columns=["N", "토론실"], errors="ignore")
    result["시장"] = market_name
    return result

# KOSPI (sosok=0), KOSDAQ (sosok=1)
kospi = get_stocks(0, "KOSPI")
kosdaq = get_stocks(1, "KOSDAQ")

# 합치기
df = pd.concat([kospi, kosdaq], ignore_index=True)

print(f"\n✅ KOSPI {len(kospi)}개 + KOSDAQ {len(kosdaq)}개 = 총 {len(df)}개!")
print(df.head(5).to_string(index=False))

df.to_excel("전체종목.xlsx", index=False)
print("\n💾 전체종목.xlsx 저장 완료!")

# ==============================
# 여기서 조건 바꿔가며 사용하세요!
# ==============================

# 숫자 변환 (혹시 문자로 저장된 경우 대비)
df["PER"] = pd.to_numeric(df["PER"], errors="coerce")
df["ROE"] = pd.to_numeric(df["ROE"], errors="coerce")
df["시가총액"] = pd.to_numeric(df["시가총액"], errors="coerce")
df["외국인비율"] = pd.to_numeric(df["외국인비율"], errors="coerce")
df["등락률"] = df["등락률"].str.replace("%","").str.replace("+","").astype(float, errors="ignore")

# 필터링 조건 (원하는 대로 수정!)
filtered = df[
    (df["PER"] > 0) & (df["PER"] < 15) &       # PER 15 이하 (저평가)
    (df["ROE"] > 10) &                           # ROE 10% 이상 (수익성 좋음)
    (df["시가총액"] > 1000)                       # 시총 1000억 이상 (안정성)
]

print(f"\n✅ 조건에 맞는 종목: {len(filtered)}개")
print(filtered[["종목명", "시장", "현재가", "PER", "ROE", "시가총액"]].to_string(index=False))

filtered.to_excel("필터결과.xlsx", index=False)
print("\n💾 필터결과.xlsx 저장 완료!")