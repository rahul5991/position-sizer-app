import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config("📊 NSE Position Sizer", layout="centered")
st.title("📊 NSE Position Sizer (Cash & Futures)")

# -- Fetch NSE F&O lot sizes (live CSV) --
@st.cache_data(ttl=3600)
def fetch_lot_sizes():
    url = "https://archives.nseindia.com/content/fo/fo_mktlots.csv"
    df = pd.read_csv(url)
    return df.set_index("SYMBOL")["MULTIPLE"].to_dict()

lot_sizes = fetch_lot_sizes()
symbols = sorted(lot_sizes.keys())

# -- Mode & Symbol selection --
mode = st.selectbox("Mode", ["Cash", "Futures"])
symbol = st.selectbox("Select Symbol", symbols)

# -- Live Price Fetch --
suffix = ".NS" if mode == "Cash" else "-F.NS"
ticker = yf.Ticker(symbol + suffix)
data = ticker.history(period="1d")

if data.empty:
    st.error("❌ Could not fetch price; check symbol or network.")
    st.stop()

ltp = data["Close"].iloc[-1]
st.success(f"📈 Live Price for {symbol}: ₹{ltp:.2f}")

# -- Input Parameters --
capital = st.number_input("💰 Capital (₹)", value=500000.0, step=10000.0)
risk_pct = st.number_input("🎯 Risk per Trade (%)", value=1.0, step=0.1)
sl_pct = st.number_input("🔻 Stop Loss (%)", value=2.0, step=0.1)

# -- Lot Size (Futures only) --
lot_size = 1
if mode == "Futures":
    lot_size = lot_sizes.get(symbol, 1)
    st.info(f"📦 Futures lot size for {symbol}: {lot_size}")

# -- Position Size Calculation --
risk_amt = (risk_pct / 100) * capital
sl_per_unit = (sl_pct / 100) * ltp

if mode == "Futures":
    lots = int(risk_amt // (sl_per_unit * lot_size))
    qty = lots * lot_size
else:
    qty = int(risk_amt // sl_per_unit)

# -- Results --
if qty <= 0:
    st.error("⚠️ Not enough capital or stop loss too small.")
else:
    st.write(f"🧾 Position Size: **{qty} {'units' if mode=='Cash' else 'futures units'}**")
    st.write(f"⚠️ Max Risk: ₹{qty * sl_per_unit:.2f}")
    st.write(f"🔻 SL Price Level: ₹{ltp - sl_per_unit:.2f}")
    if mode == "Futures":
        st.write(f"📦 Number of Lots: {lots}")

st.caption("Lot sizes sourced from NSE CSV :contentReference[oaicite:6]{index=6} · Prices from Yahoo Finance")
