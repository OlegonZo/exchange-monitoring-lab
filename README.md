# Exchange Monitoring Lab

[![tests](https://github.com/OlegonZo/exchange-monitoring-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/OlegonZo/exchange-monitoring-lab/actions/workflows/tests.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**A sanitized, paper-only Python portfolio project for normalizing MEXC and
Hyperliquid market data, assessing market regime, and explaining deterministic
short-position exit decisions.**

[Русская версия](README_RU.md) · [Paper research case study](docs/CASE_STUDY.md) · [July 2026 operational snapshot](docs/OPERATIONS_UPDATE_2026-07.md)

> This repository does not place orders, connect to private APIs, or contain a
> trading strategy. It demonstrates engineering patterns with synthetic data.

## Why this project exists

My private research workspace grew from exchange scanners into a set of
repeatable paper experiments. Publishing that workspace directly would expose
credentials, raw logs, real addresses, and private research parameters. This
repository extracts the safe, employer-reviewable parts instead:

- typed boundaries around inconsistent exchange payloads;
- a canonical `BASE/USD` comparison key for USD, USDT, and USDC markets;
- `Decimal`-based price, return, spread, and volume handling;
- a transparent cross-market regime rule;
- a deterministic paper-only short exit state machine;
- Telegram-ready messages with transport and credentials deliberately absent;
- synthetic fixtures, unit tests, and CI across Python 3.11–3.13.

## Architecture

```text
synthetic JSON fixtures
        │
        ├── MEXC normalizer ─────────┐
        └── Hyperliquid normalizer ──┤
                                     ▼
                            MarketSnapshot
                              │          │
                              ▼          ▼
                       regime check   paper exit state
                              │          │
                              └────┬─────┘
                                   ▼
                         Telegram-ready text
                         (no network transport)
```

| Module | Responsibility |
|---|---|
| `models.py` | Immutable exchange-independent domain objects |
| `normalizers.py` | MEXC and Hyperliquid boundary adapters |
| `regime.py` | Anchor momentum plus unique-symbol market breadth |
| `paper_exit.py` | Hard stop, take profit, breakeven, trailing, timeout |
| `formatting.py` | Plain text suitable for a Telegram adapter |
| `cli.py` | Reproducible local demonstration from a JSON fixture |

`MarketSnapshot.symbol` is deliberately **not** an execution symbol. MEXC USDT
markets and Hyperliquid USDC-settled perpetual markets are mapped to a neutral
`BASE/USD` comparison key. A real order adapter would retain and validate each
venue's native symbol separately.

## Run the demo

No API keys or third-party packages are required.

```bash
python -m pip install -e .
python -m exchange_monitoring examples/sample_market_data.json
```

Expected excerpt:

```text
MARKET REGIME | RISK-ON
Anchor BTC/USD: +4.74%
Positive breadth: 100.00% across 3 markets
...
PAPER SHORT | SYNTH/USD | TRAILING_STOP
No order was placed.
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## What the tests cover

- MEXC spot/contract aliases and reconstruction of a missing day-open price;
- safe cross-venue mapping of USDT and USDC quotes to a comparison-only key;
- Hyperliquid asset-context normalization and spread calculation;
- invalid/crossed books and timestamp validation;
- unique-symbol breadth when an asset appears on both exchanges;
- hard stop, take profit, trailing state, and timeout transitions;
- end-to-end synthetic output that explicitly remains paper-only.

## Research integrity

The accompanying [case study](docs/CASE_STUDY.md) includes unsuccessful and
inconclusive experiments. Two N=30 paper studies recorded positive headline
results, but their uncertainty intervals crossed zero, so they do **not** prove
an edge. Another exit study remained negative. The Hyperliquid v2 study is
paused and incomplete at 10/30 observations; its interim paper result is
negative and no final conclusion is claimed. A dated
[operational snapshot](docs/OPERATIONS_UPDATE_2026-07.md) documents the active
MEXC forward cohort and the controls used to keep research read-only and
paper-only.

That distinction matters: monitoring software can be sound even when a market
hypothesis fails. I prefer reproducible evidence over a polished profit claim.

## AI-assisted workflow

AI tools were used for implementation support, refactoring, and review. The
workflow remained specification-led: define a bounded behavior, use synthetic
fixtures, add deterministic tests, inspect edge cases, and document what the
evidence cannot establish. Final assumptions and outputs were validated by the
author.

## Safety and scope

- synthetic prices and symbols only;
- no `.env`, keys, cookies, wallet addresses, or Telegram tokens;
- no exchange authentication or order endpoint;
- no live trading, leverage, or capital allocation;
- public defaults are illustrative, not private production parameters;
- not financial advice.

## Author

**Oleg Gulyaev** — crypto researcher and AI-assisted automation builder.

This project is intended for technical portfolio review and educational use.

