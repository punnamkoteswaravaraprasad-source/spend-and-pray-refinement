# KPI definitions

All order metrics use the selected Data scope, then dashboard filters (if present). Order Matching has a separately labeled status filter for the displayed records. An order is one checkout, not one bottle. Currency is USD. Campaign allocations are full planned budgets, not actual spend or prorated by order dates.

| KPI | Formula | Unit and interpretation |
| --- | --- | --- |
| Total orders | Number of selected orders | Orders; each included once |
| Total revenue | Sum of selected order totals | USD; demonstration sales, not profit |
| Average order value | Total revenue / total orders | USD per order; 0 with no orders |
| Matched orders | Count with recomputed status Matched | Orders verified by saved signals or owner review |
| Matched revenue | Sum of matched order totals | USD; excludes unattributed and review orders |
| Attribution Coverage | Matched orders / total orders × 100 | %; same denominator as the two rates below |
| Unattributed Order Rate | Unattributed orders / total orders × 100 | %; no verified campaign assignment |
| Needs Review Rate | Needs Review orders / total orders × 100 | %; unverified or conflicting campaign evidence |
| Planned campaign budget | Sum of selected campaign allocations | USD; not confirmed ad expenditure |
| Budget-based ROAS | Matched revenue / selected planned budget | Multiple, e.g. 2.13x; N/A without a positive budget |
| Campaign ROAS | Campaign-matched revenue / that campaign's planned budget | Multiple; N/A without positive budget |
| Bottles sold by sauce | Sum of readable historical item quantities by product | Bottles; not inferred product revenue |

Coverage + Unattributed Order Rate + Needs Review Rate = 100% for a nonempty selection, subject to display rounding. Empty selections show all three rates as 0%. Every record is recomputed into exactly one status; stored Pending values do not disappear from the denominator or donut.

ROAS of 1.00x means revenue equals planned budget. It is not a profit break-even threshold: product costs, refunds/fulfillment costs, and actual ad spend are not modeled. Owner reviews are associations supported by recorded notes, not causal proof.

Invalid order dates remain in all-date KPIs; date-limited reports and dated charts exclude them with a warning. Historical naive timestamps are treated as UTC. Revenue lines only connect observed dates. One date shows a bar, and an optional cumulative view is explicitly ordered by individual purchases, not calendar periods.
