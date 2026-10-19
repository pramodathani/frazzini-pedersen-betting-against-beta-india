# Summary: Frazzini and Pedersen, Betting Against Beta

Version read: the authors' final manuscript dated 10 May 2013 (80 pages; see `README.md`). "p." means the PDF page. Table III and the method pages (pp.16-19) were checked against the page images; the other numbers come from a close reading by the paper_reader subagent, which checked each table against its page image. India does not appear anywhere in the paper.

## Hypothesis

Many investors cannot borrow, so to get more return they buy high-beta assets instead of levering up. That bids high-beta assets up, so the security market line is flatter than the CAPM says (pp.2-3, 7-9). The paper's model (eq. 2, p.8) gives five predictions:

1. **Alpha falls with beta** (Proposition 1, pp.9-10). Required return is r_f + ψ + β·λ (eq. 8), so alpha is ψ(1−β). Sharpe ratios also fall with beta.
2. **A BAB factor earns a positive expected return** (Proposition 2, p.12; eqs. 9-10). The factor is long leveraged low-beta assets and short high-beta assets.
3. **BAB loses when funding constraints tighten** (Proposition 3, pp.12-13).
4. **Funding-liquidity risk compresses betas towards one** (Proposition 4, p.13).
5. **Constrained investors hold higher-beta portfolios** (Proposition 5, p.14).

## Data (equity part)

- **US** (pp.14, 39). CRSP common stocks (share codes 10 and 11), January 1926 to March 2012. Betas are measured against the CRSP value-weighted index, and excess returns are over the T-bill. The paper states no price screen, size screen or delisting treatment.
- **International** (pp.15, 39). Xpressfeed Global: 19 MSCI developed markets, mostly 1989 to 2012. Betas are measured against the local MSCI index. Returns are in US dollars, in excess of the US T-bill.
- **Factors** (p.15). The Fama-French factors SMB and HML plus the momentum factor UMD, all from Ken French's library, and the Pastor-Stambaugh liquidity factor (1968-2011 only). International factors come from Asness and Frazzini (2011).
- **TED spread** (p.16): December 1984 to March 2012.

## Method

**Ex-ante beta.** Beta is estimated as β_TS = ρ·σ_i/σ_m (eq. 14, p.17).
- Volatilities come from 1-day log returns over a 1-year window, with at least 120 trading days.
- Correlation comes from overlapping 3-day log returns over a 5-year window, with at least 750 trading days. The 3-day returns correct for non-synchronous trading.
- If only monthly data are available, the windows are 1 and 5 years, with at least 12 and 36 observations.
- Shrinkage (eq. 15, p.17): β = 0.6·β_TS + 0.4·1. The pooled Vasicek weight would be 0.61 (fn 14). Shrinkage leaves ranks unchanged but sets the leverage of each leg.

**BAB factor** (pp.18-19, eqs. 16-17).
1. Each month, rank stocks by beta measured at the previous month-end, and split them at the median.
2. Weight stocks within each leg by rank: z is the vector of beta ranks, k = 2 / 1′|z − z̄|, w_H = k(z − z̄)⁺ and w_L = k(z − z̄)⁻. Each leg's weights sum to one.
3. Lever each leg to beta one: r_BAB = (r_L − r_f)/β_L − (r_H − r_f)/β_H.
4. Rebalance monthly.

On average the US factor is long $1.40 and short $0.70 (p.19).

**Decile portfolios** (Table III note, p.41). Stocks are sorted on the previous month-end beta into deciles at NYSE breakpoints, equal-weighted and rebalanced monthly.

**Alphas** (p.41). Monthly excess returns are regressed on the market (CAPM), then adding SMB and HML (3-factor), UMD (4-factor) and liquidity (5-factor). "Beta (realized)" is the market loading.

**t-statistics.** Tables III to VIII do not say how they are computed. Table IX uses White standard errors clustered by date (p.47), and Tables X and XI use Newey-West with 60 lags (pp.48-49). Our study will use Newey-West throughout, as ResearchRules.md requires.

## Tables to reproduce for India

### Table III: US equities, 1926-2012 (p.41)

Checked against the page image. Values are monthly %, with t-statistics in parentheses. Volatility and Sharpe ratio are annualised.

| | P1 low | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 high | BAB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Excess return | 0.91 (6.37) | 0.98 (5.73) | 1.00 (5.16) | 1.03 (4.88) | 1.05 (4.49) | 1.10 (4.37) | 1.05 (3.84) | 1.08 (3.74) | 1.06 (3.27) | 0.97 (2.55) | 0.70 (7.12) |
| CAPM alpha | 0.52 (6.30) | 0.48 (5.99) | 0.42 (4.91) | 0.39 (4.43) | 0.34 (3.51) | 0.34 (3.20) | 0.22 (1.94) | 0.21 (1.72) | 0.10 (0.67) | −0.10 (−0.48) | 0.73 (7.44) |
| 3-factor alpha | 0.40 (6.25) | 0.35 (5.95) | 0.26 (4.76) | 0.21 (4.13) | 0.13 (2.49) | 0.11 (1.94) | −0.03 (−0.59) | −0.06 (−1.02) | −0.22 (−2.81) | −0.49 (−3.68) | 0.73 (7.39) |
| 4-factor alpha | 0.40 (6.05) | 0.37 (6.13) | 0.30 (5.36) | 0.25 (4.92) | 0.18 (3.27) | 0.20 (3.63) | 0.09 (1.63) | 0.11 (1.94) | 0.01 (0.12) | −0.13 (−1.01) | 0.55 (5.59) |
| 5-factor alpha | 0.37 (4.54) | 0.37 (4.66) | 0.33 (4.50) | 0.30 (4.40) | 0.17 (2.44) | 0.20 (2.71) | 0.11 (1.40) | 0.14 (1.65) | 0.02 (0.21) | 0.00 (−0.01) | 0.55 (4.09) |
| Beta (ex ante) | 0.64 | 0.79 | 0.88 | 0.97 | 1.05 | 1.12 | 1.21 | 1.31 | 1.44 | 1.70 | 0.00 |
| Beta (realized) | 0.67 | 0.87 | 1.00 | 1.10 | 1.22 | 1.32 | 1.42 | 1.51 | 1.66 | 1.85 | −0.06 |
| Volatility | 15.7 | 18.7 | 21.1 | 23.1 | 25.6 | 27.6 | 29.8 | 31.6 | 35.5 | 41.7 | 10.7 |
| Sharpe ratio | 0.70 | 0.63 | 0.57 | 0.54 | 0.49 | 0.48 | 0.42 | 0.41 | 0.36 | 0.28 | 0.78 |

The pattern to test in India:
- excess returns are roughly flat across deciles, but alphas fall steadily with beta;
- the realised beta rises from 0.67 to 1.85;
- the BAB factor has a Sharpe ratio of 0.78 and a 4-factor alpha of 0.55% a month (t 5.59).

### Table IV: international equities, 1984-2012 (p.42)

| | P1 low | P10 high | BAB |
|---|---|---|---|
| Excess return | 0.63 (2.48) | 0.30 (0.66) | 0.64 (4.66) |
| CAPM alpha | 0.45 (2.91) | 0.00 (−0.01) | 0.64 (4.68) |
| 4-factor alpha | 0.20 (1.42) | −0.16 (−0.59) | 0.30 (2.20) |
| Beta (ex ante) | 0.61 | 1.35 | 0.00 |
| Volatility | 15.0 | 27.1 | 8.1 |
| Sharpe ratio | 0.50 | 0.13 | 0.95 |

The international results are a closer analogue to India than the US ones: a shorter sample, local-index betas, and many countries with few stocks.

### Table V: BAB by country (p.43)

The BAB Sharpe ratio is positive in 18 of the 19 countries. The 4-factor alpha is positive in 13 and significant in 6 (p.22). Low power with few stocks is flagged on p.22. Examples:

| Country | Excess return | 4-factor alpha | Sharpe ratio |
|---|---|---|---|
| Canada | 1.23 (t 5.17) | 0.67 | 1.05 |
| Japan | 0.21 | 0.01 | 0.19 |
| Austria | −0.03 | | −0.02 |

### Robustness tables we can reproduce in India (Appendix B)

**Table B1, factor loadings of the legs (p.66).**
- US low-beta leg: alpha 0.36, market loading 0.67.
- US high-beta leg: alpha −0.01, market loading 1.28.
- BAB loads on HML (0.10) and UMD (0.19).

**Table B2, alternative beta windows (p.67).** In the US, a 3-year or 1-year correlation window gives an excess return of 0.76 (t 7.60) and a Sharpe ratio of 0.83.

**Table B3, within size deciles (p.68).**
- The US BAB alpha is significant in every size decile.
- The US excess return falls from 1.11 (small) to 0.25 (large).

**Table B4, subperiods (p.69).**
- US 1926-45 is insignificant (t 1.00); every other US period is significant.
- This conflicts with the p.4 claim that BAB is significant in every 20-year subperiod.

**Table B5, within idiosyncratic-volatility deciles (p.70).** The US alpha survives; international t-statistics stay below 1.96.

**Table B9, value-weighted BAB (pp.63-64, 74).**
- Construction: 2 size groups × 3 beta groups (30th and 70th percentiles).
- US beta-neutral: excess 0.51 (t 5.22), 4-factor alpha 0.45, Sharpe ratio 0.57.
- US dollar-neutral: excess 0.03 (t 0.20).

Table B9 matters for India: the premium in raw returns comes largely from levering the low-beta leg.

**Table IX, BAB on the TED spread (p.47).**
- Lagged TED: −0.025 (t −5.24).
- Change in TED: −0.019 (t −2.58).
- An Indian analogue would need a domestic funding spread, which is not yet decided.

## Conclusions (pp.33-34)

- High-beta assets have lower alphas and Sharpe ratios in US stocks, in most international markets, and in Treasuries, credit and futures.
- BAB earns large risk-adjusted returns, comparable to value and momentum.
- BAB returns are low when funding tightens.
- Betas are compressed when funding risk is high.
- Constrained investors hold high-beta assets.

## Limitations and ambiguities a replication must settle

1. **No transaction costs or turnover.** The paper reports neither, and funding is tested only through alternative risk-free rates (Table B6, p.71). We must add Indian costs ourselves.
2. **No delisting treatment or screens stated.** The paper does not say how it handles delistings, price or size screens, or missing days.
3. **Returns in the beta estimate.** It is unclear whether the market side uses excess or raw returns. The text says "regressions of excess returns on market excess returns" (p.16) and also "log returns" (p.17).
4. **Standard errors.** The method is not stated for Tables III to VIII.
5. **International details.** The start date is inconsistent: 1989 on p.15 versus 1984 in the captions on pp.42-43. Pooling and decile breakpoints are not specified.
6. **The authors' own caveats.** The sign on the lagged TED spread runs against the model (pp.5, 27). Beta estimation error cannot be fully excluded (p.29). Single-country power is low (p.22).
7. **Typos and mislabels.** p.19 cites "portfolio (8)" where (9)/(17) is meant. p.25 cites "Table VII" for Table VIII. The Table B6 Long/Short headers appear swapped. Table B2 has duplicated rows.

## Implications for India

- **Decile breakpoints.** NYSE breakpoints have no direct analogue. Candidates are NIFTY 500 members or a size cut.
- **History.** The 750-day correlation minimum needs at least 3 years of daily history before a stock can be ranked. With bhavcopies from about 2005, rankings start around 2008 to 2010.
- **Short side.** Shorting cash equities overnight is not possible for most investors in India. The long-short BAB is therefore a research factor only. The investable product is the long-only low-beta leg, levered where possible (for example through NIFTY futures), and measured against the NIFTY 500 TRI.
