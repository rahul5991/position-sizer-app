import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from io import StringIO

st.set_page_config("📊 NSE Position Sizer", layout="centered")
st.title("📊 NSE Position Sizer (Cash & Futures)")

# -- Custom CSV Fetch with Headers --
@st.cache_data(ttl=3600)
def fetch_lot_sizes():
    url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df.set_index("SYMBOL")["MULTIPLE"].to_dict()
    else:
        raise Exception("⚠️ Could not fetch lot sizes from NSE.")

try:
    lot_sizes = fetch_lot_sizes()
    symbols = sorted(lot_sizes.keys())

    # -- UI --
    mode = st.selectbox("Mode", ["Cash", "Futures"])
    symbol = st.selectbox("Select Symbol", symbols)

    # -- Live Price --
    suffix = ".NS" if mode == "Cash" else "-F.NS"
    ticker = yf.Ticker(symbol + suffix)
    data = ticker.history(period="1d")

    if data.empty:
        st.error("❌ Could not fetch live price.")
        st.stop()

    ltp = data["Close"].iloc[-1]
    st.success(f"📈 Live Price for {symbol}: ₹{ltp:.2f}")

    # -- Inputs --
    capital = st.number_input("💰 Capital (₹)", value=500000.0, step=10000.0)
    risk_pct = st.number_input("🎯 Risk per Trade (%)", value=1.0, step=0.1)
    sl_pct = st.number_input("🔻 Stop Loss (%)", value=2.0, step=0.1)

    # -- Lot Size --
    lot_size = 1
    if mode == "Futures":
        lot_size = lot_sizes.get(symbol, 1)
        st.info(f"📦 Lot size for {symbol}: {lot_size}")

    # -- Position Size --
    risk_amt = capital * risk_pct / 100
    sl_per_unit = ltp * sl_pct / 100

    if mode == "Futures":
        lots = int(risk_amt // (sl_per_unit * lot_size))
        qty = lots * lot_size
    else:
        qty = int(risk_amt // sl_per_unit)

    # -- Results --
    if qty <= 0:
        st.error("⚠️ Risk/capital too low for trade.")
    else:
        st.write(f"🧾 **Position Size**: {qty} {'units' if mode=='Cash' else 'futures units'}")
        st.write(f"🔻 SL Price: ₹{ltp - sl_per_unit:.2f}")
        st.write(f"⚠️ Estimated Max Loss: ₹{qty * sl_per_unit:.2f}")
        if mode == "Futures":
            st.write(f"📦 No. of Lots: {lots}")

except Exception as e:
    st.error(f"❌ {e}")
