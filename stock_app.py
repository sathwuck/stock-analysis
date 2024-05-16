import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests


API_KEY = '3YE7WM629T7OPA8I'
BASE_URL = 'https://www.alphavantage.co/query'


def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY,
        'outputsize': 'compact'  # Using 'compact' to limit data to last 100 days for faster performance
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        return df
    else:
        st.error(f"Failed to fetch data for {symbol}. Please check the stock symbol and try again.")
        return None


def preprocess_data(df):
    df = df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })
    df = df.sort_index()
    return df


def display_stock_info(df, symbol):
    start_date = df.index.min()
    latest_date = df.index.max()
    latest_open = df.loc[latest_date, 'Open']
    latest_close = df.loc[latest_date, 'Close']
    profit_loss = latest_close - latest_open

    st.write(f"**{symbol} Stock Information**")
    st.write(f"**Data From:** {start_date.strftime('%Y-%m-%d')}")
    st.write(f"**Latest Date:** {latest_date.strftime('%Y-%m-%d')}")
    st.write(f"**Opening Price:** ${latest_open:.2f}")
    st.write(f"**Closing Price:** ${latest_close:.2f}")
    st.write(f"**Profit/Loss:** ${profit_loss:.2f}")

    if profit_loss > 0:
        st.success(f"Profit: ${profit_loss:.2f}")
    else:
        st.error(f"Loss: ${profit_loss:.2f}")

    return start_date, latest_date, latest_open, latest_close, profit_loss


def plot_stock_data(df, symbol):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df['Close'], label='Close Price')
    ax.set_title(f'{symbol} Stock Price')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)


# Streamlit App
st.title("Stock Market Analysis Tool")

symbols = st.text_area("Enter Stock Symbols (comma separated):", "AAPL, MSFT, AMZN")

if st.button("Fetch Data"):
    symbols = symbols.split(',')
    summary = []

    for symbol in symbols:
        symbol = symbol.strip().upper()
        df = fetch_stock_data(symbol)
        if df is not None:
            df = preprocess_data(df)
            start_date, latest_date, latest_open, latest_close, profit_loss = display_stock_info(df, symbol)
            summary.append({
                "Symbol": symbol,
                "Data From": start_date,
                "Latest Date": latest_date,
                "Open": latest_open,
                "Close": latest_close,
                "Profit/Loss": profit_loss
            })
            plot_stock_data(df, symbol)

    if summary:
        st.write("## Summary Table")
        summary_df = pd.DataFrame(summary)
        summary_df["Data From"] = summary_df["Data From"].dt.strftime('%Y-%m-%d')
        summary_df["Latest Date"] = summary_df["Latest Date"].dt.strftime('%Y-%m-%d')
        st.dataframe(summary_df)
