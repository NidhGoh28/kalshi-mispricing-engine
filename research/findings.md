# Findings log

## 2026-09-22: First live arbitrage check

Ran check_ladders.py against live Kalshi prices.
Result: 7 apparent violations across 511 related groups.
Full output: output_2026-09-22.txt

Examples:
- KXOSCARACTO-27 (Best Actor): sell every outcome, edge 2c
- KXTRUMPAGCOUNT-29 (Trump Attorneys General count): buy every outcome, edge 6c

### Why these are probably not real money

1. Fees: [explain that each outcome is a separate leg and each leg pays a fee,
   so a 6-leg trade with a 2c edge loses money]

2. Capital locked up: [explain the Best Actor example - roughly 498c tied up to
   earn 2c, for about 6 months. Write out the profit = B - 100 derivation.]

3. Might not be real: [mention order book depth, and that the buy-every-outcome
   check only works if the buckets cover every possible outcome]

### What to do next
- Look up Kalshi's exact fee formula and record it here
- Measure edge per dollar locked up per year, not raw edge
- Check depth before calling anything tradable