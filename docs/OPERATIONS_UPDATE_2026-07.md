# Operational research snapshot — 2026-07-23

This is a dated, sanitized snapshot of the private paper-research workspace behind the public demo. It is intended to show how experiments are operated and evaluated, not to advertise a trading result.

## Scope and safety

- Every result below is from paper or shadow measurement; no live capital was authorized.
- Only aggregate metrics are published. Credentials, raw logs, exchange identifiers, private thresholds and order access remain private.
- Operational reliability and strategy edge are evaluated separately.
- Open unrealized PnL is not counted as a closed result.

## MEXC Move15 forward cohort

Last verified from read-only artifacts at **2026-07-23 09:53 UTC**.

The cohort was frozen before observation, started on 2026-07-17, and targets 60 PASS+BLOCK source signals with minimum resolved coverage in both groups.

| Metric | Verified value |
|---|---:|
| Source signals | 25 / 60 |
| Closed / open outcomes | 24 / 1 |
| PASS signals | 19 |
| PASS closed | 18 |
| PASS closed net PnL | +5.19 USDT |
| PASS margin expectancy | +0.26% |
| PASS symbol-cluster 95% CI | [-8.88%, +8.80%] |
| BLOCK counterfactual signals | 6 |
| BLOCK closed net PnL | -35.23 USDT |
| BLOCK margin expectancy | -4.31% |
| PASS-minus-BLOCK symbol-cluster 95% CI | [-5.81%, +17.51%] |

The point estimate is not a validated edge. Both the PASS interval and the PASS-minus-BLOCK interval include zero, comparison coverage is incomplete, leave-one-symbol-out stability is not yet satisfied, and the final decision remains **NOT_EVALUATED**.

Valid next action: keep collecting the frozen cohort without intermediate parameter tuning.

## Operational controls

At the snapshot time, the paper loop, price-path logger, forward monitor and read-only AI research supervisor were all running. Data quality was reported as `OK`, with no recorded errors in the prior 24 hours; candidate and mark freshness were approximately 36 seconds and 1 second.

The stack records component health, bounded-worker restarts, data freshness and open-position count. A PID alone is not treated as proof of health. Strategy auto-tuning, strategy-change authorization and live-capital authorization were all disabled.

The AI research supervisor can summarize deterministic metrics, but it cannot edit strategy files, databases or orders.

## Hyperliquid guarded-short v2

This cohort is **paused and incomplete**. The latest retained state contained 10 closed observations out of 30 planned:

| Metric | Interim value |
|---|---:|
| Closed observations | 10 / 30 |
| Interim paper net PnL | -49.66 USDT |
| Interim margin expectancy | -8.13% |
| Score-shadow observations | 7 |
| Score-shadow split | 4 PASS / 3 BLOCK |

The interim result is negative, but the pre-registered stopping rule was not reached. It is therefore reported as an incomplete experiment, not as a final strategy verdict. Stream reconnects were observed during collection and remain an operational limitation to resolve before any clean continuation.

## What this demonstrates

- frozen forward-only cohort definitions;
- preservation of BLOCK decisions as counterfactual observations;
- separation of closed outcomes from open unrealized marks;
- cost-aware net reporting and uncertainty intervals;
- symbol-cluster and leave-one-symbol-out checks;
- automated health, freshness and recovery monitoring;
- read-only AI analysis with explicit authority boundaries.

## Public/private boundary

The public repository contains synthetic fixtures, tests and generic architecture. Private runtime code, exact thresholds, credentials, addresses and raw operational logs are deliberately excluded.
