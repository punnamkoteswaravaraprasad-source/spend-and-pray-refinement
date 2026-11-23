# Professor feedback update — verification

Updated 2026-11-23. Original ZIP and pre-update refinement snapshot are preserved outside the public repository in the local work folder. A personal checkout record and its linked response from the supplied ZIP are excluded from the public seed files. The public baseline is 150 fictional orders, six campaigns, and 65 linked feedback responses.

## Automated checks

- 13 regression tests: campaign links, customer name and optional email validation, cart item/total linkage, date grouping, single-date behavior, invalid dates, KPI rates, scope isolation, review history and duplicate-write protection.
- Isolated integration checklist: welcome/owner overview, campaign creation, blank campaign name, reversed campaign dates, 150-order consistency, charts, single-date filter, empty filter, heat filter, checkout confirmation, missing CSV files and all-invalid order dates.
- Baseline verified: 120 matched, 30 unattributed, zero needs review. Coverage 80%; unattributed rate 20%; Needs Review Rate 0%. All 65 responses reference distinct valid orders.

## Visual review

- Desktop: split welcome screen, clear entry actions, owner overview and dashboard KPI labels.
- 390px phone: sidebar starts collapsed, storefront cards stack at full width, bottle labels visible, patterned background has a light overlay and readable headings.
- Tracked campaign URL opens the storefront directly without a page-not-found popup. Links are generated against the current host; saved seed URLs use the refinement deployment.

## Deployment target

Repository: punnamkoteswaravaraprasad-source/spend-and-pray-refinement (main).
App: https://spend-and-pray-refinement-u57ftmvykdvvycohk8fkc9.streamlit.app/
The older prototype repository and MRP deployment remain separate.

## Limits

The public InsurAI login page was used as the interaction reference. Its authenticated dashboard was not inspected. Spend & Pray retains explicitly labeled demo access. CSV storage is ephemeral on Streamlit Cloud, single-process write locking does not provide multi-server persistence, and no payments or authentication are implemented. Budget-based ROAS does not measure profit or causation. Use fictional customer details only.


## Internal workspace layout revision

- Replaced decorative owner banners with compact, consistent page headers and a neutral canvas.
- Owner entry opens the analytics dashboard directly. Shared panels, typography, controls, table styling and chart colors are used throughout.
- Added a chart grid with separate revenue/order channel charts, separate dollar/ROAS campaign charts, and order volume.
- Replaced the 150 expandable order blocks with a searchable table and a single review form. Matched, Unattributed, and Needs Review remain separate.
- Extended isolated integration checks to cover status filtering, empty search, required evidence, and saving an order review.
- Retained validation, cart linkage, idempotent writes, single-date bars, invalid-date warnings, filtered feedback, and N/A for zero-budget ROAS.


## Supplied-reference revision

- Added a dedicated owner Dashboard and retained Analytics as a separate filtered chart page.
- Navy grouped sidebar, white analytics header, icon KPI cards, calculated tracking briefing, and rate/revenue progress panels match the supplied visual direction.
- Removed the duplicated attribution donut from Analytics; order volume now sits beside the revenue trend. Other graphs remain visible beneath filters.
- Customer view uses separate storefront navigation and a product-led orange/cream hero. Owner navigation is absent from the customer storefront; demo switching is inside a footer expander.
- No added newsletter, phone or birthday fields, simulated discounts, authentication claims or AI-analysis claims.
- Automated checks include six interfaces, channel/campaign graph and KPI synchronization, search/review evidence validation, checkout linkage, invalid dates, single-date and empty selections.
