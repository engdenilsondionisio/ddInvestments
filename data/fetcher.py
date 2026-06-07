import requests
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def fetch_btc_history() -> pd.DataFrame:
    """Fetch BTC daily close prices from Binance (paginated, no API key required)."""
    url = "https://api.binance.com/api/v3/klines"
    all_candles: list = []
    start_time = 1483228800000  # 2017-01-01 00:00:00 UTC in ms

    try:
        while True:
            params = {
                "symbol": "BTCUSDT",
                "interval": "1d",
                "startTime": start_time,
                "limit": 1000,
            }
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            candles = resp.json()
            if not candles:
                break
            all_candles.extend(candles)
            if len(candles) < 1000:
                break
            start_time = int(candles[-1][0]) + 86_400_000  # advance one day

        df = pd.DataFrame(all_candles)
        df["date"] = pd.to_datetime(df[0].astype(int), unit="ms").dt.normalize()
        df["close"] = df[4].astype(float)
        df = df.set_index("date")[["close"]]
        df = df[~df.index.duplicated(keep="last")].sort_index()
        df = df[df["close"] > 0]
        return df
    except Exception as e:
        st.error(f"Erro ao buscar preço BTC: {e}")
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
