from datetime import datetime

import streamlit as st

from attribution_engine import calculate_kpis, process_orders, save_review
from ui import apply_theme, hero, page_steps, section_label, status_pill


apply_theme()

# Order Matching page: HotVile dark theme overrides.
# Keep these rules inside the <style> block so Streamlit does not render them as text.
st.markdown(
    """
    <style>
    /* Page background and default text */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background: #FFF9F1 !important;
        color: #2D211D !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 2rem !important;
    }

    .stApp p,
    .stApp label,
    .stApp li,
    .stApp span,
    .stApp div {
        color: inherit;
    }

    /* Headings and supporting copy */
    h1, h2, h3, h4,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #2D211D !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] {
        color: #6B5A51 !important;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #EADFD5 !important;
        border-left: 5px solid #F05A3A !important;
        border-radius: 16px !important;
        padding: 18px 20px !important;
        min-height: 105px;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: #6B5A51 !important;
        font-size: 0.9rem !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div {
        color: #2D211D !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #F2A65A !important;
    }

    /* Select boxes and text inputs */
    [data-testid="stSelectbox"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stDateInput"] label {
        color: #443630 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #FFFDF9 !important;
        color: #2D211D !important;
        border: 1px solid #DCCBC0 !important;
        border-radius: 9px !important;
    }

    [data-baseweb="select"] input,
    [data-baseweb="select"] span {
        color: #2D211D !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #FFFDF9 !important;
        color: #2D211D !important;
    }

    [role="option"] {
        color: #2D211D !important;
    }

    [role="option"]:hover {
        background: #EADFD5 !important;
    }

    /* Expanders / order records */
    [data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #EADFD5 !important;
        border-radius: 13px !important;
        margin-bottom: 0.65rem !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: #2D211D !important;
    }

    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #FFFFFF !important;
        color: #2D211D !important;
    }

    /* Buttons */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(90deg, #D62828, #F05A3A) !important;
        color: #2D211D !important;
        border: 1px solid #F05A3A !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        border-color: #F2A65A !important;
        color: #FFFFFF !important;
        filter: brightness(1.08);
    }

    /* Alerts and info boxes */
    [data-testid="stAlert"] {
        background: #FFFDF9 !important;
        border: 1px solid #DCCBC0 !important;
        color: #2D211D !important;
        border-radius: 12px !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div {
        color: #443630 !important;
    }

    /* Form containers and dividers */
    [data-testid="stForm"] {
        background: #FFFFFF !important;
        border: 1px solid #EADFD5 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    hr {
        border-color: #EADFD5 !important;
    }

    /* Checkbox and radio labels, if present */
    [data-testid="stCheckbox"] label,
    [data-testid="stRadio"] label {
        color: #443630 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

results, campaigns = process_orders()
kpis = calculate_kpis(results)

hero(
    "Review how orders were matched",
    "Focus on orders requiring attention while keeping technical tracking signals out of the customer experience.",
    "Attribution Quality",
    icon="🔗",
)

page_steps([
    ("", "Detect", "Check campaign IDs and promo-code signals."),
    ("", "Match", "Connect confirmed signals to saved campaigns."),
    ("", "Measure", "Use confirmed matches in campaign reporting."),
])

if not results:
    st.info("No demonstration orders are available yet.")
    st.stop()

section_label("Attribution summary")
# Simplified view: orders without a confirmed campaign match are grouped
# under Unattributed. The underlying attribution engine and review history
# remain unchanged.
display_unattributed = kpis["total_orders"] - kpis["matched_orders"]

k1, k2, k3 = st.columns(3)
k1.metric("Total Orders", kpis["total_orders"])
k2.metric("Matched", kpis["matched_orders"])
k3.metric("Unattributed", display_unattributed)

d1, d2 = st.columns(2)
d1.metric("Attribution Coverage", f"{kpis['coverage']:.1f}%")
d2.metric("Matched Revenue", f"${kpis['matched_revenue']:,.2f}")

st.markdown("### Orders")
filter_col, count_col = st.columns([3, 1])

with filter_col:
    selected_filter = st.selectbox(
        "Filter by attribution status",
        ["All", "Matched", "Unattributed"],
    )

def display_status(order):
    return "Matched" if order["status"] == "Matched" else "Unattributed"

filtered_results = (
    results
    if selected_filter == "All"
    else [
        row for row in results
        if display_status(row) == selected_filter
    ]
)

with count_col:
    st.metric("Visible Orders", len(filtered_results))

if not filtered_results:
    st.info("No orders are available in this category.")
else:
    for order in filtered_results:
        with st.expander(
            f"{order['customer_name']} · {order['order_id']} · "
            f"{display_status(order)} · ${order['revenue']:,.2f}"
        ):
            st.markdown(f"**Customer:** {order['customer_name']}")
            st.write(order.get("items") or "No item details")
            st.write(f"**Order date:** {order.get('order_date') or 'Unavailable'}")
            st.write(
                "**Campaign:** "
                f"{order['campaign_name'] if order['status'] == 'Matched' else 'Not verified'}"
            )
            st.info(order["reason"])

            with st.form(f"review_{order['order_id']}"):
                decision = st.selectbox(
                    "Review decision",
                    [
                        "Assign to campaign",
                        "Keep unattributed",
                        "Restore automatic matching",
                    ],
                    key=f"decision_{order['order_id']}",
                )

                campaign_options = {
                    campaign["campaign_id"]: campaign for campaign in campaigns
                }

                campaign_id = (
                    st.selectbox(
                        "Campaign to assign",
                        list(campaign_options),
                        format_func=lambda key: (
                            f"{campaign_options[key]['campaign_name']} · {key[-4:]}"
                        ),
                        key=f"campaign_{order['order_id']}",
                    )
                    if campaigns
                    else None
                )

                note = st.text_input(
                    "Evidence / review note",
                    help=(
                        "Record why you chose this attribution. "
                        "Original tracking is preserved."
                    ),
                    key=f"note_{order['order_id']}",
                )

                if st.form_submit_button("Save Review", type="primary"):
                    action = {
                        "Assign to campaign": "Matched",
                        "Keep unattributed": "Unattributed",
                        "Restore automatic matching": "Automatic",
                    }[decision]

                    try:
                        save_review(order["order_id"], action, campaign_id, note)
                    except ValueError as error:
                        st.error(str(error))
                    else:
                        st.session_state["review_saved"] = order["order_id"]
                        st.rerun()

if st.session_state.pop("review_saved", None):
    st.success(
        "Review saved. KPIs and charts now use the updated attribution. "
        "Original tracking remains unchanged."
    )

with st.expander("How order matching works"):
    st.markdown(
        """
        - **Matched:** A campaign ID or valid promo code connects the order to a saved campaign.
        - **Unattributed:** No campaign connection has been confirmed for the order. This also includes orders with incomplete or conflicting tracking signals.

        Attribution indicates an association between marketing and a purchase. It does not prove that marketing caused the purchase.
        """
    )

from interaction_ui import apply_interactions
apply_interactions()
