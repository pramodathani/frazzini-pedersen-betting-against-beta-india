# Betting Against Beta in India

This study replicates Frazzini and Pedersen (2014), *Betting Against Beta*, Journal of Financial Economics 111(1), 1-25, on shares listed on the National Stock Exchange of India. It builds the beta-sorted portfolios and the betting-against-beta (BAB) factor of the paper's equity tables for February 2008 to September 2026 (224 months), then tests long-only low-beta portfolios an Indian investor could hold, after Indian trading costs and against the NIFTY 500 total-return index.

**In one line:** low-beta shares did earn more risk-adjusted return than high-beta shares in India, as the paper says, but the BAB factor's size depends on tiny, thinly traded shares that nobody can short: across all shares it earns 0.79% a month (Newey-West t 3.37, 0.63% after costs), across the 500 most traded shares only 0.35% (t 1.63).

*A chart and an interactive companion page come at the Companion site stage.*

## Headline results

Monthly returns in excess of the risk-free rate, 224 months, t-statistics Newey-West. Full tables: [`results/summary.md`](results/summary.md).

| Portfolio | Before costs | t | After costs | t | Worst drawdown after costs |
|---|---|---|---|---|---|
| BAB, all shares with a beta (rank weighted, as the paper) | 0.79% | 3.37 | 0.63% | 2.70 | -28.9% |
| BAB, 500 most traded shares | 0.35% | 1.63 | 0.27% | 1.25 | -31.1% |
| BAB, equal weights (all shares) | 0.60% | 3.71 | 0.43% | 2.69 | -21.1% |
| BAB, traded-value weights, 2 size x 3 beta (paper Table B9) | 0.33% | 1.47 | 0.13% | 0.58 | -38.6% |
| Paper, US 1926-2012 (Table III, p.41) | 0.70% | 7.12 | not reported | | |

Long-only, against the NIFTY 500 total-return index (10.3% a year, worst drawdown -51.5%):

| Portfolio | Annual return after costs | Worst drawdown | Excess over NIFTY 500 | Beta |
|---|---|---|---|---|
| Lowest-beta decile of the 500 most traded, monthly rebalance | 14.1% | -42.4% | 3.8% a year (t 1.12) | 0.70 |
| Same, rebalanced every 12 months (the best of 17 specifications, so treat with suspicion) | 16.6% | -39.1% | 6.3% a year (t 2.07) | 0.70 |
| NIFTY100 Low Volatility 30 TRI | 13.7% | -38.5% | 3.4% a year (t 1.10) | 0.72 |

## What the Indian data says

1. **The beta-return slope is flat or inverted, as in the paper.** Among the 500 most traded shares, realised betas run from 0.70 to 1.74 across deciles, and the CAPM alpha falls from +0.41% a month for the lowest-beta decile to -0.45% for the highest. The paper's US numbers are +0.52% and -0.10%.
2. **BAB across all shares is significant, across the liquid 500 it is not.** The rank-weighted BAB earns 0.79% a month before costs over all shares (t 3.37), close to the paper's 0.70%, but 0.35% (t 1.63) over the 500 most traded.
3. **Half of the all-shares BAB comes from the least traded half of shares.** Dropping them cuts it from 0.79% to 0.38% a month (t 1.84). The low-beta leg there is full of thinly traded shares whose measured betas are biased down by stale prices, so part of the premium is an illiquidity premium, not a funding-constraint one.
4. **Weighting matters, as Novy-Marx and Velikov argued for the US.** BAB with traded-value weights earns 0.33% (t 1.47) against 0.79% with rank weights. Equal weights land in between at 0.60%.
5. **Costs take about a fifth of the all-shares BAB and a quarter of the liquid one.** Net of costs the BAB earns 0.63% (t 2.70) and 0.27% (t 1.25). The shorts cannot be held overnight in cash shares in India, and no borrowing fee is charged, so these are paper numbers.
6. **Delistings are a real uncertainty.** NSE files do not say what holders got when a share was delisted. If every share that stops trading loses everything, the all-shares BAB falls from 0.79% to 0.66% (t 2.81) before costs.
7. **Not stable over time.** In three equal subperiods the liquid-500 BAB earns 0.47%, 0.88% and -0.29% a month, and is negative in the last six years. The all-shares BAB is positive in all three (0.65%, 0.82%, 0.89%).
8. **The long-only version is the practical result.** The lowest-beta decile of the 500 most traded shares beats the NIFTY 500 TRI by 3.8% a year after costs with a beta of 0.70 and a smaller worst drawdown, but the excess is not statistically significant over 18 years (t 1.12). That is no better than NSE's own low-volatility indices (3.4% a year).

## The paper in brief

Some investors cannot borrow, so they hold high-beta assets instead of leveraging the market, which bids high-beta assets up and makes their risk-adjusted returns low. A factor that is long leveraged low-beta assets and short high-beta assets, scaled to zero beta, should therefore earn a positive return. Frazzini and Pedersen find it does in US stocks since 1926 (Sharpe ratio 0.78), in 19 other developed markets, in Treasuries, credit and futures. The paper's own summary is in [`paper/summary.md`](paper/summary.md).

## What was changed for India, and why

| Item | Paper | India | Why |
|---|---|---|---|
| Universe | All CRSP common stocks | Every NSE share (EQ, BE, BZ), delisted shares included, with funds, ETFs and rights removed; and the 500 most traded as the liquid universe | No index membership history; thin micro-caps give unreliable betas |
| Decile cut points | NYSE | The 500 most traded shares | Plays the NYSE's role |
| Dates | 1926 to 2012 | Returns from 2005, portfolios 2008-02 to 2026-09 | Corporate actions are complete from 2005; the first beta needs 750 days |
| Market | CRSP value-weighted index | NIFTY 500 total-return index | A broad value-weighted Indian index |
| Risk-free rate | US T-bill | IIMA's RF (RBI 91-day T-bill) to 2025-12, RBI auction yields after | The 2026 rate differs from IIMA's method by up to 0.04 points a month |
| Factors | Fama-French, momentum, liquidity | IIMA SMB, HML, WML | No Indian liquidity factor |
| Size | Market cap | Median daily traded value | Market cap is unavailable before 2024 |
| Short selling | Free | Not possible overnight in most cash shares, so BAB is a research factor | No borrowing fee charged |
| Costs | None | brahmagupta delivery costs plus 0.10% (liquid) or 0.30% (all shares) impact a side | House rules |

The full plan is in [`plan/india_plan.md`](plan/india_plan.md).

## Data

NSE bhavcopies (daily, 1995 to 16 October 2026, delisted shares included), NSE corporate actions (complete from 2005), the NIFTY 500 and two NIFTY low-volatility total-return indices, IIMA's factors and RBI T-bill auctions, and UBI daily prices as a cross-check. Raw data is not published; [`data/README.md`](data/README.md) lists every file and its catches.

## Caveats

- **17 specifications were tried:** the main one, ten variants, the equal-weighted and value-weighted BAB, BAB within size groups and within volatility groups, and 3- and 12-month holds. The main specification was fixed before any result was seen. With a Bonferroni correction for 17 tests, |t| must exceed about 2.98, and only the all-shares BAB before costs passes.
- **224 months, not 1,000.** A Sharpe ratio of 0.78 would give a t-statistic near 3.4 over this sample, against the paper's 7.1.
- **No borrowing cost and no short-selling constraint** are modelled for the BAB's short leg.
- **Symbols are linked across renames by ISIN** where the bhavcopies carry one (from about 2011). Older renames that never carry an ISIN look like delistings.
- **Rights issues are not adjusted;** 996 daily returns beyond -50% or +100% (of 8.2 million) were set to zero and logged.
- **Factor alphas cover 215 months,** because IIMA's factors end in December 2025.
- **12-month holds keep weight on shares that stop trading** until the next rebalance (up to 2.6% of the portfolio), earning nothing.
- **Reviewed twice** by an adversarial reviewer; findings and fixes are in [`results/review/`](results/review/) and [`results/review2/`](results/review2/).

## Reproducing the results

```
python3.14 -m venv .venv
.venv/bin/pip install -e ".[test]"
.venv/bin/pip install -e /path/to/brahmagupta
.venv/bin/python -m frazzini_pedersen_india.data.bhavcopy_reader data/derived/prices_2003.parquet 2003 data/external/earlier_bhavcopy_raw data/nse/bhavcopy_raw
.venv/bin/python -m frazzini_pedersen_india.scripts.build_returns data
.venv/bin/python -m frazzini_pedersen_india.scripts.build_betas data
.venv/bin/python -m frazzini_pedersen_india.scripts.run_main data results
.venv/bin/python -m frazzini_pedersen_india.scripts.run_tables data results
.venv/bin/python -m frazzini_pedersen_india.scripts.run_variants data results
.venv/bin/python -m frazzini_pedersen_india.scripts.run_subperiods results
.venv/bin/python -m frazzini_pedersen_india.scripts.run_benchmarks data results
.venv/bin/python -m frazzini_pedersen_india.scripts.write_summary results
.venv/bin/pytest
```

The raw data must be fetched first; see `data/README.md`.

## Repository layout

```
src/frazzini_pedersen_india/
    data/       bhavcopy reader, corporate actions, returns, share filter and identity, market data, downloaders
    bab/        beta estimator, portfolios, weights, scoring, stress tests
    scripts/    one command-line step each
tests/          unit tests on made-up data, no network
results/        tables as CSV and summary.md
paper/          the paper's record, summary and literature notes (PDFs are not in git)
plan/           the approved plan for India
data/           README only; data is git-ignored
```

## Citation

See `CITATION.cff`, and cite the original paper: Frazzini, A., and Pedersen, L. H. (2014). Betting against beta. *Journal of Financial Economics*, 111(1), 1-25. https://doi.org/10.1016/j.jfineco.2013.10.005
