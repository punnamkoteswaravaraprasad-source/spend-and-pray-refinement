# Spend & Pray — Professor feedback refinement

Independent HotVile classroom demo, based on the supplied professor-feedback ZIP. The original prototype repository is unchanged.

## Run locally

Install `requirements.txt`, then run `streamlit run app.py`.

## Connected data

The supplied baseline contains 6 campaigns, 150 fictional orders and 65 fictional feedback responses. Every screen uses `data/campaigns.csv` and `data/demo_orders.csv`; feedback is joined using order ID. New demonstration orders are appended to that dataset. These records do not represent real business results. Use fictional names and emails in the public demo.

The optional sample-scope engine API is retained for compatibility and covered by tests; legacy sample files are not added to the visible dashboard or matching page.

## Interaction update

The split welcome screen, focused action cards, form spacing and focus feedback are inspired by the public InsurAI login page. HotVile branding is retained. Demo role access is explicitly labeled; this is not an authentication system. The owner workspace opens directly into a professional analytics dashboard with neutral panels, four primary KPIs, a chart grid, and visible filters. Campaign creation uses a focused form beside sharing guidance. Order Matching uses a searchable table and one review form; all three attribution statuses remain distinct. Navigation is initially collapsed and cards stack on phones.

## KPI definitions

- Attribution coverage: matched orders / all selected orders × 100 (%).
- Unattributed order rate: unattributed orders / all selected orders × 100 (%).
- Needs Review Rate: review orders / all selected orders × 100 (%).
- Revenue: sum of order totals ($); attributed revenue includes verified matched orders only.
- Average order value: revenue / order count ($).
- Planned budget: sum of selected campaign budgets ($).
- Budget-based ROAS: matched revenue / planned budget (x); N/A if budget is zero. This is not profit or actual advertising spend.

Dashboard campaign and channel filters narrow verified matches while retaining unmatched orders for context; an explicit caption explains this. Date filters exclude invalid dates. Feedback follows the same selected order IDs. The donut includes all three attribution statuses. Single-date revenue uses a bar and explains why there is no trend.

## Limitations

No authentication, payments, inventory, shipping calculation, tax calculation, actual ad-platform spend, or causal attribution. Promo codes identify campaigns; they do not apply discounts. CSV writes are serialized within one process only. Streamlit Cloud local writes are ephemeral and may reset on redeployment; use an external database and authentication before collecting real customer details. Feedback is self-reported and is never treated as a verified campaign match. Seed order totals are illustrative historic values, not a price audit against today's catalog.

## Verification

Run `python -m unittest discover -s tests -v` and `python scripts/verify_interfaces.py`. Integration checks work in temporary copies and do not create records in the deployed dataset. See `PROFESSOR_UPDATE_VERIFICATION.md` for final results.

## Internal workspace refinement

Owner screens share `workspace_ui.py` and `workspace.css`. The dashboard includes revenue trends, attribution breakdown, channel revenue and order comparisons, campaign budget/revenue comparisons, budget-based ROAS ranking, order volume, and filtered customer feedback. Order status filters use the same denominator for every chart and KPI. Product cards use restrained borders and no glow effects. The welcome screen was left unchanged during this internal-layout revision.


## Supplied design references

The owner workspace now follows the supplied InsurAI screenshots: navy grouped navigation, a dedicated overview with a dark hero and calculated tracking briefing, larger KPI cards with descriptions, and a separate Analytics page with filters, rate/revenue bars, and chart comparisons. Customer shopping has a separate orange-and-cream product-led storefront, inspired by the supplied sauce-store screenshot. No newsletter signup or discount offer is implemented. Technical explanations remain in expandable sections. Graphs and KPI totals share the same selected orders; the integration checklist verifies channel and campaign changes together.


## HotVile brand alignment

The current shared palette is white, charcoal/black and flame orange. Owner navigation, page headers, KPI accents, graph colors and controls use HotVile's palette. The copied navy treatment and duplicate hero summary were removed. The landing page introduces HotVile's sauce collection, heat range and product imagery first; Spend & Pray is described as the supporting owner workspace beneath the collection preview. The customer storefront layout is retained. Analytics filters still update graphs and totals together.

The current landing page uses the exact six catalog bottle photographs with cream labels, replacing the dark-label collection banner. Landing and owner surfaces use light cream/white backgrounds with orange accents, including the owner sidebar and tracking briefing.

The owner navigation now follows Business Overview → Order Matching → Marketing Dashboard. Business Overview explains campaign creation/sharing, customer checkout, matching and performance review; Create Campaign is launched from its first step. The Marketing intelligence tagline and Analytics display names are removed.
