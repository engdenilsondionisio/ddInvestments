import requests
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def fetch_btc_history() -> pd.DataFrame:
    """Fetch full BTC daily close price history from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "max", "interval": "daily"}
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        prices = data.get("prices", [])
        df = pd.DataFrame(prices, columns=["timestamp_ms", "close"])
        df["date"] = pd.to_datetime(df["timestamp_ms"], unit="ms").dt.normalize()
        df = df.set_index("date").drop(columns=["timestamp_ms"])
        df = df[~df.index.duplicated(keep="last")].sort_index()
        df = df[df["close"] > 0]
        return df
    except Exception as e:
        st.error(f"Erro ao buscar preço BTC: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_mvrv_data() -> pd.DataFrame:
    """Fetch Market Cap and Realized Cap from CoinMetrics Community API to compute MVRV."""
    url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
    params = {
        "assets": "btc",
        "metrics": "CapMrktCurUSD,CapRealUSD",
        "frequency": "1d",
        "start_time": "2010-01-01",
        "page_size": "10000",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        rows = resp.json().get("data", [])
        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame()
        df["date"] = pd.to_datetime(df["time"]).dt.normalize()
        df = df.set_index("date")
        df["CapMrktCurUSD"] = pd.to_numeric(df["CapMrktCurUSD"], errors="coerce")
        df["CapRealUSD"] = pd.to_numeric(df["CapRealUSD"], errors="coerce")
        df = df.dropna(subset=["CapMrktCurUSD", "CapRealUSD"])
        df = df[df["CapRealUSD"] > 0]
        df["mvrv"] = df["CapMrktCurUSD"] / df["CapRealUSD"]
        return df[["mvrv"]].sort_index()
    except Exception as e:
        st.error(f"Erro ao buscar MVRV: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_fear_greed() -> dict:
    """Fetch Fear & Greed Index history from Alternative.me."""
    url = "https://api.alternative.me/fng/"
    params = {"limit": 365, "format": "json"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        entries = resp.json().get("data", [])
        if not entries:
            return _default_fg()
        current = entries[0]
        history = [
            {
                "date": pd.to_datetime(int(e["timestamp"]), unit="s").normalize(),
                "value": int(e["value"]),
                "classification": e["value_classification"],
            }
            for e in entries
        ]
        hist_df = pd.DataFrame(history).set_index("date").sort_index()
        return {
            "value": int(current["value"]),
            "classification": current["value_classification"],
            "history": hist_df,
        }
    except Exception as e:
        st.error(f"Erro ao buscar Fear & Greed: {e}")
        return _default_fg()


def _default_fg() -> dict:
    return {"value": 50, "classification": "Neutral", "history": pd.DataFrame()}
