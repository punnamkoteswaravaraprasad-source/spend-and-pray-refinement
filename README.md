# Spend & Pray — HotVile demo

A classroom storefront and marketing-attribution workspace. This separate v0.8 refinement was extracted from Spend_and_Pray_Latest_2026-11-17.zip. The original project and live deployment are unchanged.

## Run locally

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m streamlit run app.py
```

## Workflows

- Customers can filter six sauces by heat, adjust quantities, validate an optional promo code, and place a fictional order with a required name and optional email. No money is collected and no confirmation email is sent. The saved order links the entered name to the unique order ID, recorded cart quantities, and order total.
- Owners can create campaign links and QR codes. Copy links with the copy control in the link's code box. Links generated locally work only on the same computer.
- The dashboard's channels, campaigns, statuses, and optional UTC order-date range apply to all KPIs and charts. Unknown channel and No verified campaign preserve visibility into attribution gaps.
- Planned budgets are full campaign allocations. They are not actual spending, not prorated by selected order dates, and not a profit measure. Zero-budget ROAS is N/A.
- In Order Matching, expand an order, record evidence, and assign a campaign, keep it unattributed, or restore automatic matching. The append-only `data/attribution_reviews.csv` history preserves original tracking records. The latest review takes effect in reports.
- Malformed order dates stay in all-date totals and are disclosed; date-limited reports and trends exclude them. Single-date revenue is shown as a bar, with no invented trend.

## Development

```powershell
.venv/Scripts/python -m unittest discover -s tests
```

`catalog.py` defines products, `dashboard_charts.py` defines revenue visuals, `reporting.py` defines report selection, and `data_store.py` serializes same-process CSV writes. Stable order IDs prevent duplicate writes for retries using the same checkout token. Exact repeated campaign details are rejected.

## Demo boundaries

Owner/customer switching is a demo experience selector, not authentication. CSV data is local to the running instance; locks cover one Python process, not multiple replicas. Keep private data out of a public demo. Production use requires owner authentication, an external transactional database, and a deployment/storage plan. Product sizes, ingredient lists, and allergen claims must come from verified product information and are not invented here.

The old `spend-and-pray-demo.streamlit.app` deployment uses Leya-Varghese's repository. Pushing to `punnamkoteswaravaraprasad-source/spend-and-pray-prototype` does not update that deployment.


## Separate refinement project (v0.8)

Start this copy on a different port:

```powershell
python -m streamlit run app.py --server.port 8503
```

- A shared owner Data scope selector persists between Overview, Campaign Builder, Order Matching, and Marketing Dashboard. Local dashboard/status filters are additional filters and are labeled as such.
- Customer orders reads `data/demo_orders.csv` and `data/campaigns.csv`. Existing legacy demo checkout records are classified as customer-order records; this does not mean paid real-world sales.
- Illustrative sample reads optional `data/sample_orders.csv` and `data/sample_campaigns.csv` using the same headers as the customer CSVs. None are generated or shipped by this refinement. Missing sample files show an empty state.
- Combined merges the two explicitly supplied sources. Sample identifiers are namespaced in memory to prevent collisions or cross-source campaign matches. Illustrative records are read-only; new orders, campaigns, and reviews apply to customer data only.
- Coverage, Unattributed Order Rate, and Needs Review Rate use the same selected-order denominator. The engine recomputes every record into exactly one of these three attribution classes rather than dropping pending or unrecognized stored labels. See KPI_DEFINITIONS.md.
- The ZIP baseline has no feedback survey feature, illustrative dataset generator, or developer-diagnostics panel. The public site's 1-response survey cannot be edited in this source. If surveys are later imported, display the response count beside ratings and label small samples as early feedback; keep self-reports separate from verified campaign attribution.
- Demo experience switching remains available and explicitly labeled as non-authenticated. Use fictitious personal information for demonstrations. Authentication and an external database remain required for public production use.

Validation: `python -m unittest discover -s tests` and `python scripts/verify_interfaces.py`.
