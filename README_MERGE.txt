# Spend & Pray — Combined Prototype

This is a merged version built on your uploaded project.

## What is included
- Your existing Business Owner / Customer role selection and branded navigation.
- Your existing customer feedback survey and feedback analytics.
- Your original glowing storefront effects and checkout flow.
- Your friend's textured background on the customer storefront ONLY.
- Six products and a heat-level filter.
- Improved campaign creation with dynamic campaign tracking links and QR codes.
- Order matching with review decisions and an append-only review history.
- A filtered marketing dashboard with product-demand and revenue analysis.
- Automated tests and an interface verification script.

## Install
1. Extract this ZIP.
2. Open the extracted `spend_pray_merged` folder in VS Code.
3. Keep your existing `.venv` if you have one, or create a fresh environment:
   `python -m venv .venv`
4. Activate it in PowerShell:
   `.\.venv\Scripts\Activate.ps1`
5. Install packages:
   `python -m pip install -r requirements.txt`
6. Run:
   `python -m streamlit run app.py`

## Important data notes
- The current project's `data/campaigns.csv`, `data/demo_orders.csv`, and `data/customer_feedback.csv` were preserved.
- Friend sample customer/order/campaign records were NOT imported.
- A new empty `data/attribution_reviews.csv` was added for order review history.
- Back up the whole project before replacing your working folder.
- Campaign budgets are entered budgets, not verified actual ad spend. Budget-based ROAS is not profit or causal proof.
- Self-reported customer discovery sources are shown separately and are not used to assign campaign ROAS.

## Tests
From the project root, run:
`python -m unittest discover -s tests -v`

Then run:
`python scripts/verify_interfaces.py`

These checks are included but should also be run in your local environment.
