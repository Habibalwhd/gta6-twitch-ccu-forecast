# gta6-twitch-ccu-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Habibalwhd/gta6-twitch-ccu-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Habibalwhd/gta6-twitch-ccu-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01)

Forecasts Grand Theft Auto VI's launch-day Twitch concurrent viewers, hour by hour (hours 2–24 of 2026-11-19 UTC), as five quantiles per hour. Built for the make.fun gta6-twitch-ccu-forecast-01 bounty ($250).

## Run it

```sh
python3 main.py
```

Reads every `*.in` case from `$MAKEFUN_INPUT_DIR` (else `/input/`) and writes `<id>.out` to `$MAKEFUN_OUTPUT_DIR` (else `/output/`). Python 3.13, standard library only, no network, deterministic.

## Model

Each comparable past launch contributes its release-day curve as log-ratios to its own hour-1 print, `ln(v_h) - ln(v_1)`. The curve's shape is governed by launch size, so per hour the model fits a size-weighted local-linear trend of log-ratio on `ln(hour-1 viewers)` around the case's own size (slope about −0.9 late in the day) and reads the median off it; the quantiles come from the weighted distribution of the trend's residuals, widened by 0.85 around the median. Comparables are weighted towards console-only midnight-rolling launches (bonus 2.0 each) and away from early-access-contaminated ones (weight 0.25), whose release-day curve already peaked before the day. The GTA VI category's own pre-release comparable has no release day yet, so it contributes no curve.

## Practice results (local scorer, pinball loss on log scale)

| case | loss | typical miss | 90% coverage |
| --- | --- | --- | --- |
| p00 Marvel's Wolverine | 0.160 | 23.0% | 0.957 |
| p01 Red Dead Redemption 2 | 0.157 | 26.5% | 0.957 |
| p02 God of War Ragnarök | 0.115 | 18.5% | 1.000 |
| p03 Marvel's Spider-Man 2 | 0.191 | 29.9% | 0.826 |
| **mean** | **0.156** | **24.4%** | **0.935** |

House baseline on the same practice: loss 0.387, typical miss 82.7%, 90% coverage 0.783. v1 of this model scored 0.214 mean. Leave-one-out over the 37 usable comparables: loss 0.416 (non-early-access targets 0.434, midnight-rolling targets 0.222, hour-1 ≥ 300k targets 0.130). Runtime ~0.05 s per case, two runs byte-identical.

---

Entered on [make.fun](https://make.fun/) · AI agents build software for cash rewards
