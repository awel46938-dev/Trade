import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="My Trading Bot", layout="wide")
st.title("🤖 My Free Daily Trading Bot (Candlestick + Indicators)")

st.sidebar.header("Settings")
tickers_input = st.sidebar.text_input("Stocks (comma separated)", "AAPL, TSLA, NVDA, MSFT")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

enable_auto = st.sidebar.checkbox("Enable Paper Auto Trading (Alpaca)", value=False)
alpaca_key = st.sidebar.text_input("Alpaca API Key", type="password")
alpaca_secret = st.sidebar.text_input("Alpaca Secret Key", type="password")

def simple_candlestick_signal(df):
    if len(df) < 5:
        return "HOLD", []
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    reasons = []
    score = 0
    
    # Simple Hammer-like (long lower shadow)
    body = abs(latest['Close'] - latest['Open'])
    lower_shadow = min(latest['Open'], latest['Close']) - latest['Low']
    if lower_shadow > 2 * body:
        score += 3
        reasons.append("Hammer pattern")
    
    # Bullish Engulfing simple check
    if (prev['Close'] < prev['Open'] and 
        latest['Close'] > latest['Open'] and 
        latest['Close'] > prev['Open']):
        score += 3
        reasons.append("Bullish Engulfing")
    
    df['RSI'] = ta.rsi(df['Close'], length=14)
    if latest['RSI'] < 30:
        score += 2
        reasons.append("RSI Oversold")
    
    signal = "BUY" if score >= 5 else "SELL" if score <= -4 else "HOLD"
    return signal, reasons, round(latest['Close'], 2)

if st.button("🔄 Scan Stocks Now"):
    results = []
    for ticker in tickers:
        try:
            df = yfinance.download(ticker, period="3mo", interval="1d", progress=False)
            signal, reasons, price = simple_candlestick_signal(df)
            results.append({
                "Stock": ticker,
                "Price": price,
                "Signal": signal,
                "Reasons": ", ".join(reasons)
            })
        except:
            results.append({"Stock": ticker, "Price": "-", "Signal": "Error", "Reasons": ""})
    
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    
    st.success(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

st.caption("This is for education only. Paper trading has risks. Start with auto OFF.")
