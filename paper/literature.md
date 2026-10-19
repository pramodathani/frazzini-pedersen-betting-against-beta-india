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
| Agarwalla, Jacob, Varma and Vasudevan (2014), Betting against beta in the Indian market, IIMA working paper 2014-07-01, https://www.iima.ac.in/publication/betting-against-beta-indian-market; also a chapter in The Financial Landscape of Emerging Economies (Springer, 2020) | A Frazzini-Pedersen BAB factor earns significant positive returns in India that dominate the size, value and momentum factors. | Abstract only; this is the closest prior study, and we should get its full text to compare numbers |
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
