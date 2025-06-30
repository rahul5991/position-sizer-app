import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect

# --- Config ---
st.set_page_config(page_title="Futures Position Sizer + Margin", layout="centered")
st.title("📈 Futures Position Sizer + Margin Estimator (Zerodha Kite)")

# --- Kite Credentials ---
api_key = st.secrets["KITE_API_KEY"]
api_secret = st.secrets["KITE_API_SECRET"]
kite = KiteConnect(api_key=api_key)
login_url = kite.login_url()

# --- Request Token Input ---
st.markdown(f"🔐 [Login to Kite Connect]({login_url})")
request_token = st.text_input("Paste `request_token` from redirected URL after login:")

if request_token:
    try:
        session_data = kite.generate_session(request_token, api_secret=api_secret)
        kite.set_access_token(session_data["access_token"])
        st.success("✅ Logged in to Zerodha!")

        # --- Load NSE Futures Instruments ---
        @st.cache_data
        def load_fno():
            df = pd.DataFrame(kite.instruments("NFO"))
            return df[df["instrument_type"] == "FUT"]

        fno_df = load_fno()
        symbol_list = sorted(fno_df["name"].unique())
        symbol = st.selectbox("🔎 Select F&O Symbol", symbol_list)

        expiry_df = fno_df[fno_df["name"] == symbol]
        expiry = st.selectbox("📅 Select Expiry Date", sorted(expiry_df["expiry"].unique()))
        contract = expiry_df[expiry_df["expiry"] == expiry].iloc[0]

        tradingsymbol = contract["tradingsymbol"]
        lot_size = contract["lot_size"]
        last_price = contract["last_price"]

        st.info(f"📦 Trading Symbol: `{tradingsymbol}` | Lot Size: **{lot_size}** | LTP: ₹{last_price}")

        # --- Input Risk Parameters ---
        capital = st.number_input("💰 Total Capital (₹)", min_value=10000.0, value=500000.0, step=10000.0)
        risk_percent = st.number_input("🎯 Risk per Trade (%)", min_value=0.1, value=1.0, step=0.1)
        stop_loss_percent = st.number_input("🔻 Stop Loss (%)", min_value=0.1, value=2.0, step=0.1)
        entry_price = st.number_input("📈 Entry Price", value=last_price, step=1.0)

        # --- Position Sizing ---
        risk_amount = capital * risk_percent / 100
        sl_per_unit = entry_price * stop_loss_percent / 100
        units = int(risk_amount // (sl_per_unit * lot_size)) * lot_size

        if units == 0:
            st.error("⚠️ Capital too small or SL too tight for this trade.")
        else:
            st.success(f"✅ Position Size: **{units} units**")
            st.write(f"⚠️ Max Risk: ₹{units * sl_per_unit:.2f}")
            st.write(f"💼 Trade Value: ₹{units * entry_price:,.2f}")
            st.write(f"🔻 Stop Loss Level: ₹{entry_price - sl_per_unit:.2f}")

            # --- Margin Estimate ---
            st.write("---")
            st.write("🔍 Fetching Required Margin...")

            try:
                margin = kite.order_margins([{
                    "exchange": "NFO",
                    "tradingsymbol": tradingsymbol,
                    "transaction_type": kite.TRANSACTION_TYPE_BUY,
                    "quantity": units,
                    "product": kite.PRODUCT_MIS,
                    "order_type": kite.ORDER_TYPE_MARKET
                }])[0]

                st.success(f"💰 Total Margin Required: ₹{margin['total']:,}")
                st.write(f"- SPAN: ₹{margin['span']:,}")
                st.write(f"- Exposure: ₹{margin['exposure']:,}")
                st.write(f"- Charges: ₹{margin['charges']:,}")
            except Exception as e:
                st.error(f"❌ Margin fetch failed: {e}")

    except Exception as e:
        st.error(f"❌ Login failed: {e}")
else:
    st.info("🔑 First, log in via Kite and paste the `request_token` here.")
