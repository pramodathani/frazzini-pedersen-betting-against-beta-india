# Second review: bab-pilot (2026-10-19)
Scripts: results/review2/*.py (groups, junctions, recompute, bench, lastmonth). Tests: 51 pass with PYTHONPATH=src. Without it, collection fails because the package is not installed in the gateway venv.

## 1 Fixes (a)-(c)
- symbol_map: 4064 symbols, 3704 groups, 319 multi-symbol groups. Top 15: IBULLSLTD(6: IBWSL,SORILHOLD,IBULISL,YAARII,YAARI), RNAVAL(4: PIPAVAVYD,PIPAVAVDOC,RDEL), DIGISPICE(4), STYRENIX(4: INEABS,STYABS,INEOSSTYRO), ANDHRAPAP(4), PROZONER(4), GVT&D(4: AREVAT&D,ALSTOMT&D,GET&D), GVPIL(4), CPCAP, VEDL(SESAGOA,SSLT), DHANI(IBSEC,IBVENTURES), DVL, ZFCVINDIA(WABCO), DELPHIFX(WEIZFOREX,EBIXFOREX), LANDSMILL(EXCELINFO,EXCEL). All are plausible rename chains.
- Overlapping trading dates within a group in prices_2003: 0 group-days.
- 360 junctions. Only 2 have a price ratio >3x: KRITIIND->KRITI (2,468-day gap, 14.6x) and HYDROS&S->KINGFA (656 days, 3.3x). daily_returns sets the return to 0 on both gap days, so no spurious return.
- The "latest symbol" label uses future information, but it is only a name. Returns are unaffected.
- traded_in_month uses only the formation month (return_panel.py:117-135). WeightSchedule.build filters on it at the formation date, so there is no look-ahead.
- bab_weights legs are normalised to 1 each and the split handles ties. OK.
## 2 DelistingStress
758 shares charged, each exactly once, in the month after its last return. No charged share has a return in the final month. 447 charges hit held bab_full positions. 5 charges fall in 2026-09, a complete 21-session month. Recomputed bab_full gross/net: -1.0 gives 0.006568/0.005011 and -0.3 gives 0.007478/0.005913. Both match variants_summary exactly.
## 3 RebalanceSchedule
Reproduced turnover: liquid_D1 0.2315 / 0.1508 / 0.0809 (monthly / 3-month / 12-month). Drift months have exactly 0 turnover. Rebalance months are 0.95, and full_D1's are 1.07. Weight sums stay 1.0000.
Turnover is ~1/12 of a near-full replacement, not 1/12 of the monthly figure. That is expected. Not a bug.
Caveat: weights on shares that stop trading are kept (returns fillna 0), so unpriced weight rises to 1.2% (liquid_D1_12) and 2.6% (full_D1_12).
## 4 Value/equal-weighted BAB
These follow the B9 US construction: independent 2x3 sorts, size at the breakpoint-set median, beta at the 30th and 70th percentiles, the average of small and large, and each leg divided by its beta. The equal-weighted version splits at the median. OK.
Caveat: weighting by traded value rather than market cap tilts towards high-turnover shares. Under-specified: the paper's international version uses an 80th-percentile size break with conditional sorts.
## 5 Benchmarks
- NIFTY 500 TRI CAGR from raw month-end levels is 0.103254. This matches the file.
- liquid_D1 gross excess+rf CAGR is 0.147637. This matches.
- BUG: sharpe is computed on total returns. NIFTY 500 gives 0.573 on total versus 0.281 on excess.
- BUG: alpha and beta come from a regression of total on total. liquid_D1 alpha 0.00565 against CAPM alpha 0.00408 in variants_summary. The difference is 0.00157, which is about (1-beta)*rf = 0.305*0.0051.
- Cosmetic: the benchmark's alpha_t against itself is -2.65; it should be NaN.
## Verdict: sound with caveats
