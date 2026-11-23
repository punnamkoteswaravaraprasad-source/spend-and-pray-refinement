# Spend & Pray — Connected Demo Dataset Update

This package replaces the previous test/demo CSV data with one connected fictional dataset.

## What changed
- `data/campaigns.csv`: 6 seeded HotVile campaigns across Paid Social, Influencer, Farmers Market, and Pop-up Event.
- `data/demo_orders.csv`: 150 fictional orders. 120 are matched to a saved campaign through both campaign ID and promo code; 30 are unattributed.
- `data/customer_feedback.csv`: 65 fictional feedback responses. Every response references a valid order ID, with no duplicate order responses.
- `data/attribution_reviews.csv`: retained as an empty review log with its original header.
- `pages/marketing_dashboard.py`: removed the separate in-memory illustrative sample campaigns/orders. The dashboard now reads the shared campaign/order CSV data, so the campaign builder, store, matching page, and dashboard share one dataset.

## ROAS demonstration values
Attributed order revenue divided by each campaign's planned budget is set to a range of approximately 0.78x–2.15x. This is a balanced demonstration range, not verified advertising performance. Planned budget is not confirmed ad spend, and ROAS is not profit.

## Important
All generated customer names, emails (`example.com`), orders, and feedback are fictional. Do not present them as real customer activity or real business results.

The existing project code and design were otherwise retained. New campaigns created in the campaign builder continue to be saved to `data/campaigns.csv`; future store orders and feedback continue to be written to the same shared CSV files.

## Local test
From the project folder:
```bash
python -m streamlit run app.py
```

Python syntax compilation passed. The automated pytest suite could not be collected in this environment because Streamlit is not installed here; run the project tests in your normal environment after installing `requirements.txt`.

## Before replacing your local project
Keep a copy of your existing `data` folder if you want to preserve the old test records. This package contains the updated data files.
