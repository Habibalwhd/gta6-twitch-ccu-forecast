#!/usr/bin/env python3
"""Forecast GTA VI's launch-day Twitch viewers hour by hour (make.fun
gta6-twitch-ccu-forecast-01), Python 3.13, standard library only.

Method: for every comparable past launch, take its release-day curve as a
log-ratio to its own hour-1 print, lr[h] = ln(v_h) - ln(v_1), hours 2..24.
Weight each comparable by how much its launch resembles this case --
console-only midnight-rolling launches first (every case in this contest
is one: GTA VI on PS5/Xbox Series, and all four practice launches are
console-only too), then closeness in log hour-1 size -- and read the
forecast quantiles off the weighted distribution of log-ratios per hour,
applied to this case's hour-1 print. A small widening factor keeps the
90% band honest. No network, no randomness: two runs are byte-identical.
"""

import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]

# Every launch in this contest unlocks at midnight local time, rolling
# country by country, on consoles only -- so those are the traits a
# comparable is weighted towards.
CONSOLE_BONUS = 2.0       # comparable has no PC in its platforms
ROLLING_BONUS = 1.5       # unlock text says midnight local / rolling
SIMULT_BONUS = 0.7        # unlock text says simultaneous / single global
LOGH1_SIGMA = 0.9         # Gaussian width on ln(hour-1 viewers)
WEIGHT_FLOOR = 0.0        # tuned to zero: any floor lets the tiny-hour-1
                          # explosive curves (log-ratios up to +7) leak
                          # weight into every forecast
WIDEN = 0.85              # tuned down from 1.15: the v1 bands covered
                          # 0.946 of practice hours, wider than the honest
                          # 0.90, and narrowing them cut the loss


def _parse_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def _is_console_only(platforms):
    return "PC" not in (platforms or "")


def _unlock_kind(unlock):
    text = (unlock or "").lower()
    if "midnight local" in text or "rolling" in text:
        return "rolling"
    if "simultaneous" in text or "single global" in text or "global unlock" in text:
        return "simultaneous"
    return "other"


def _log_ratio_curve(comp):
    """Release-day log-ratio curve of one comparable, hours 2..24, plus its
    hour-1 viewers -- or (None, None) when its day is incomplete (the GTA
    VI pre-release comparable has no release day yet, so it is left out
    here)."""
    day_start = _parse_time(comp["day_start"])
    by_hour = {}
    for point in comp["hourly"]:
        delta = (_parse_time(point["from"]) - day_start).total_seconds() / 3600.0
        hour = int(delta) + 1
        if 1 <= hour <= 24:
            viewers = point.get("viewers") or 0
            if viewers > 0:
                by_hour[hour] = viewers
    if len(by_hour) != 24:
        return None, None
    first = math.log(by_hour[1])
    curve = [math.log(by_hour[h]) - first for h in range(2, 25)]
    return curve, float(by_hour[1])


def _weight(comp, log_h1):
    weight = 1.0
    if _is_console_only(comp.get("platforms")):
        weight *= CONSOLE_BONUS
    kind = _unlock_kind(comp.get("unlock"))
    if kind == "rolling":
        weight *= ROLLING_BONUS
    elif kind == "simultaneous":
        weight *= SIMULT_BONUS
    curve_h1 = comp["_h1"]
    weight *= math.exp(-0.5 * ((math.log(curve_h1) - log_h1) / LOGH1_SIGMA) ** 2)
    return weight + WEIGHT_FLOOR


def _weighted_quantile(pairs, tau):
    """pairs: list of (value, weight), sorted by value. Smallest value whose
    cumulative weight reaches tau of the total."""
    ordered = sorted(pairs)
    total = sum(w for _, w in ordered)
    target = tau * total
    acc = 0.0
    for value, weight in ordered:
        acc += weight
        if acc >= target:
            return value
    return ordered[-1][0]


def forecast_case(case):
    first = next((k for k in case["known"] if k["hour"] == 1), None)
    if first is None:
        raise ValueError("case has no hour-1 print")
    p1 = max(1.0, float(first["viewers"]))
    log_h1 = math.log(p1)

    curves = []
    for comp in case["comparables"]:
        curve, h1 = _log_ratio_curve(comp)
        if curve is None or h1 is None or h1 <= 0:
            continue
        comp = dict(comp)
        comp["_h1"] = h1
        curves.append((comp, curve))

    if not curves:
        # No usable comparable: fall back to the flat baseline shape.
        curves = []

    rows = []
    for idx, hour in enumerate(range(2, 25)):
        if curves:
            pairs = [(_w[1][idx], _weight(_w[0], log_h1)) for _w in curves]
            median = _weighted_quantile(pairs, 0.5)
            quantiles = []
            for tau in LEVELS:
                q = _weighted_quantile(pairs, tau)
                quantiles.append(median + WIDEN * (q - median))
        else:
            quantiles = [0.0] * 5
        values = []
        prev = 0.0
        for lr in quantiles:
            v = p1 * math.exp(lr)
            v = min(max(v, 1.0), 1e9)
            v = round(v, 2)
            if v < prev:
                v = prev
            values.append(v)
            prev = v
        rows.append({"hour": hour, "q": values})
    return {"hours": rows}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        forecast = forecast_case(case)
        (OUTPUT_DIR / f"{path.stem}.out").write_text(
            json.dumps(forecast, separators=(",", ":")) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
