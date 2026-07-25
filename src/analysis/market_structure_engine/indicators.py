from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .config import TimeframeProfile
from .utils import round_or_none, safe_div


def sma(values: list[float | None], length: int) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    window: list[float] = []
    for index, value in enumerate(values):
        if value is None:
            window = []
            continue
        window.append(float(value))
        if len(window) > length:
            window.pop(0)
        if len(window) == length:
            output[index] = sum(window) / length
    return output


def ema(values: list[float], length: int) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    if len(values) < length:
        return output
    seed = sum(values[:length]) / length
    output[length - 1] = seed
    alpha = 2.0 / (length + 1.0)
    previous = seed
    for index in range(length, len(values)):
        previous = alpha * values[index] + (1.0 - alpha) * previous
        output[index] = previous
    return output


def wilder_rma(values: list[float | None], length: int) -> list[float | None]:
    output: list[float | None] = [None] * len(values)
    valid_indexes = [i for i, value in enumerate(values) if value is not None]
    if len(valid_indexes) < length:
        return output
    first_indexes = valid_indexes[:length]
    if first_indexes[-1] - first_indexes[0] != length - 1:
        return output
    seed_index = first_indexes[-1]
    seed = sum(float(values[i] or 0.0) for i in first_indexes) / length
    output[seed_index] = seed
    previous = seed
    for index in range(seed_index + 1, len(values)):
        value = values[index]
        if value is None:
            output[index] = None
            continue
        previous = ((length - 1) * previous + float(value)) / length
        output[index] = previous
    return output


def true_range(bars: list[dict[str, Any]]) -> list[float]:
    result: list[float] = []
    for index, bar in enumerate(bars):
        if index == 0:
            result.append(bar["high"] - bar["low"])
        else:
            previous_close = bars[index - 1]["close"]
            result.append(
                max(
                    bar["high"] - bar["low"],
                    abs(bar["high"] - previous_close),
                    abs(bar["low"] - previous_close),
                )
            )
    return result


def rsi(closes: list[float], length: int) -> list[float | None]:
    gains: list[float | None] = [None]
    losses: list[float | None] = [None]
    for previous, current in zip(closes, closes[1:]):
        delta = current - previous
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))
    avg_gain = wilder_rma(gains, length)
    avg_loss = wilder_rma(losses, length)
    output: list[float | None] = [None] * len(closes)
    for index, (gain, loss) in enumerate(zip(avg_gain, avg_loss)):
        if gain is None or loss is None:
            continue
        if loss == 0:
            output[index] = 100.0 if gain > 0 else 50.0
        else:
            rs = gain / loss
            output[index] = 100.0 - 100.0 / (1.0 + rs)
    return output


def macd(
    closes: list[float],
    fast: int,
    slow: int,
    signal: int,
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    fast_values = ema(closes, fast)
    slow_values = ema(closes, slow)
    line: list[float | None] = [
        None if a is None or b is None else a - b for a, b in zip(fast_values, slow_values)
    ]
    compact = [value for value in line if value is not None]
    compact_signal = ema(compact, signal)
    signal_values: list[float | None] = [None] * len(line)
    cursor = 0
    for index, value in enumerate(line):
        if value is None:
            continue
        signal_values[index] = compact_signal[cursor]
        cursor += 1
    histogram = [
        None if value is None or sig is None else value - sig
        for value, sig in zip(line, signal_values)
    ]
    return line, signal_values, histogram


def adx(
    bars: list[dict[str, Any]],
    length: int,
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    plus_dm: list[float | None] = [None]
    minus_dm: list[float | None] = [None]
    tr: list[float | None] = [None]
    for index in range(1, len(bars)):
        up_move = bars[index]["high"] - bars[index - 1]["high"]
        down_move = bars[index - 1]["low"] - bars[index]["low"]
        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
        tr.append(
            max(
                bars[index]["high"] - bars[index]["low"],
                abs(bars[index]["high"] - bars[index - 1]["close"]),
                abs(bars[index]["low"] - bars[index - 1]["close"]),
            )
        )
    smoothed_plus = wilder_rma(plus_dm, length)
    smoothed_minus = wilder_rma(minus_dm, length)
    smoothed_tr = wilder_rma(tr, length)
    plus_di: list[float | None] = [None] * len(bars)
    minus_di: list[float | None] = [None] * len(bars)
    dx: list[float | None] = [None] * len(bars)
    for index in range(len(bars)):
        if smoothed_tr[index] in (None, 0):
            continue
        plus = 100.0 * float(smoothed_plus[index] or 0.0) / float(smoothed_tr[index] or 1.0)
        minus = 100.0 * float(smoothed_minus[index] or 0.0) / float(smoothed_tr[index] or 1.0)
        plus_di[index] = plus
        minus_di[index] = minus
        dx[index] = 100.0 * safe_div(abs(plus - minus), plus + minus)
    adx_values = wilder_rma(dx, length)
    return adx_values, plus_di, minus_di


def roc(closes: list[float], length: int) -> list[float | None]:
    output: list[float | None] = [None] * len(closes)
    for index in range(length, len(closes)):
        base = closes[index - length]
        output[index] = 100.0 * safe_div(closes[index] - base, base)
    return output


def calculate_indicators(bars: list[dict[str, Any]], profile: TimeframeProfile) -> dict[str, Any]:
    closes = [bar["close"] for bar in bars]
    tr_values = true_range(bars)
    atr_input: list[float | None] = list(tr_values)
    atr_values = wilder_rma(atr_input, profile.atr_length)
    atr_average = sma(atr_values, profile.atr_average_length)
    ema_fast = ema(closes, profile.ema_fast)
    ema_medium = ema(closes, profile.ema_medium)
    ema_slow = ema(closes, profile.ema_slow)
    rsi_values = rsi(closes, profile.rsi_length)
    macd_line, macd_signal, macd_histogram = macd(
        closes, profile.macd_fast, profile.macd_slow, profile.macd_signal
    )
    adx_values, plus_di, minus_di = adx(bars, profile.adx_length)
    roc_values = roc(closes, profile.roc_length)

    def latest(values: Iterable[float | None]) -> float | None:
        return next((value for value in reversed(list(values)) if value is not None), None)

    latest_close = closes[-1]
    latest_atr = latest(atr_values)
    alignment = "MIXED"
    ef, em, es = latest(ema_fast), latest(ema_medium), latest(ema_slow)
    if None not in (ef, em, es) and ef is not None and em is not None and es is not None:
        if latest_close > ef > em > es:
            alignment = "BULLISH"
        elif latest_close < ef < em < es:
            alignment = "BEARISH"

    return {
        "latest": {
            "close": round_or_none(latest_close),
            "ema_20": round_or_none(ef),
            "ema_50": round_or_none(em),
            "ema_200": round_or_none(es),
            "ema_alignment": alignment,
            "atr_14": round_or_none(latest_atr),
            "atr_14_average_50": round_or_none(latest(atr_average)),
            "rsi_14": round_or_none(latest(rsi_values)),
            "macd_line": round_or_none(latest(macd_line)),
            "macd_signal": round_or_none(latest(macd_signal)),
            "macd_histogram": round_or_none(latest(macd_histogram)),
            "adx_14": round_or_none(latest(adx_values)),
            "plus_di_14": round_or_none(latest(plus_di)),
            "minus_di_14": round_or_none(latest(minus_di)),
            "roc_14": round_or_none(latest(roc_values)),
        },
        "series": {
            "true_range": tr_values,
            "atr_14": atr_values,
            "ema_20": ema_fast,
            "ema_50": ema_medium,
            "ema_200": ema_slow,
            "rsi_14": rsi_values,
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_histogram": macd_histogram,
            "adx_14": adx_values,
            "plus_di_14": plus_di,
            "minus_di_14": minus_di,
            "roc_14": roc_values,
        },
        "formula_metadata": {
            "ema": "SMA seed, recursive alpha=2/(length+1)",
            "atr": "standard true range with Wilder RMA",
            "rsi": "Wilder average gain/loss",
            "macd": "EMA fast minus EMA slow with EMA signal",
            "adx": "Wilder DMI/ADX",
            "roc": "100*(close/close[n]-1)",
        },
    }
