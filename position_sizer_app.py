import streamlit as st

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

st.caption("Settings are saved per session. Refreshing resets them.")

st.markdown("""
---
<center>
<a href="https://coff.ee/rahulkatiyar" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="45" width="162">
</a>
</center>
""", unsafe_allow_html=True)

