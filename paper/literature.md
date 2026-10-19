# Literature around Betting Against Beta

Gathered by the literature_scout subagent on 2026-10-19. Many publisher pages blocked fetching, so several findings below come only from abstracts or snippets and are marked **unverified**. Nothing here is cited in results until it is read in full.

## Replications and critiques

| Paper | What it says | Status |
|---|---|---|
| Novy-Marx and Velikov (2022), Betting against betting against beta, JFE 143(1), 80-106, https://ideas.repec.org/a/eee/jfinec/v143y2022i1p80-106.html | The authors' preprint snippet says that the paper's first non-standard procedure, rank weighting, "drives BAB's performance". The rest of the argument has not been read. | Snippet only |
| Cederburg and O'Doherty (2016), Does it pay to bet against beta?, JF 71(2), 737-774 | A conditional CAPM with instrumented market risk resolves the beta anomaly. | Abstract snippet |
| Alquist, Frazzini, Ilmanen and Pedersen (2020), Fact and fiction about low-risk investing, SSRN 3539452 | Defends the low-risk effect against the main critiques. | Snippet |
| Bali, Brown, Murray and Tang (2017), A lottery-demand-based explanation of the beta anomaly, JFQA 52(6), 2369-2397 | Lottery demand (MAX, factor FMAX) as an explanation. Whether it removes the BAB alpha is unconfirmed. | Unverified |
| Asness, Frazzini, Gormsen and Pedersen (2020), Betting against correlation, JFE 135(3), 629-652 | Splits beta into volatility and correlation; the BAC factor separates leverage-constraint theories from behavioural ones. | Abstract |
| Schneider, Wagner and Zechner (2020), Low-risk anomalies?, JF 75(5), 2673-2718 | Low-risk anomalies may be compensation for coskewness risk. | Unverified |
| Liu, Stambaugh and Yuan (2018), Absolving beta of volatility's effects, JFE 128(1), 1-15 | The beta anomaly is attributed to idiosyncratic volatility. | Title only, unverified |
| Hong and Sraer (2016), Speculative betas, JF 71(5), 2095-2144 | A model of why high-beta stocks are overpriced; the mechanism was not read. | Unverified |
| Hou, Xue and Zhang (2020), Replicating anomalies, RFS 33(5); Jensen, Kelly and Pedersen (2023), Is there a replication crisis in finance?, JF 78, 2465-2518 | Both cite the paper; their treatment of BAB was not checked. | Unverified |

## Indian evidence

| Study | Sample and finding | Status |
|---|---|---|
| Agarwalla, Jacob, Varma and Vasudevan (2014), Betting against beta in the Indian market, IIMA working paper 2014-07-01, SSRN 2464097. **Full text read** (`paper/AgarwallaJacobVarmaVasudevan2014.pdf`, supplied by the user; 22 pages, printed page numbers) | BSE stocks from Prowess, returns January 1993 to June 2013, BAB measured January 1998 to June 2013 (15.5 years, p.9). Market is the Sensex and the risk-free rate is the 91-day T-bill (p.5). Beta follows Frazzini-Pedersen: 1-year volatility, 5-year correlation of 3-day returns, at least 120 and 750 days, shrinkage 0.6 (pp.5-6); stocks with under 5 years of data get a modified shrinkage (eq. 4, p.7). Rank-weighted BAB (eqs. 5-6, p.7). Table 2 (p.18), equal-weighted: BAB excess return 1.70 a month (significant at 1%), CAPM alpha 1.67, 3-factor 1.35, 4-factor 1.08 (5%), realised beta 0.09, volatility 23.79, Sharpe 0.86; average long $1.32 and short $0.91 (p.9). Decile CAPM alphas fall from -0.44 (P1) to -2.89 (P10), all negative because most small stocks lose; value-weighted P1-P10 4-factor alphas run -0.55 to -1.68. Within small stocks BAB is larger; for growth stocks and for winner and loser groups alpha is not significant (Table 4, p.10). | Read in full. Their universe is all BSE stocks, mostly illiquid small stocks, which is a different universe from our liquid-500 main one |
| Tulsyan, Joshipura and Mishra (2025), Does profitability explain the low-risk anomaly in India?, QREF 104 | NIFTY 500 stocks, 2003-2022. There is no risk-return relation rather than an inverted one; controlling for profitability weakens the anomaly but does not remove it. | Abstract |
| Sehgal, Rakhyani and Deisting (2022), Does betting against beta strategy work in major Asian markets?, Pacific-Basin Finance Journal 75 | Tests BAB across Asian markets, India included, against a profitability factor. | Results not seen |
| Peswani and Joshipura (2022), Managerial Finance 48(3) | A stock-level low-risk strategy beats sector bets. | Snippet |
| Agarwalla, Jacob and Varma, Returns to low risk investment strategy | Low-volatility stocks earn higher risk-adjusted returns in India. | Snippet |
| NSE Indices: NIFTY100 Low Volatility 30 and NIFTY Alpha Low-Volatility 30 | Volatility is the 1-year standard deviation of daily log returns; Low Vol 30 weights stocks by inverse volatility. These are an investable benchmark for the long-only leg. | Methodology from snippets; no NSE performance figures read |

## AQR data library

AQR's monthly BAB equity factor dataset covers the US and 23 international markets. Whether India is among them is unverified; check the file's column headers before using it.

## What this means for our study

1. Report rank-weighted (as in the paper), equal-weighted and value-weighted constructions side by side, because Novy-Marx and Velikov show construction drives much of BAB.
2. Measure the long-only low-beta leg after costs against the NIFTY 500 TRI, and compare it with NIFTY100 Low Volatility 30.
3. Compare with Agarwalla et al. (2014) once we have their numbers.
