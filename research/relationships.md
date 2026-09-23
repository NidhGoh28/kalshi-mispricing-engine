# Tracked market groups

## General notes

Two things I had to understand before any of these notes made sense.

First, the buy and sell prices across a whole group almost never add up to
exactly 100. Buying everything usually costs a bit over 100 and selling
everything usually brings in a bit under. That's just the gap between buy and
sell prices, and it's normal in any market with active traders. It only counts
as free money if buying everything costs LESS than 100, or selling everything
brings in MORE than 100.

Second, the smallest price step on Kalshi is 1 cent. So a contract that should
really be worth a tenth of a cent still gets quoted at 1 cent. In a group with
39 outcomes, that's a lot of near-worthless contracts all priced at the
minimum, which pushes the total way above 100 for reasons that have nothing to
do with anyone being wrong. The more outcomes in a group, the more this
distorts the total.

## Bitcoin price at the end of 2026
Event: KXBTCY-27JAN0100
Type: range_partition
Rule: exhaustive: YES prices sum to ~100 (both checks apply)
Markets: 28   Settles: 2027-01-01
Notes: This one covers every possible price. The bottom bucket is "19,999.99
or below" with no lower limit, the top is "150,000 or above" with no upper
limit, and every bucket in between picks up exactly where the last one ended,
so there are no gaps. That means one of them has to pay out, and both of my
checks apply here. Buying everything costs 101 and selling everything brings
in 95, which is the normal gap, not an opportunity. Worth noting that a few of
the middle buckets have no buy price at all, so even if something looked
mispriced there I couldn't actually sell into it.

## S&P close price end of 2026?
Event: KXINXY-26DEC31H1600
Type: range_partition
Rule: exhaustive: YES prices sum to ~100 (both checks apply)
Markets: 27   Settles: 2026-12-31
Notes: Same structure as the Bitcoin one and also covers every possible price,
so both checks apply. But this group is much emptier than it first looks.
The bottom 12 buckets, everything below 6,200, have nobody willing to buy at
all and are just sitting at 1 cent to sell. Only about 15 of the 27 buckets
have real prices on both sides. That's why selling everything only brings in
84 while buying everything costs 116, which is a much bigger gap than
Bitcoin's. Most of that 116 is the minimum-price effect from the dead buckets
rather than anything meaningful.

## Inflation in December 2026 (CPI YoY)
Event: KXCPIYOY-26DEC
Type: ladder_above
Rule: P must not increase as the threshold increases
Markets: 21   Settles: 2027-01-13
Notes: The prices fall steadily from 95 (above 3.0%) down to 3 (above 5.0%),
which is the order they should be in, since it's harder for inflation to clear
a higher bar. Two spots look out of order if I only look at the buy prices:
4.4% is 16 while 4.3% is 15, and 4.7% is 11 while 4.6% is 10. Neither one is
actually tradable though, because I'd have to sell one for more than I could
buy the other, and the gap between buying and selling prices is wider than the
difference. I'd expect these to genuinely go out of order right after a new
inflation figure comes out, since some of these will update faster than others.
The buy/sell gap widens to 6 cents around 3.6% and 4.2%, which is where the
outcome is least certain, so anything that looks like an opportunity in that
range is probably not real.

## How many House seats will Republicans win in the Midterms?
Event: KXRHOUSEWON-26NOV03
Type: ladder_above
Rule: P must not increase as the threshold increases
Markets: 14   Settles: 2027-01-03
Notes: Prices drop from 89 (at least 182 seats) down to 3 (at least 234), which
makes sense since winning more seats is harder. Same pattern as the inflation
one: "at least 210" has a buy price of 23 while "at least 206" is 22, which is
backwards, but the gap between buy and sell prices is too wide for it to be
worth anything. The buy/sell gaps blow out to 6 cents right around 206 to 210
seats, which is roughly where the majority is decided and where nobody's
confident. This group settles after the midterms in November, so I should see
it move a lot and eventually resolve while the project is still running.

## How low will the S&P get this year?
Event: KXINXMINY-01JAN2027
Type: ladder_below
Rule: P must not increase as the threshold decreases
Markets: 5   Settles: 2027-01-01
Notes: This is the smallest group I'm tracking and the only one that runs
downward, and it has an actual contradiction in it right now. "6,100 or below"
can be bought at 10, but "6,200 or below" can be sold at 9. The S&P can't
reach 6,100 without passing through 6,200 first, so the 6,100 contract can
never be worth more than the 6,200 one. It is right now, by 1 cent. That's
tiny and fees would probably eat it, but it's a genuine contradiction sitting
in a market people are actively trading. The data for this group is also shaped
oddly compared to the others: the upper and lower limits are the same number
rather than one of them being open-ended.

## Heisman Trophy Winner
Event: KXHEISMAN-27
Type: exclusive_set
Rule: exclusive but maybe not exhaustive (sell-side check only)
Markets: 39   Settles: 2027-01-01
Notes: 39 players listed, and 21 of them have nobody willing to buy at all, so
most of this group isn't really trading. More importantly, this list can't
cover every possibility. Someone not on it could have a big season and win, so
I can't assume one of these 39 has to pay out. That means only the selling
check applies here, not the buying one. Selling everything brings in 89, well
short of the 100 it would need to be worth doing. The 129 it costs to buy
everything looks alarming but it's mostly the 1-cent minimum on 20-odd players
nobody expects to win.

## How many states will redistrict before the midterms?
Event: KXNUMREDISTRICTING-26NOV03
Type: range_partition
Rule: exhaustive: YES prices sum to ~100 (both checks apply)
Markets: 7   Settles: 2026-11-03
Notes: This covers everything, since there's a "below 8" at one end, each
number from 8 to 12 in the middle, and "above 12" at the other end, so both
checks apply. It's dominated by one bucket: "below 8" is trading at 77 to 84
while everything else is in single digits. That one also has a 7 cent gap
between buying and selling, which is wide for something this heavily favoured.
This is the closest group to settling out of everything I'm tracking, so it's
the one where I'll get a complete price history from start to finish.

