from owner_scope import owner_scope
from datetime import datetime

import streamlit as st

from attribution_engine import calculate_kpis, process_orders, save_review
from ui import apply_theme, hero, page_steps, section_label, status_pill


apply_theme()
results, campaigns = process_orders(owner_scope())
kpis = calculate_kpis(results)

hero(
    "Review how orders were matched",
    "Focus on orders requiring attention while keeping technical tracking signals out of the customer experience.",
    "Attribution Quality",
    icon="🔗",
)

page_steps([
    ("🔎", "Detect", "Check campaign IDs and promo-code signals."),
    ("🧩", "Classify", "Separate matched, unattributed, and review orders."),
    ("✅", "Verify", "Resolve uncertain records before using the results."),
])

if not results:
    st.info("No demonstration orders are available yet.")
    st.stop()

section_label("Attribution summary")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", kpis["total_orders"])
k2.metric("Matched", kpis["matched_orders"])
k3.metric("Unattributed", kpis["unattributed_orders"])
k4.metric("Needs Review", kpis["needs_review"])

d1, d2, d3, d4 = st.columns(4)
d1.metric("Attribution Coverage", f"{kpis['coverage']:.1f}%")
d2.metric("Matched Revenue", f"${kpis['matched_revenue']:,.2f}")

d3.metric("Unattributed order rate", f"{kpis['unattributed_rate']:.1f}%")
d4.metric("Needs review rate", f"{kpis['needs_review_rate']:.1f}%")

st.markdown("### Orders")
filter_col, count_col = st.columns([3, 1])
with filter_col:
    selected_filter = st.selectbox(
        "Filter by attribution status",
        ["All", "Matched", "Unattributed", "Needs Review"],
    )
with count_col:
    filtered_results = (
        results
        if selected_filter == "All"
        else [row for row in results if row["status"] == selected_filter]
    )
    st.metric("Visible Orders", len(filtered_results))

if not filtered_results:
    st.info("No orders are available in this category.")
else:
    for order in filtered_results:
        with st.expander(f"{order['customer_name']} · {order['order_id']} · {order['status']} · ${order['revenue']:,.2f}"):
            st.text(f"Customer: {order['customer_name']}")
            st.write(order.get('items') or 'No item details')
            st.write(f"Order date: {order.get('order_date') or 'Unavailable'}")
            st.write(f"Campaign: {order['campaign_name'] if order['status'] == 'Matched' else 'Not verified'}")
            st.caption(f"Source: {order['data_source']}")
            st.info(order['reason'])
            if order['data_source'] == 'Illustrative sample':
                st.caption('Illustrative record — read only')
                continue
            with st.form(f"review_{order['order_id']}"):
                decision = st.selectbox('Review decision', ['Assign to campaign', 'Keep unattributed', 'Restore automatic matching'])
                campaign_options = {c['campaign_id']: c for c in campaigns if c.get('data_source') == 'Customer orders'}
                campaign_id = st.selectbox('Campaign to assign', list(campaign_options),
                    format_func=lambda key: f"{campaign_options[key]['campaign_name']} · {key[-4:]}") if campaign_options else None
                note = st.text_input('Evidence / review note', help='Record why you chose this attribution. Original tracking is preserved.')
                if st.form_submit_button('Save Review', type='primary'):
                    action = {'Assign to campaign':'Matched','Keep unattributed':'Unattributed','Restore automatic matching':'Automatic'}[decision]
                    try:
                        save_review(order['order_id'], action, campaign_id, note)
                    except ValueError as error:
                        st.error(str(error))
                    else:
                        st.session_state['review_saved'] = order['order_id']
                        st.rerun()
if st.session_state.pop('review_saved', None):
    st.success('Review saved. KPIs and charts now use the updated attribution. Original tracking remains unchanged.')

with st.expander("How order matching works"):
    st.markdown(
        """
        - **Matched:** A campaign ID or valid promo code connects the order to a saved campaign.
        - **Unattributed:** The order contains no campaign ID or promo code.
        - **Needs Review:** A tracking value is present but cannot be verified, or signals conflict.

        Attribution indicates an association between marketing and a purchase. It does not prove that marketing caused the purchase.
        """
    )
