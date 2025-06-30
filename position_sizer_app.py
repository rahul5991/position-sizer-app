import streamlit as st

def calculate_position_size(entry_price, capital, risk_percent, stop_loss_percent):
    risk_amount = (risk_percent / 100) * capital
    stop_loss_per_share = (stop_loss_percent / 100) * entry_price
    position_size = int(risk_amount / stop_loss_per_share)
    total_position_value = position_size * entry_price
    estimated_loss = position_size * stop_loss_per_share

    return position_size, total_position_value, stop_loss_per_share, estimated_loss

# Streamlit UI
st.title("📊 Position Sizing Calculator (NSE/BSE)")

entry_price = st.number_input("Entry Price (₹)", min_value=1.0, step=1.0)
capital = st.number_input("Total Capital (₹)", min_value=1.0, step=1000.0)
risk_percent = st.number_input("Risk per Trade (%)", min_value=0.1, step=0.1)
stop_loss_percent = st.number_input("Stop Loss (%)", min_value=0.1, step=0.1)

if st.button("Calculate Position Size"):
    position_size, total_value, sl_per_share, est_loss = calculate_position_size(
        entry_price, capital, risk_percent, stop_loss_percent
    )

    st.success(f"🧾 Position Size: **{position_size} shares**")
    st.write(f"💸 Total Trade Value: ₹{total_value:,.2f}")
    st.write(f"🔻 Stop Loss per Share: ₹{sl_per_share:.2f}")
    st.write(f"⚠️ Estimated Max Loss: ₹{est_loss:.2f}")

st.markdown("---")
st.markdown("Made for NSE/BSE traders — adjust and calculate on the fly!")
