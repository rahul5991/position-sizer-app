import streamlit as st
import yfinance as yf
import requests
import json
import streamlit as st
import os

def send_telegram_alert(symbol, current_price, target_price, condition):
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]
    message = f"📢 {symbol} is ₹{current_price:.2f} ({condition} ₹{target_price})"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

def check_alerts():
    with open("alerts.json", "r") as f:
        alerts = json.load(f)

    for alert in alerts:
        symbol = alert["symbol"]
        target = float(alert["target_price"])
        cond = alert["condition"]

        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")["Close"].iloc[-1]

            if (cond == "above" and price >= target) or (cond == "below" and price <= target):
                send_telegram_alert(symbol, price, target, cond)
                st.success(f"✅ Alert sent for {symbol}")
            else:
                st.info(f"ℹ️ {symbol} is ₹{price:.2f} — no alert triggered")

        except Exception as e:
            st.error(f"❌ Error for {symbol}: {e}")

# Add this to your Streamlit app
st.markdown("### 📬 Check & Send Telegram Alerts")
if st.button("Run Alert Check Now"):
    check_alerts()


st.title("📊 Position Sizing Calculator (NSE/BSE)")

# Session state defaults
default_values = {
    'entry_price': 1704.0,
    'capital': 700000.0,
    'risk_percent': 0.5,
    'stop_loss_percent': 4.5
}

for key, default in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Inputs
entry_price = st.number_input("Entry Price (₹)", min_value=1.0, step=1.0,
                              value=st.session_state.entry_price, key='entry_price')
capital = st.number_input("Total Capital (₹)", min_value=1.0, step=1000.0,
                          value=st.session_state.capital, key='capital')
risk_percent = st.number_input("Risk per Trade (%)", min_value=0.1, step=0.1,
                               value=st.session_state.risk_percent, key='risk_percent')
stop_loss_percent = st.number_input("Stop Loss (%)", min_value=0.1, step=0.1,
                                    value=st.session_state.stop_loss_percent, key='stop_loss_percent')

def calculate_position_size(entry_price, capital, risk_percent, stop_loss_percent):
    risk_amount = (risk_percent / 100) * capital
    stop_loss_per_share = (stop_loss_percent / 100) * entry_price
    position_size = int(risk_amount / stop_loss_per_share)
    total_position_value = position_size * entry_price
    estimated_loss = position_size * stop_loss_per_share
    stop_loss_level = entry_price - stop_loss_per_share

    return position_size, total_position_value, stop_loss_per_share, estimated_loss, stop_loss_level

# Run calc
if st.button("Calculate Position Size"):
    position_size, total_value, sl_per_share, est_loss, sl_level = calculate_position_size(
        entry_price, capital, risk_percent, stop_loss_percent
    )

    st.success(f"🧾 Position Size: **{position_size} shares**")
    st.write(f"💸 Total Trade Value: ₹{total_value:,.2f}")
    st.write(f"🔻 Stop Loss per Share: ₹{sl_per_share:.2f}")
    st.write(f"📉 **Stop Loss Price Level**: ₹{sl_level:.2f}")
    st.write(f"⚠️ Estimated Max Loss: ₹{est_loss:.2f}")

st.markdown("""
---
<center>
<a href="https://coff.ee/rahulkatiyar" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="45" width="162">
</a>
</center>
""", unsafe_allow_html=True)

