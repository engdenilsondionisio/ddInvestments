import numpy as np
import pandas as pd

GENESIS_DATE = pd.Timestamp("2009-01-03")


def enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add SMA50, SMA200, Log Regression Bands and MRI to the BTC price DataFrame."""
    df = df.copy()

    df["sma50"] = df["close"].rolling(50, min_periods=1).mean()
    df["sma200"] = df["close"].rolling(200, min_periods=1).mean()

    df["days"] = (df.index - GENESIS_DATE).days.astype(float)
    df = df[df["days"] > 0].copy()

    close = df["close"].values
    days = df["days"].values

    log_days = np.log(days)
    log_prices = np.log(close)

    a, b = np.polyfit(log_days, log_prices, 1)
    log_reg = a * log_days + b
    residuals = log_prices - log_reg
    std = float(np.std(residuals))

    df["log_regression"] = np.exp(log_reg)
    df["band_top2"] = np.exp(log_reg + 2.0 * std)
    df["band_top1"] = np.exp(log_reg + 1.0 * std)
    df["band_bot1"] = np.exp(log_reg - 1.0 * std)
    df["band_bot2"] = np.exp(log_reg - 2.0 * std)

    # Mean Reversion Index: rolling Z-score of log residuals (window=365d)
    residuals_series = pd.Series(residuals, index=df.index)
    rolling_std = residuals_series.rolling(window=365, min_periods=180).std()
    df["mri"] = residuals_series / rolling_std

    # Bollinger Bands (20-day, ±2σ)
    bb_sma = df["close"].rolling(20, min_periods=1).mean()
    bb_std = df["close"].rolling(20, min_periods=1).std().fillna(0)
    df["bb_upper"] = bb_sma + 2.0 * bb_std
    df["bb_mid"]   = bb_sma
    df["bb_lower"] = bb_sma - 2.0 * bb_std

    # Bull Market Support Band (Benjamin Cowen)
    df["bull_sma20w"] = df["close"].rolling(140, min_periods=1).mean()   # 20-week SMA
    df["bull_ema21w"] = df["close"].ewm(span=147, adjust=False).mean()    # 21-week EMA

    # MVRV approximation: price / realized_price_proxy
    # Realized price proxy = EWM of close prices (span=730 ≈ 2-year half-life)
    # Correlates well with actual realized price without requiring on-chain data
    realized_price = df["close"].ewm(span=730, min_periods=365).mean()
    df["mvrv"] = df["close"] / realized_price

    return df
