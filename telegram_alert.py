import json
import yfinance as yf
import requests
import os

# Load Telegram info from env
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CONFIG_PATH = "alerts.json"

def send_alert(symbol, current_price, target_price, condition):
    emoji = "📈" if condition == "above" else "📉"
    message = (
        f"{emoji} ALERT: {symbol} is now ₹{current_price:.2f} "
        f"({condition} ₹{target_price})"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def main():
    with open(CONFIG_PATH, "r") as f:
        alerts = json.load(f)

    for alert in alerts:
        symbol = alert["symbol"]
        target_price = float(alert["target_price"])
        condition = alert["condition"].lower()

        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")["Close"].iloc[-1]

            # Trigger logic
            if (condition == "above" and price >= target_price) or \
               (condition == "below" and price <= target_price):
                send_alert(symbol, price, target_price, condition)

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

if __name__ == "__main__":
    main()
