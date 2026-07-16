# Paper research case study

This document summarizes selected experiments behind the public architecture.
It reports outcomes as they were observed, including weak and negative results.
All experiments were paper-only: no live orders and no capital at risk.

## Research question

Can explicit market-state guards and deterministic exits make short-side crypto
monitoring hypotheses more measurable and easier to invalidate?

The private research workspace included market snapshots, paper positions,
structured exit reasons, Telegram notifications, and frozen experiment plans.
This public repository exposes only generic engineering patterns and synthetic
fixtures. Credentials, real addresses, raw logs, exact private thresholds, and
execution code are intentionally excluded.

## Recorded experiments

| Experiment | Sample | Recorded paper result | Honest interpretation |
|---|---:|---:|---|
| Exit engine B vs. baseline | N=30 | Better than baseline, but still negative | No profitable edge demonstrated |
| Overheated-short guard | N=30 | +183.26 USDT; 66.67% wins | Confidence interval crossed zero; edge not proven |
| Market-regime guard | N=30 | +196.26 USDT; 70.00% wins | Confidence interval crossed zero; clean replication required |
| Hyperliquid guarded-short v1 | N=0 | No qualifying entries | Strict filters and data/rate constraints prevented evaluation |
| Hyperliquid guarded-short v2 | Ongoing | Pre-registered before observation | No conclusion until its stopping rule is met |

For the two positive 30-observation studies, the uncertainty interval included
zero. Their headline paper PnL and win rate therefore cannot support a claim of
a durable trading advantage. Small samples, market dependence, fees, slippage,
and selection effects remain material limitations.

## Engineering decisions demonstrated here

1. **Normalize at the boundary.** MEXC and Hyperliquid fields become one typed
   `MarketSnapshot` before any rule evaluates them. USD-, USDT-, and USDC-quoted
   markets share a `BASE/USD` comparison key. This is an analytical identifier,
   not a venue-native symbol suitable for placing an order.
2. **Use decimal arithmetic.** Price, spread, and percentage calculations avoid
   binary floating-point surprises.
3. **Keep rules deterministic.** The paper exit engine is a state machine with
   named reasons, making every transition testable and auditable.
4. **Collapse duplicate markets.** Breadth uses one vote per symbol even when
   the same asset is observed on two exchanges.
5. **Separate decisions from transport.** Formatters produce Telegram-ready
   text, but this repository contains no bot token and sends no message.
6. **Fail safely.** Missing anchors, insufficient breadth, malformed payloads,
   and timezone mistakes do not silently produce a positive signal.

## What this case study does not claim

- It is not a profitable strategy or financial advice.
- Paper results are not live execution results.
- The synthetic demo parameters are illustrative and are not the private
  research configuration.
- AI tools assisted implementation and review; tests, assumptions, and final
  decisions were checked by the author.

## Next valid research step

Complete the frozen Hyperliquid v2 observation window without intermediate
parameter tuning, preserve rejected observations, calculate uncertainty after
the stopping rule, and attempt an out-of-sample replication before considering
any live-capital discussion.

