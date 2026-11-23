SPEND & PRAY — PROFESSOR FEEDBACK UPDATE
========================================

This update applies the visual and usability recommendations while preserving
the existing campaign, storefront, order matching, attribution, and shared CSV
workflows.

WHAT CHANGED
------------
1. Introduced a warm light theme across the app: cream page backgrounds,
   white cards, dark readable text, and HotVile red/orange accents.
2. Increased typography and improved contrast for headings, labels, captions,
   KPI values, and dashboard cards.
3. Removed decorative emoji from navigation and key page labels; the sidebar
   now uses a consistent HOTVILE wordmark treatment.
4. Simplified the Marketing Dashboard copy and changed its charts to a light
   chart theme.
5. Kept individual order-level review in Order Matching; the Business Owner
   Marketing Dashboard remains focused on aggregate KPIs and charts.
6. Redesigned Customer Satisfaction with average rating, positive-rating
   percentage, response count/rate, a rating-distribution chart, a discovery
   source chart, and compact review cards.
7. Kept self-reported discovery sources separate from verified campaign
   matches and campaign ROAS.

DATA
----
The existing connected CSV files are included unchanged:
- data/campaigns.csv
- data/demo_orders.csv
- data/customer_feedback.csv

The archive contains 6 campaigns, 150 order records, and 65 feedback records.
No demo data was regenerated or disconnected.

LOCAL TESTING
-------------
Python syntax compilation passed for the project files.

The automated pytest suite could not be collected in this build environment
because Streamlit is not installed here. Run the app in your existing project
environment after installing requirements.txt:

    python -m pip install -r requirements.txt
    python -m streamlit run app.py

RECOMMENDED CHECK BEFORE DEPLOYMENT
----------------------------------
1. Open the Home page and confirm the owner/customer role selection.
2. Create a test campaign and confirm it is saved.
3. Open Order Matching and confirm individual order records still appear.
4. Open Marketing Dashboard and test channel, campaign, and date filters.
5. Check Customer Satisfaction charts and review cards.
6. Place a test storefront order and submit a survey only if you want to test
   live writes to your local CSV files.

BACKUP
------
Before replacing your current working folder, keep a copy of it. This archive
contains the updated source files and the connected demo CSV data.
