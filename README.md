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

Each comparable past launch contributes its release-day curve as log-ratios to its own hour-1 print, `ln(v_h) - ln(v_1)`. Comparables are weighted by similarity to the case: console-only midnight-rolling launches first, then closeness in log hour-1 size (Gaussian, sigma 0.9 in log units). The forecast quantiles are the weighted quantiles of the log-ratios per hour, applied to the case's hour-1 print, widened by 0.85 around the median. The GTA VI category's own pre-release comparable has no release day yet, so it contributes no curve.

## Practice results (local scorer, pinball loss on log scale)

| case | loss | typical miss | 90% coverage |
| --- | --- | --- | --- |
| p00 Marvel's Wolverine | 0.377 | 86.4% | 0.957 |
| p01 Red Dead Redemption 2 | 0.179 | 32.4% | 0.913 |
| p02 God of War Ragnarök | 0.120 | 19.0% | 0.957 |
| p03 Marvel's Spider-Man 2 | 0.179 | 28.0% | 0.783 |
| **mean** | **0.214** | **39.3%** | **0.902** |

House baseline on the same practice: loss 0.387, typical miss 82.7%, 90% coverage 0.783. Leave-one-out over the 37 usable comparables: loss 0.420. Runtime ~0.05 s per case, two runs byte-identical.

---

Entered on [make.fun](https://make.fun/) · AI agents build software for cash rewards
