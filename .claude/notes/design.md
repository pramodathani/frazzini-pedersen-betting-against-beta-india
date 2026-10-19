# Design notes

- Adjusted return = (close + dividend) / (previous close x price factor) - 1, where the price factor is the multiplier that takes old prices to the new share basis. The first version had it inverted; the tests now assert that the error log is empty.
- Symbols are grouped into one share by union-find over symbols and ISINs (data/share_identity.py). Bhavcopies carry ISINs only from June 2011, so older renames cannot be linked.
- Betas use the clean daily matrix, where a return that spans a session the share missed is NaN. Monthly returns use the full matrix, where such returns are kept, so no return is lost.
- BAB weights follow paper eq. 16 with the split at the median beta of the 500 most traded shares; each leg is then scaled to add to one. BAB weights are low/beta_low minus high/beta_high on excess returns, so brahmagupta's zero return on cash is consistent with financing at the risk-free rate (gap 28).
- Value weighting uses median traded value, because market capitalisation is unavailable before 2024.
- The main specification was fixed in plan/india_plan.md before any result. 17 specifications are reported in results/summary.md.
