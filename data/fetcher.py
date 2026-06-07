import requests
import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=300)
def fetch_btc_history() -> pd.DataFrame:
    """Fetch BTC daily close prices from Yahoo Finance via yfinance (no API key required)."""
    try:
        df = yf.download("BTC-USD", period="max", interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            raise ValueError("Nenhum dado retornado pelo Yahoo Finance.")
        # yfinance >=0.2 may return MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Close"]].rename(columns={"Close": "close"})
        df.index = pd.to_datetime(df.index)
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        df.index = df.index.normalize()
        df.index.name = "date"
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
