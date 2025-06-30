import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from io import StringIO

st.set_page_config("📊 NSE Position Sizer", layout="centered")
st.title("📊 NSE Position Sizer (Cash & Futures)")

# -- Fetch lot sizes from NSE with correct parsing --
@st.cache_data(ttl=3600)
def fetch_lot_sizes():
    url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        csv_raw = StringIO(response.content.decode("ISO-8859-1"))
        df = pd.read_csv(csv_raw)
        df = df[["SYMBOL", "MARKET LOT"]]  # Ensure columns exist
        return df.set_index("SYMBOL")["MARKET LOT"].to_dict()
    else:
        raise Exception("⚠️ Could not fetch lot sizes from NSE.")

try:
    lot_sizes = fetch_lot_sizes()
    symbols = sorted(lot_sizes.keys())

    mode = st.selectbox("Mode", ["Cash", "Futures"])
    symbol = st.selectbox("Select Symbol", symbols)

    # Live price fetch
    suffix = ".NS" if mode == "Cash" else "-F.NS"
    ticker = yf.Ticker(symbol + suffix)
    data = ticker.history(period="1d")

    if data.empty:
        st.error("❌ Could not fetch price.")
        st.stop()

    ltp = data["Close"].iloc[-1]
    st.success(f"📈 Live Price for {symbol}: ₹{ltp:.2f}")

    # User inputs
    capital = st.number_input("💰 Capital (₹)", value=500000.0, step=10000.0)
    risk_pct = st.number_input("🎯 Risk per Trade (%)", value=1.0, step=0.1)
    sl_pct = st.number_input("🔻 Stop Loss (%)", value=2.0, step=0.1)

    lot_size = 1
    if mode == "Futures":
        lot_size = lot_sizes.get(symbol, 1)
        st.info(f"📦 Lot size for {symbol}: {lot_size}")

    risk_amt = capital * risk_pct / 100
    sl_per_unit = ltp * sl_pct / 100

    if mode == "Futures":
        lots = int(risk_amt // (sl_per_unit * lot_size))
        qty = lots * lot_size
    else:
        qty = int(risk_amt // sl_per_unit)

    if qty <= 0:
        st.error("⚠️ Risk too small for trade.")
    else:
        st.write(f"🧾 **Position Size**: {qty} {'units' if mode == 'Cash' else 'futures units'}")
        st.write(f"⚠️ Estimated Max Loss: ₹{qty * sl_per_unit:.2f}")
        st.write(f"🔻 Stop Loss Price: ₹{ltp - sl_per_unit:.2f}")
        if mode == "Futures":
            st.write(f"📦 Lots: {lots}")

except Exception as e:
    st.error(f"❌ Error: {e}")
