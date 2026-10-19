# Results: Betting Against Beta on NSE shares

Holding months 2008-02 to 2026-09 (224 months). Returns are monthly percent in excess of the risk-free rate. t is the Newey-West t-statistic. Gross is before trading costs and net is after brahmagupta delivery costs (STT, stamp duty, exchange and SEBI charges, GST) plus market impact of 0.10% a side for the liquid universe and 0.30% for the full universe. The paper figures are its Table III, US stocks 1926-2012 (manuscript p.41). Alphas against IIMA factors use the 215 months to December 2025.

## Beta deciles (the 500 most traded shares), gross of costs

| Decile | Excess return | t | CAPM alpha | t | 4-factor alpha | t | Realised beta | Volatility % | Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 0.75 | 2.02 | 0.41 | 2.55 | 0.41 | 3.37 | 0.70 | 16.4 | 0.55 |
| P2 | 0.64 | 1.24 | 0.16 | 0.92 | 0.18 | 1.55 | 0.97 | 22.1 | 0.35 |
| P3 | 0.81 | 1.44 | 0.28 | 1.68 | 0.35 | 2.46 | 1.07 | 24.2 | 0.40 |
| P4 | 0.77 | 1.29 | 0.19 | 0.98 | 0.30 | 2.27 | 1.17 | 26.9 | 0.34 |
| P5 | 0.64 | 1.04 | 0.02 | 0.09 | 0.13 | 0.95 | 1.26 | 28.8 | 0.27 |
| P6 | 0.94 | 1.39 | 0.29 | 1.28 | 0.38 | 2.59 | 1.31 | 30.4 | 0.37 |
| P7 | 0.83 | 1.16 | 0.11 | 0.42 | 0.10 | 0.65 | 1.43 | 33.3 | 0.30 |
| P8 | 0.75 | 1.03 | 0.02 | 0.07 | 0.04 | 0.27 | 1.47 | 34.4 | 0.26 |
| P9 | 0.57 | 0.75 | -0.21 | -0.65 | -0.22 | -1.13 | 1.57 | 37.1 | 0.18 |
| P10 | 0.41 | 0.49 | -0.45 | -1.10 | -0.33 | -1.39 | 1.74 | 41.9 | 0.12 |

Paper, Table III (US): P1 excess 0.91 (t 6.37), CAPM alpha 0.52, realised beta 0.67, Sharpe 0.70; P10 excess 0.97 (t 2.55), CAPM alpha -0.10, realised beta 1.85, Sharpe 0.28.

## Beta deciles (every share with a beta, cut points from the 500 most traded), gross of costs

| Decile | Excess return | t | CAPM alpha | t | 4-factor alpha | t | Realised beta | Volatility % | Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 1.19 | 2.27 | 0.77 | 2.51 | 0.67 | 3.19 | 0.86 | 23.9 | 0.60 |
| P2 | 1.05 | 1.75 | 0.51 | 1.91 | 0.43 | 2.95 | 1.07 | 27.1 | 0.46 |
| P3 | 1.15 | 1.79 | 0.57 | 2.00 | 0.52 | 3.38 | 1.16 | 28.6 | 0.48 |
| P4 | 1.23 | 1.86 | 0.61 | 2.05 | 0.59 | 4.07 | 1.24 | 30.6 | 0.48 |
| P5 | 1.15 | 1.68 | 0.51 | 1.64 | 0.45 | 3.15 | 1.28 | 31.5 | 0.44 |
| P6 | 0.98 | 1.35 | 0.31 | 0.96 | 0.30 | 2.49 | 1.35 | 33.2 | 0.35 |
| P7 | 0.87 | 1.17 | 0.16 | 0.46 | 0.11 | 0.77 | 1.44 | 35.1 | 0.30 |
| P8 | 0.77 | 1.03 | 0.05 | 0.14 | -0.01 | -0.10 | 1.44 | 35.4 | 0.26 |
| P9 | 0.66 | 0.83 | -0.10 | -0.28 | -0.13 | -0.77 | 1.53 | 37.4 | 0.21 |
| P10 | 0.45 | 0.54 | -0.38 | -0.91 | -0.31 | -1.29 | 1.68 | 41.0 | 0.13 |

## BAB factor

| Portfolio | Costs | Excess return | t | CAPM alpha | 4-factor alpha | t | Realised beta | Volatility % | Sharpe | Worst drawdown % | Turnover per month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bab_full | gross | 0.79 | 3.37 | 0.76 | 0.63 | 3.36 | 0.06 | 10.8 | 0.87 | -26.1 | 0.38 |
| bab_full | net | 0.63 | 2.70 | 0.60 | 0.48 | 2.52 | 0.06 | 10.8 | 0.70 | -28.9 | 0.38 |
| bab_liquid | gross | 0.35 | 1.63 | 0.40 | 0.36 | 2.15 | -0.10 | 10.5 | 0.40 | -27.7 | 0.38 |
| bab_liquid | net | 0.27 | 1.25 | 0.32 | 0.28 | 1.67 | -0.11 | 10.5 | 0.31 | -31.1 | 0.38 |
| bab_full_equal | gross | 0.60 | 3.71 | 0.58 | 0.49 | 3.74 | 0.05 | 7.5 | 0.96 | -17.9 | 0.40 |
| bab_full_equal | net | 0.43 | 2.69 | 0.41 | 0.33 | 2.50 | 0.04 | 7.5 | 0.70 | -21.1 | 0.40 |
| bab_liquid_equal | gross | 0.19 | 1.16 | 0.22 | 0.22 | 1.70 | -0.06 | 7.6 | 0.29 | -26.4 | 0.39 |
| bab_liquid_equal | net | 0.10 | 0.64 | 0.14 | 0.14 | 1.06 | -0.07 | 7.6 | 0.16 | -31.2 | 0.39 |
| bab_full_value | gross | 0.33 | 1.47 | 0.46 | 0.28 | 1.25 | -0.25 | 13.7 | 0.29 | -35.1 | 0.49 |
| bab_full_value | net | 0.13 | 0.58 | 0.26 | 0.08 | 0.34 | -0.25 | 13.7 | 0.11 | -38.6 | 0.49 |
| bab_liquid_value | gross | 0.29 | 1.25 | 0.42 | 0.25 | 1.10 | -0.27 | 14.2 | 0.25 | -35.4 | 0.51 |
| bab_liquid_value | net | 0.18 | 0.78 | 0.32 | 0.14 | 0.62 | -0.27 | 14.2 | 0.15 | -39.0 | 0.51 |

Paper, Table III (US, rank weighted): excess 0.70 (t 7.12), 4-factor alpha 0.55 (t 5.59), realised beta -0.06, volatility 10.7, Sharpe 0.78, $1.40 long and $0.70 short (p.19). Indian bab_full holds on average $1.16 long and $0.73 short. Agarwalla et al. (2014, BSE, 1998-2013, equal-weighted deciles, rank-weighted BAB): excess 1.70, 4-factor alpha 1.08, Sharpe 0.86.

Value-weighted rows weight by median traded value, not market capitalisation, which is unavailable before 2024. They follow the paper's Table B9 construction (2 size x 3 beta groups).

## Legs of the BAB factor, each scaled to beta 1 (paper Table B1)

| Leg | Costs | Excess return | t | 4-factor alpha | t |
|---|---|---|---|---|---|
| full_low_leg_scaled | gross | 1.48 | 2.01 | 0.82 | 3.86 |
| full_low_leg_scaled | net | 1.39 | 1.89 | 0.73 | 3.46 |
| full_high_leg_scaled | gross | 0.69 | 1.09 | 0.18 | 1.18 |
| full_high_leg_scaled | net | 0.63 | 1.00 | 0.13 | 0.81 |
| liquid_low_leg_scaled | gross | 0.93 | 1.54 | 0.47 | 3.81 |
| liquid_low_leg_scaled | net | 0.89 | 1.47 | 0.43 | 3.47 |
| liquid_high_leg_scaled | gross | 0.58 | 0.96 | 0.11 | 0.75 |
| liquid_high_leg_scaled | net | 0.55 | 0.91 | 0.08 | 0.55 |

Paper Table B1 (US): low-beta leg alpha 0.36, high-beta leg alpha -0.01.

## BAB within size groups, by median traded value, full universe (paper Table B3)

| Group (1 low to 5 high) | Gross excess | t | 4-factor alpha | t | Net excess | Net t |
|---|---|---|---|---|---|---|
| Q1 | 1.05 | 3.02 | 0.79 | 2.70 | 0.81 | 2.34 |
| Q2 | 0.89 | 4.17 | 0.75 | 4.00 | 0.64 | 2.99 |
| Q3 | 0.53 | 2.65 | 0.44 | 2.25 | 0.28 | 1.41 |
| Q4 | 0.19 | 0.94 | 0.17 | 0.91 | -0.02 | -0.09 |
| Q5 | 0.46 | 1.86 | 0.41 | 1.90 | 0.31 | 1.25 |

## BAB within idiosyncratic volatility groups, full universe (paper Table B5)

| Group (1 low to 5 high) | Gross excess | t | 4-factor alpha | t | Net excess | Net t |
|---|---|---|---|---|---|---|
| Q1 | 0.54 | 2.10 | 0.51 | 2.06 | 0.29 | 1.14 |
| Q2 | 0.59 | 2.53 | 0.48 | 2.45 | 0.20 | 0.84 |
| Q3 | 0.87 | 2.59 | 0.57 | 2.08 | 0.42 | 1.27 |
| Q4 | 1.20 | 3.00 | 0.85 | 2.70 | 0.76 | 1.92 |
| Q5 | 0.49 | 1.17 | 0.06 | 0.17 | 0.19 | 0.46 |

Residual volatility here is the one-year market-model residual of daily returns, an approximation of the paper (p.61).

## Three subperiods, gross (paper Table B4)

| Portfolio | Months | Excess return | t |
|---|---|---|---|
| bab_full | 2008-02 to 2014-03 | 0.65 | 1.65 |
| bab_liquid | 2008-02 to 2014-03 | 0.47 | 1.11 |
| liquid_D1 | 2008-02 to 2014-03 | 0.55 | 0.64 |
| full_D1 | 2008-02 to 2014-03 | 0.62 | 0.64 |
| bab_full | 2014-04 to 2020-05 | 0.82 | 3.20 |
| bab_liquid | 2014-04 to 2020-05 | 0.88 | 2.57 |
| liquid_D1 | 2014-04 to 2020-05 | 0.66 | 1.60 |
| full_D1 | 2014-04 to 2020-05 | 0.52 | 0.86 |
| bab_full | 2020-06 to 2026-09 | 0.89 | 1.87 |
| bab_liquid | 2020-06 to 2026-09 | -0.29 | -1.12 |
| liquid_D1 | 2020-06 to 2026-09 | 1.05 | 2.12 |
| full_D1 | 2020-06 to 2026-09 | 2.41 | 2.60 |

## Robustness variants, monthly excess return % (Newey-West t)

| Variant | bab_full gross | bab_full net | bab_liquid gross | bab_liquid net | liquid_D1 net |
|---|---|---|---|---|---|
| main | 0.79 (3.37) | 0.63 (2.70) | 0.35 (1.63) | 0.27 (1.25) | 0.70 (1.88) |
| liquid_300 | 0.79 (3.29) | 0.64 (2.64) | 0.40 (1.63) | 0.32 (1.31) | 0.77 (2.02) |
| liquid_1000 | 0.78 (3.42) | 0.62 (2.73) | 0.53 (2.78) | 0.45 (2.35) | 0.83 (1.87) |
| drop_least_traded_half | 0.38 (1.84) | 0.22 (1.08) | 0.34 (1.55) | 0.26 (1.17) | 0.71 (1.84) |
| delay_one_session | 0.82 (3.62) | 0.66 (2.94) | 0.49 (2.47) | 0.41 (2.07) | 0.53 (1.50) |
| delisting_-1.0 | 0.66 (2.81) | 0.50 (2.14) | 0.30 (1.37) | 0.22 (1.01) | 0.58 (1.52) |
| delisting_-0.3 | 0.75 (3.20) | 0.59 (2.53) | 0.33 (1.55) | 0.25 (1.17) | 0.67 (1.77) |
| correlation_3_year | 0.86 (3.22) | 0.70 (2.60) | 0.34 (1.65) | 0.26 (1.25) | 0.49 (1.39) |
| correlation_1_year | 1.05 (3.13) | 0.83 (2.50) | 0.44 (1.97) | 0.34 (1.51) | 0.38 (0.93) |
| no_shrinkage | 1.17 (2.89) | 1.02 (2.51) | 0.59 (2.01) | 0.51 (1.74) | 0.70 (1.88) |
| five_day_overlap | 0.69 (3.33) | 0.54 (2.59) | 0.34 (1.63) | 0.26 (1.25) | 0.68 (1.87) |

Specifications tried: 17, namely the main one and ten variants above, and the equal-weighted BAB, the value-weighted BAB, BAB within size groups, BAB within volatility groups, and holding the long-only portfolios for 3 and for 12 months. With Bonferroni correction for 17 tests the two-sided 5% threshold is |t| of about 2.98, and only the gross full-universe BAB passes. The main specification was fixed in plan/india_plan.md before any result was seen.

## Long-only low-beta portfolios against the NIFTY 500 TRI

| Portfolio | Costs | Annual return % | Volatility % | Worst drawdown % | Excess over NIFTY 500 % a year | t | CAPM alpha % a month | t | Beta |
|---|---|---|---|---|---|---|---|---|---|
| NIFTY 500 TRI | index | 10.3 | 21.2 | -51.5 | 0.0 |  |  |  | 1.00 |
| NIFTY100 Low Volatility 30 TRI | index | 13.7 | 16.5 | -38.5 | 3.4 | 1.10 | 0.32 | 2.65 | 0.72 |
| NIFTY Low Volatility 50 TRI | index | 13.7 | 16.8 | -39.8 | 3.4 | 1.34 | 0.31 | 3.10 | 0.76 |
| liquid_D1 | gross | 14.8 | 16.4 | -42.0 | 4.4 | 1.38 | 0.41 | 2.94 | 0.70 |
| liquid_D1 | net | 14.1 | 16.4 | -42.4 | 3.8 | 1.12 | 0.36 | 2.58 | 0.70 |
| liquid_D1_every_3_months | gross | 13.7 | 16.2 | -43.8 | 3.4 | 0.94 | 0.33 | 2.41 | 0.69 |
| liquid_D1_every_3_months | net | 13.3 | 16.2 | -44.1 | 2.9 | 0.77 | 0.30 | 2.17 | 0.69 |
| liquid_D1_every_12_months | gross | 16.8 | 16.4 | -39.0 | 6.5 | 2.17 | 0.56 | 3.94 | 0.70 |
| liquid_D1_every_12_months | net | 16.6 | 16.4 | -39.1 | 6.3 | 2.07 | 0.54 | 3.80 | 0.70 |
| bab_low_leg | gross | 13.6 | 20.5 | -52.7 | 3.3 | 1.82 | 0.27 | 2.18 | 0.92 |
| bab_low_leg | net | 13.1 | 20.5 | -53.0 | 2.8 | 1.54 | 0.24 | 1.89 | 0.92 |
| bab_low_leg_every_3_months | gross | 13.2 | 20.4 | -53.2 | 2.9 | 1.58 | 0.25 | 1.98 | 0.92 |
| bab_low_leg_every_3_months | net | 12.9 | 20.4 | -53.4 | 2.6 | 1.39 | 0.22 | 1.78 | 0.92 |
| full_D1 | gross | 19.3 | 23.8 | -46.3 | 8.9 | 2.28 | 0.77 | 2.55 | 0.86 |
| full_D1 | net | 17.7 | 23.8 | -47.1 | 7.4 | 1.92 | 0.66 | 2.18 | 0.86 |
