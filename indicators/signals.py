def _score(value, thresholds: list, scores: list) -> float:
    """Map a value to a score using a list of (threshold, score) breakpoints (ascending)."""
    for threshold, score in zip(thresholds, scores):
        if value < threshold:
            return score
    return scores[-1]


def generate_signal(
    mri: float,
    mvrv: float,
    fear_greed: int,
    price: float,
    sma200: float,
) -> dict:
    """
    Compute a weighted buy/sell score from four indicators.
    Returns a dict with keys: signal, score, color, details.
    """
    # MRI score (weight 35%) — negative MRI = oversold = buy pressure
    mri_score = _score(
        mri,
        [-2.0, -1.0, 1.0, 2.0],
        [2.0, 1.0, 0.0, -1.0, -2.0],
    )

    # MVRV score (weight 30%)
    mvrv_score = _score(
        mvrv,
        [1.0, 1.5, 3.0, 4.0],
        [2.0, 1.0, 0.0, -1.0, -2.0],
    )

    # Fear & Greed score (weight 20%) — contrarian: extreme fear = buy
    fg_score = _score(
        fear_greed,
        [20, 35, 65, 80],
        [2.0, 1.0, 0.0, -1.0, -2.0],
    )

    # SMA200 deviation score (weight 15%)
    deviation = ((price - sma200) / sma200 * 100) if sma200 > 0 else 0.0
    sma_score = _score(
        deviation,
        [-30.0, -10.0, 10.0, 50.0],
        [2.0, 1.0, 0.0, -1.0, -2.0],
    )

    final_score = (
        mri_score * 0.35
        + mvrv_score * 0.30
        + fg_score * 0.20
        + sma_score * 0.15
    )

    if final_score >= 1.2:
        signal, color = "COMPRA FORTE", "#00C853"
    elif final_score >= 0.4:
        signal, color = "COMPRA", "#69F0AE"
    elif final_score >= -0.4:
        signal, color = "NEUTRO / HOLD", "#FFD740"
    elif final_score >= -1.2:
        signal, color = "VENDA", "#FF6D00"
    else:
        signal, color = "VENDA FORTE", "#FF1744"

    return {
        "signal": signal,
        "color": color,
        "score": round(final_score, 2),
        "details": {
            "MRI": round(mri_score, 1),
            "MVRV": round(mvrv_score, 1),
            "Fear & Greed": round(fg_score, 1),
            "SMA200 Dev.": round(sma_score, 1),
        },
        "values": {
            "MRI atual": round(mri, 2),
            "MVRV atual": round(mvrv, 2),
            "Fear & Greed": fear_greed,
            "Desvio SMA200": f"{deviation:+.1f}%",
        },
    }
