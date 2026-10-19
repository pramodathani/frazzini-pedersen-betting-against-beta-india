# Plan: Betting Against Beta on Indian shares

Status: draft for Pramod's approval (Adapt to India gate), 2026-10-19. Page numbers refer to the authors' 10 May 2013 manuscript in `paper/`.

## 1. What we will reproduce

| Paper | Indian version | Notes |
|---|---|---|
| Table I (p.39), sample description | Number of shares per month, in the full and the liquid universe | |
| Table III/IV (pp.41-42), beta deciles and BAB | The core table: P1 to P10 plus BAB, with excess return, CAPM / 3-factor / 4-factor alphas, ex-ante and realised beta, volatility and Sharpe ratio | No 5-factor alpha: there is no Indian Pastor-Stambaugh factor |
| Table V (p.43), BAB by country | A single India row in the same columns, set beside the paper's 19 countries | |
| Table B1 (p.66), factor loadings of the two legs, $long and $short | Same | |
| Table B2 (p.67), alternative beta windows | Correlation over 5, 3 and 1 years | |
| Table B3 (p.68), BAB within size groups | Size quintiles, not deciles, because there are too few shares. Size is median traded value. | No market capitalisation before 2024 (gap 10) |
| Table B4 (p.69), subperiods | Three subperiods of about six years each | |
| Table B5 (p.70), BAB within idiosyncratic-volatility groups | Quintiles | |
| Table B9 (pp.63-64, 74), 2 size × 3 beta "value-weighted" BAB | Weights proportional to traded value instead of market cap. Both beta-neutral and dollar-neutral versions. | Answers the Novy-Marx and Velikov critique that rank weighting drives the result |

Two extra parts for an Indian investor, which the paper does not have:

1. **Long-only low-beta portfolios.** These are the lowest-beta decile, the lowest quintile, and the rank-weighted low-beta leg, all in the liquid universe. Each is rebalanced monthly and also quarterly, the quarterly version to cut costs. Each is reported before and after delivery costs against the NIFTY 500 TRI, and beside the NIFTY100 Low Volatility 30 and NIFTY Low Volatility 50 total-return indices.
2. **The levered low-beta leg scaled to beta one** (the long half of BAB). This shows what leverage adds, financed at the T-bill rate. That rate is an optimistic assumption, and we say so.

Out of scope: Tables IX and X (TED spread and beta compression) need an Indian funding-spread series we do not have. Table XI (holdings) and the non-equity asset classes need data we do not have either. We can add an Indian TED analogue later if you want one.

## 2. What changes for India, and why

| Item | Paper | India | Why |
|---|---|---|---|
| **Universe** | All CRSP common stocks (share codes 10 and 11) | **Full:** every NSE share in series EQ, BE or BZ, delisted shares included, without ETFs, fund units, rights entitlements or partly-paid shares. **Liquid (main):** the 500 shares with the highest median daily traded value over the past 12 months, a stand-in for the NIFTY 500 | There is no index-membership history (gap 11). Thinly traded micro-caps give unreliable betas and cannot be traded at our cost assumptions. |
| **Decile breakpoints** | NYSE breakpoints | Breakpoints from the liquid universe, applied to the full universe | This plays the same role as NYSE: a breakpoint set that small shares do not dominate. |
| **Dates** | 1926 to 2012 | Daily returns from January 2005, when the corporate-action list becomes complete. The first ranking needs 750 days of returns, so portfolios start in about January 2008 and end with the last full month, September 2026: about 225 months | Our clean, adjusted history starts in 2005. |
| **Beta estimate** | 1-year volatility of 1-day log returns (at least 120 days). 5-year correlation of overlapping 3-day log returns (at least 750 days). β = 0.6·β_TS + 0.4 | The same formula against the daily NIFTY 500 TRI, with log returns not reduced by the risk-free rate | The daily risk-free rate is tiny. The paper is ambiguous here (p.16 versus p.17); we record our choice. |
| **Market** | CRSP value-weighted index, or the local MSCI index | NIFTY 500 total-return index, daily from 1995 | A free-float value-weighted broad index. MSCI India is not freely available. |
| **Risk-free rate** | US one-month T-bill | IIMA's monthly RF (RBI 91-day T-bill), through December 2025. For 2026 we will fetch RBI 91-day auction results at the Data stage; failing that, we carry December 2025 forward and report risk-adjusted statistics through December 2025 as the main ones | FRED is not reachable from this machine, and IIMA's file ends in 2025-12. |
| **Factors** | French's SMB, HML and UMD, plus Pastor-Stambaugh liquidity | IIMA's survivorship-bias-adjusted SMB, HML and WML; the market is NIFTY 500 TRI minus RF | This is the standard Indian factor set. There is no liquidity factor, so there is no 5-factor alpha. |
| **Size** | Market cap | Median daily traded value | NSE market-cap files exist only from February 2024; the PR archives for 2010 and 2015 have no MCAP file (checked today). |
| **Trading hours and timing** | Monthly | Betas use data up to the last session of month t−1. Positions are formed at that close and held through month t. A robustness run waits one extra session before trading | This keeps the paper's timing, and the extra-session run shows the cost of a realistic delay. |
| **Settlement** | n/a | T+1 delivery, so cash from sales is usable for buys the next day | Monthly rebalancing is unaffected. |
| **Short selling** | Free shorting assumed | Overnight shorting of shares is possible only through stock lending (thin) or single-stock futures (about 200 shares). The long-short BAB is therefore a **research factor**. It gets delivery costs on both sides, but no borrowing fee is charged (brahmagupta gap 27) | We say so beside every BAB number. |
| **Costs** | None in the paper | brahmagupta delivery costs: STT, stamp duty, exchange and SEBI fees, GST and brokerage. Market impact is 0.10% a side for the liquid universe and 0.30% for the full universe. Everything is reported before and after costs | These follow the house rules. |
| **Leverage** | The low leg is levered to beta one, about $1.40 long | Shown as a research portfolio, financed at the T-bill rate. It is not an Indian retail product | brahmagupta's cash earns zero. We run it on excess returns so the financing is consistent (a new gap is recorded). |
| **Benchmark** | n/a | NIFTY 500 TRI, plus NIFTY100 Low Volatility 30 TRI and NIFTY Low Volatility 50 TRI (daily from at least 2006, checked today). Index data from before each index's launch are NSE's back-calculations | |

## 3. Data, and where it comes from

| Data | Source | Status |
|---|---|---|
| Daily bhavcopies, 1995-01-02 to 2026-10-16 (old format and UDiFF) | jt-pilot's raw downloads, read-only: `external/earlier_bhavcopy_raw` and `nse/bhavcopy_raw/2026` | Reused. The Data stage tops them up to the latest session into our own `data/`. |
| Corporate actions, 1995 to 2026 (complete from 2005) | jt-pilot `external/earlier_corporate_actions` and `nse/corporate_actions/2026.json` | Reused, and refreshed for 2026 |
| NIFTY 500 TRI, daily from 1995 | jt-pilot `nse/nifty500_tri.json` | Reused, and topped up |
| IIMA factors and RF, monthly to 2025-12 | jt-pilot `nse/iima/` | Reused |
| NIFTY100 Low Vol 30 and NIFTY Low Vol 50 TRI | niftyindices.com endpoint (tested today) | New download |
| RF for 2026 | RBI 91-day T-bill auction results | To find at the Data stage |
| UBI daily prices, December 2019 onwards | `export_prices` | Used only to cross-check our adjusted prices, because UBI's history is too short for 5-year correlations (gaps 1, 2 and 7) |

Every reused file will be listed in `data/README.md`. We will not read jt-pilot's code, derived files or results. Returns are adjusted for splits, bonuses and dividends from the corporate-action list, and we check the adjustment on known actions. Daily moves below −50% or above +100% are treated as data errors: they are set to zero and logged.

## 4. Code and tests

The package is `frazzini_pedersen_india`, and its backtests run on brahmagupta. The unit tests use small made-up data with known answers and need no network. They will cover:
1. Adjusted returns: a made-up split, bonus and dividend give the expected return on the ex-date.
2. The universe filter: ETFs, fund units and rights entitlements are removed, and delisted shares are kept until they stop trading.
3. Overlapping 3-day log returns and the minimum-observation rules (120 and 750 days).
4. The beta estimator recovers a known beta from simulated returns, and shrinkage gives 0.6·β + 0.4.
5. **No look-ahead:** changing returns after a formation date leaves that date's betas and weights unchanged.
6. Rank weights (eq. 16): each leg sums to one, matches a hand-worked example, and gives a zero ex-ante BAB beta after the eq. 17 scaling.
7. Decile breakpoints from the liquid universe, and equal weights within each decile.
8. Alignment of the risk-free rate and the factors with portfolio months, and the Newey-West t-statistics on a known series.

Commits come in phases: data adapters, returns, betas, portfolios, statistics, then scripts.

## 5. Statistics and honesty rules

- Every average return comes with a Newey-West t-statistic, the number of months and the worst drawdown, before and after costs.
- **Main specification, fixed before any results:** the paper's beta, the full universe with liquid-universe breakpoints for the deciles and for BAB, and the long-only lowest decile of the liquid universe rebalanced monthly.
- **Planned variants: about 20** (beta windows, universes, weighting schemes, rebalancing frequency, the one-session delay). We will report the count and will not promote the best variant.
- The backtest_reviewer subagent checks the backtests before any result is reported.
- **Delisting losses.** The bhavcopies hold delisted shares, but not the value at delisting. A stress test charges −100% (and −30%) the month after a share's last trade.

## 6. Where India cannot match the paper

1. **About 18 years, not 86.** With roughly 225 months, standard errors will be wider. A Sharpe ratio of 0.78 would give a t-statistic of only about 3.3.
2. **No market capitalisation.** True value weights and size deciles are impossible before 2024; traded value is a rough proxy.
3. **No liquidity factor, and no TED-spread tests.**
4. **Thin trading** in Indian small caps biases betas towards zero, even with 3-day returns. Low-beta deciles in the full universe may be full of illiquid shares, which is why the liquid universe is the main one for the investable portfolios.
5. **Shorting is impractical,** so the BAB factor cannot really be traded. The investable result is long-only, so it captures low beta's alpha but not the leveraged Sharpe-ratio gain.
6. **IIMA's factors** are built on their own universe and breakpoints, which differ from ours.
7. **Risk-free rate:** the 2026 rate is unresolved, and financing the levered leg at the T-bill rate flatters it.
8. **Survivorship:** prices include delisted shares, but delisting returns are unknown (see the stress test above). Corporate actions before 2005 are incomplete, which is why the sample starts in 2005.

## 7. Prior Indian evidence to compare against

Agarwalla, Jacob, Varma and Vasudevan (2014), IIMA working paper (SSRN 2464097), report a significant Indian BAB premium. We have only the abstract; the full text would let us compare numbers.
