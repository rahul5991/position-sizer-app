import streamlit as st
from nsetools import Nse
from growwapi import GrowwAPI

# --- Initialize ---
st.title("📊 Position Sizing Calculator + Margin (Cash / Futures)")

# Load NSE F&O lot sizes once
nse = Nse()
fno_lots = nse.get_fno_lot_sizes()

# Initialize Groww API
API_TOKEN = st.secrets.get("GROWW_API_TOKEN", "")
groww = GrowwAPI(API_TOKEN)

# Default session values
default_values = {
    'entry_price': 1704.0,
    'capital': 700000.0,
    'risk_percent': 0.5,
    'stop_loss_percent': 4.5,
    'mode': 'Cash',
    'symbol': '',
    'lot_size': 1
}
for k, v in default_values.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Reset
if st.button("🔄 Reset All"):
    for k, v in default_values.items():
        st.session_state[k] = v
    st.experimental_rerun()

# --- User inputs ---
mode = st.selectbox("Select Mode", ["Cash", "Futures"], key='mode')
entry_price = st.number_input("Entry Price (₹)", value=st.session_state.entry_price, key='entry_price')
capital = st.number_input("Total Capital (₹)", value=st.session_state.capital, key='capital')
risk_percent = st.number_input("Risk per Trade (%)", value=st.session_state.risk_percent, key='risk_percent')
stop_loss_percent = st.number_input("Stop Loss (%)", value=st.session_state.stop_loss_percent, key='stop_loss_percent')

symbol = ""
lot_size = 1
if mode == "Futures":
    symbol = st.text_input("F&O Symbol (e.g. NIFTY, RELIANCE)", value=st.session_state.symbol, key='symbol').upper().strip()
    valid = nse.is_valid_code(symbol) or nse.is_valid_index(symbol)
    if valid:
        auto = fno_lots.get(symbol)
        if auto:
            st.success(f"Detected lot size for **{symbol}**: {auto}")
            lot_size = auto
        else:
            st.warning(f"No lot-size found for '{symbol}'. Please input manually.")
            lot_size = st.number_input("Lot Size (manual)", min_value=1, value=st.session_state.lot_size, key='lot_size')
    else:
        st.error(f"Symbol '{symbol}' not recognized on NSE.")
        lot_size = st.number_input("Lot Size (manual)", min_value=1, value=st.session_state.lot_size, key='lot_size')

# --- Computation ---
def calculate_position_size(entry, capital, risk_pct, sl_pct, mode, lot):
    risk_amt = capital * risk_pct / 100
    sl_per = entry * sl_pct / 100

    if mode == "Futures":
        pos = int(risk_amt // sl_per // lot) * lot
    else:
        pos = int(risk_amt // sl_per)

    total_val = pos * entry
    est_loss = pos * sl_per
    sl_level = entry - sl_per
    return pos, total_val, sl_per, est_loss, sl_level, risk_amt

# --- On Calculate ---
if st.button("Calculate Position Size & Margin"):
    if mode == "Futures" and (not symbol or not (nse.is_valid_code(symbol) or nse.is_valid_index(symbol))):
        st.error("⚠️ Please enter a valid F&O symbol to proceed.")
    else:
        pos, total_val, sl_per, est_loss, sl_level, risk_amt = calculate_position_size(
            entry_price, capital, risk_percent, stop_loss_percent, mode, lot_size
        )
        st.success(f"🧾 Position Size: **{pos} units/shares**")
        st.write(f"💸 Trade Value: ₹{total_val:,.2f}")
        st.write(f"🔻 SL per unit: ₹{sl_per:.2f}")
        st.write(f"📉 SL Price Level: ₹{sl_level:.2f}")
        st.write(f"🎯 Risk Amount: ₹{risk_amt:.2f} ({risk_percent}%)")
        st.write(f"⚠️ Estimated Max Loss: ₹{est_loss:,.2f}")

        # 🔍 Margin via Groww
        if mode == "Futures":
            st.write("---")
            try:
                order_req = { 
                    "trading_symbol": symbol,
                    "transaction_type": groww.TRANSACTION_TYPE_BUY,
                    "quantity": pos,
                    "price": entry_price,
                    "order_type": groww.ORDER_TYPE_LIMIT,
                    "product": groww.PRODUCT_MIS,
                    "exchange": groww.EXCHANGE_NSE
                }
                margin_resp = groww.get_order_margin_details(segment=groww.SEGMENT_FNO, orders=[order_req])
                st.write("💰 **Margin Breakdown:**")
                st.write(f"- SPAN required: ₹{margin_resp['span_required']}")
                st.write(f"- Exposure required: ₹{margin_resp['exposure_required']}")
                st.write(f"- Brokerage & charges: ₹{margin_resp['brokerage_and_charges']}")
                st.write(f"- Total Margin required: ₹{margin_resp['total_requirement']}")
            except Exception as e:
                st.error(f"Error fetching margin: {e}")

        else:
            # Cash: show available margin
            avail = groww.get_available_margin_details()
            st.write("---")
            st.write("💼 **Account Margin (Cash):**")
            st.write(f"- Clear Cash: ₹{avail['clear_cash']}")
            st.write(f"- Net Margin Used: ₹{avail['net_margin_used']}")
            st.write(f"- F&O Margin Used: ₹{avail['fno_margin_details']['net_fno_margin_used']}")        
