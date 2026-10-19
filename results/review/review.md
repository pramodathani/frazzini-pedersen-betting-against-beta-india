# Backtest review: bab-pilot (Frazzini-Pedersen 2014 BAB on NSE)
Reviewer: backtest_reviewer, 2026-10-19. Scripts in /tmp/bab_review/.

## 0. What was tested
FP2014 Table 3/4-style beta deciles and BAB factor. NSE shares (bhavcopy, ISIN INE, ETFs/rights removed), formation month-ends 2008-01..2026-08, holding 2008-02..2026-09 (224 months).
Beta: 0.6*(corr 5y overlapping 3-day log, vol 1y daily log) + 0.4, vs NIFTY 500 TRI. Liquid = top 500 by 252-day median traded value.
BAB = low/bL - high/bH, rank weights; backtested with brahmagupta Backtest on excess returns (IIMA RF to 2025-12, T-bill after), DeliveryCosts impact 0.3% (full) / 0.1% (liquid).
Headline: bab_full gross 0.757%/m NW t 3.34, net 0.600%; bab_liquid 0.354% t 1.66; liquid_D1 0.736%.

## 1. Tests
pytest: 36 passed.

## 2. Reproduction
Rebuilt the schedule with WeightSchedule and Backtest from /tmp/bab_review/common.py: bab_full 0.757%/m t 3.34, net 0.600%; bab_liquid 0.354% t 1.66; liquid_D1 0.736%; full_D1 1.127%. All match results/main_summary.csv exactly. Turnover column = bought+sold.

## 3. Survivorship / stale data
- bab_full: on average 16.9 held shares per month (abs weight 2.98% of book, max 7.5%) had no trade in the 31 days before formation, yet carry a beta (beta_estimator.py only needs 120 valid days in 252, with no recency check). Unpriced abs weight 3.59%, net +1.13% (long side mostly).
- 439 ISINs carry >1 symbol (506 old symbols): renames break history, the old symbol looks delisted and the new one needs 750 3-day obs before a beta.
- Delisting stress (-100% excess in month after the last monthly return), gross:
  all exits: bab_full 0.757->0.595 (t 2.61); bab_liquid 0.354->0.304 (1.38); full_D1 1.127->0.777 (1.54); liquid_D1 0.736->0.530 (1.40); bab_low_leg 0.730->0.538
  renames (ISIN reused) excluded: bab_full 0.623 (t 2.73); bab_liquid 0.298 (1.34); full_D1 0.855 (1.70); liquid_D1 0.593 (1.57)
- Monthly returns >300%: 14, < -80%: 4. Top: FTCPOF3YDV 2008-01 +1676% (a Franklin fund unit, not caught by ShareClassifier), GANGOTRI 2018-07 +733%, FTCPOF3YGR 2008-01 +608%, BLUECHIP 2018-10 +550%, GREENFIRE 2018-05 +450%, VISESHINFO 2021-12, FCSSOFT 2018-02, METKORE 2020-06, ESSAROIL 2007-11, PRAKASHSTL 2020-05... mostly penny-stock price ticks. Of top 20 only METKORE (+1.17pp), PRAKASHSTL (+1.11pp), UNITY (-0.85), ANTGRAPHIC, FCSSOFT, ICSA carry bab_full weight; small vs 224 months.
- 108 held symbols never carry an ISIN (pre-2011 names e.g. BAJAJAUTO, ARVINDMILL): fund screen for them relies on the name pattern only.

## 4. Micro-cap / illiquidity
- Drop lowest-traded-value half at each formation (cut points still from top-500): bab_full gross 0.757 -> 0.357%/m (t 1.72), net 0.202% (t 0.97); full_D1 1.127 -> 0.716 (t 1.82). => about half the full-universe BAB comes from the least-traded half.
- Cross-sectional winsorising monthly returns at 0.5/99.5%: bab_full 0.736 (t 3.30), bab_liquid 0.391, full_D1 1.059, liquid_D1 0.778. Outliers are not the driver.
- Requiring a trade in the formation month: bab_full 0.785 (t 3.39), unpriced weight 3.6% -> 0.6%; bab_liquid 0.380. Stale shares are not the driver.

## 5. Code checks
- Beta hand-recomputed (pandas, 2015-06-30) for INFY 0.708059, HINDUNILVR 0.726704, SUZLON 1.830973: identical to betas_month_end. Windows end at the formation session inclusive; 252/1260 sessions; min 120 daily / 750 three-day obs. No look-ahead.
- full_D1 and bab_full weights for formation 2015-06 recomputed by hand: max abs diff 0.0. Ex-ante beta of bab_full 5e-17; net long 0.47.
- Rank-weight legs: split at the liquid median rank (632.5) not the mean rank (636.0), so legs sum to 0.989/1.011, not 1 as the docstring in portfolio_builder.py says. BAB weights are scale-invariant (low/beta_L), so harmless; leg betas 0.880/1.503 vs 0.881/1.504 with the paper formula.
- One month by hand: bab_full 2015-07 = sum(w*excess) 0.0204585 = Backtest = results csv. INFY 2015-07 monthly 9.4174% = compounded dailies.
- Weight sums: deciles and bab_low_leg 1.000 every month; bab_low_leg_levered 0.95-1.37; bab_full 0.31-0.55 (correct for excess-return BAB). periods_with_unpriced_weight = 224 of 224 (mean abs 3.6%), see sec 3.
- Labelling: weights from month-end t are labelled t+1 (weight_schedule.py build), returns, RF and IIMA factors all PeriodIndex by calendar month: aligned.

## 6. Costs
Turnover column = bought+sold (0.38/m for bab_full on gross ~1.9). Base: impact 0.3% full, 0.1% liquid; no unverified rates.
run_backtest at impact 0.6% (results/review/bab_full_impact_0.006): net 0.600 -> 0.49%/m, NW t 2.64 -> 2.14; annual costs 3.25%.
Short side: DeliveryCosts charges STT/impact on shorts, but no securities-lending fee, and overnight cash shorts of micro-caps are not available in India: net BAB is a paper number.

## 7. Subperiods / snooping
bab_full halves 0.713 (t 2.29) / 0.801 (t 2.44); quarters 0.545 (1.06), 0.880 (2.99), 1.645 (3.24), -0.042 (-0.13) from 2022-02.
bab_liquid halves 0.533 (1.58) / 0.175 (0.69); last quarter -0.287.
liquid_D1 halves 0.65 (1.03) / 0.82 (2.12).
Main spec pre-registered in plan/india_plan.md l.76; ~20 variants planned. Bonferroni 20 two-sided 5% needs |t|>3.02: bab_full gross 3.34 passes, but net (2.64), double impact (2.14), delisting stress (2.61) and top-half liquidity (1.72) do not.

## 8. Paper (Table III, US 1926-2012)
BAB 0.70 (t 7.12), Sharpe 0.78 vs bab_full 0.76 (3.34), Sharpe 0.87; bab_liquid 0.35 (1.66), Sharpe 0.41. P1 0.91 vs full_D1 1.13 / liquid_D1 0.74. t gap is mostly 224 vs ~1,000 months. The full-universe level matches the US, but half of it comes from the least-traded half (low leg median traded value about half the high leg's), consistent with non-synchronous trading pushing illiquid betas down: an illiquidity tilt, not clean BAB.

## Verdict: sound with caveats
Code is correct (no look-ahead, weights and returns reproduce by hand). The headline bab_full figure depends on illiquid shares, on delisting treatment and on costs.
