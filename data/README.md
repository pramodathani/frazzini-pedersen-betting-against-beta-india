# Data

Everything in this folder except this file is git-ignored. Raw exchange data is never published, only derived results. Fetched on 2026-10-19 (India time); data runs to the 2026-10-16 session.

## Reused from the Jegadeesh and Titman study's raw downloads (read-only)

Only raw downloads were read. That study's code, processed files and results were not.

| Path here | Copied or linked from | Contents | Counts |
|---|---|---|---|
| `external/earlier_bhavcopy_raw` (symlink) | `research/jstor/jegadeesh_and_titman/data/bhavcopy/raw`, the raw folder that study links to | Daily NSE share bhavcopy zips, `{year}/{date}.csv.zip`; old format to 2024-07-05, UDiFF from 2024-07-08; plus `not_available.txt` | 1995-01-02 to 2026-10-06; 242 to 252 files a year from 2005 (2026: 187); 430 dates NSE had no file for |
| `external/earlier_corporate_actions` (symlink) | `.../data/bhavcopy/corporate_actions` | NSE corporate actions JSON per year, complete only from 2005 | 1995 to 2026-10-06; 829 actions in 2005, 1,778 in 2010, 2,208 in 2020, 1,927 in 2025 |
| `nse/bhavcopy_raw/2026/` | that study's `data/nse/bhavcopy_raw/2026`, copied | UDiFF bhavcopies for the sessions after the earlier files end | 8 files, 2026-10-07 to 2026-10-16; 2,949 EQ, BE and BZ shares on the last day |
| `nse/corporate_actions/2026.json` | that study's `data/nse/corporate_actions/2026.json`, copied | 2026 corporate actions refreshed to the last session; replaces the symlinked 2026 file | 1,849 actions, latest ex-date 2026-10-16 |
| `nse/indices/nifty500_tri.json` | that study's `data/nse/nifty500_tri.json`, copied | NIFTY 500 total return index, daily; fetched from niftyindices.com | 7,879 rows, 1995-01-01 to 2026-10-16. `NTR_Value` is filled only from 2015; we use `TotalReturnsIndex` |
| `nse/iima/2025-12_FourFactors_and_Market_Returns_Monthly_SurvivorshipBiasAdjusted.csv` | that study's `data/nse/iima/`, copied | IIMA SMB, HML, WML, MF and RF, monthly returns in percent; RF is from RBI 91-day T-bill auctions | 387 months, 1993-10 to 2025-12; no RF in 1993-10 |

## Downloaded for this study

| Path | Source | Contents | Counts |
|---|---|---|---|
| `nse/indices/nifty100_lowvol30_tri.json` | `POST https://www.niftyindices.com/BackPage/getTotalReturnIndexString`, index name `NIFTY100 LOW VOLATILITY 30`, one request per year | Daily total return index; the earliest rows are back-calculated by NSE | 5,344 rows (starts 2005-12-30); `NTR_Value` is empty |
| `nse/indices/nifty_lowvol50_tri.json` | same, index name `NIFTY LOW VOLATILITY 50` | Daily total return index, back-calculated before launch | 5,660 rows (starts 2003-12-31) |
| `nse/tbill_auctions.csv` | RBI press releases "Treasury Bills: Full Auction Result", `https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=N`, read by `frazzini_pedersen_india.data.tbill_downloader` | Cut-off yield (YTM) of the 91-day bill, one row per auction found | Two or three auctions a month, 2025-10-15 to 2026-10-14 (one in four to five weeks is missed because the scan steps back about 50 releases at a time) |
| `ubi/instruments_nse_equities.parquet` | UBI `export_instruments`, nse / equities | UBI's instrument master | 3,453 instruments |
| `ubi/daily_prices_nse_equities.parquet` | UBI `export_prices`, day candles, adjusted for splits and bonuses but not dividends (`price_factor` column) | Daily candles | 2,943,119 candles, 2,605 symbols, 2019-12-03 to 2026-10-16; 826 of 3,431 requested symbols have no candles; 22 NSETEST symbols were left out |

UBI is used only to cross-check our own adjusted prices from December 2019, because its history is too short for 5-year correlations and it lacks delisted shares and dividends (gaps 1, 2 and 7 in the register).

## Coverage checks

- NIFTY 500 TRI has 5,405 trading days from 2005-01-01. The bhavcopies cover 5,380 of them, and every bhavcopy date is also a TRI date. The 25 days with no bhavcopy are special Saturday and Sunday sessions (budget days, Muhurat and so on), for example 2025-02-01 and 2026-02-01. The Build stage merges each such day into the next session's return.
- None of the dates in `not_available.txt` from 2005 on is a NIFTY 500 TRI trading day, so NSE had no file only on holidays.

## Catches

- **Risk-free rate for 2026.** IIMA's RF stops at 2025-12. For 2026 we take the mean of the 91-day T-bill cut-off yields of the month's auctions and convert it with (1 + y)^(1/12) − 1. Checked against IIMA over 2025-10 to 2025-12: our figures are 0.443, 0.439 and 0.431 percent a month, IIMA's are 0.452, 0.406 and 0.468. They differ by up to 0.04 points, so the series is not identical in method. The two are joined at 2025-12 without adjustment, and risk-adjusted statistics through 2025-12 are the main ones.
- **IIMA releases are recalculated** three times a year, so the release prefix stays in the file name.
- **Low-volatility indices.** Rows before each index's launch are NSE's back-calculations, not investable history.
- **No market capitalisation before 2024.** NSE's PR archive zips exist back to 2010 but hold no MCAP file in 2010 or 2015, so traded value stands in for size (gap 10).
- **Delisted shares are in the bhavcopies** while they traded, so prices have no survivorship bias; the value at delisting is not known.
- **Raw prices are unadjusted,** and NSE does not adjust PREVCLOSE either. The Build stage applies the corporate actions.

## Rebuilding

The bhavcopy and corporate-action files can be refetched with the NSE URLs in the nse-market-data skill; that study's downloader did the same in about an hour. The two index files and the T-bill file are rebuilt with `python -m frazzini_pedersen_india.data.index_downloader data/nse/indices 2026` and `python -m frazzini_pedersen_india.data.tbill_downloader data/nse/tbill_auctions.csv 63804 61400`.
