# Separate project refinement — November 18, 2026

Source: Spend_and_Pray_Latest_2026-11-17.zip. This is a separate local copy, not the source of the newer live dark-themed site. The original project and public deployment were not changed.

## Review items

1. Shared scope: implemented on Overview, Campaign Builder, Order Matching and Dashboard. Customer records are the original ZIP data. Optional illustrative CSVs are separate, read-only, and namespaced in Combined. No synthetic activity is invented.
2. Consistent denominators: all recomputed statuses remain in totals and donut; three rates share the selected-order denominator. Both rates and counts remain explained.
3. Budget threshold: explicitly Revenue equals planned budget; not break-even/profit. Campaigns without positive budgets have ROAS N/A.
4. Customer diagnostics: not present in this ZIP. Experience switching explicitly says demo and not authentication. No security system was silently removed or added.
5. Tables: one campaign details table in an expander; currencies have two decimals and ROAS has x formatting.
6. Owner home: sales and attribution attention precede charts; tutorial guidance stays in an expander on the landing page.
7. Landing: compact banner and role-entry buttons above description cards.
8. Mobile: sidebar starts collapsed; customer bag count/total and checkout shortcut are visible near shopping controls. Cards and charts stack through Streamlit's responsive layout.
9. Survey: this ZIP contains no survey code or survey records. No invented survey or rating was added. Integration needs the newer live-site source; show response counts and Early feedback when that feature is supplied.

## Validation

13 automated unit/integration tests passed, covering KPI numerical values, zero orders, matching/review preservation, UTC dates, date aggregation, cumulative ordering, invalid dates, quantity parsing, unique writes, customer-name/cart association and source isolation.

The reusable interface script passed campaign validation, invalid promo handling, heat filtering, quantity limit 99, clear cart, empty date ranges and missing-data screens. Scope navigation was checked across real st.navigation owner pages and Dashboard/Order Matching totals agreed for Combined.

No public deployment was performed. This remains a classroom demo using local CSV files and a demo role switch. Use fictitious personal information. Real public use needs owner authentication and durable transactional storage. A local link works only on its host computer.

## Run

Install requirements in your environment and run `python -m streamlit run app.py --server.port 8503`.
Tests: `python -m unittest discover -s tests`; `python scripts/verify_interfaces.py`; `python scripts/verify_scope_navigation.py`.
