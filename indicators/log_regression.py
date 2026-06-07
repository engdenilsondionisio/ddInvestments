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

    return df
