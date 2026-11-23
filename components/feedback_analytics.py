
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import csv

from attribution_engine import process_orders

from pathlib import Path
from collections import Counter
from html import escape


# ==================================================
# 1. FILE CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

ORDERS_FILE = DATA_DIR / "demo_orders.csv"

FEEDBACK_FILE = DATA_DIR / "customer_feedback.csv"

BRAND_COLOR = "#D94B35"
GOLD_COLOR = "#D6AD72"


# ==================================================
# 2. MARKETING SOURCE MAPPING
# ==================================================

SOURCE_MAPPING = {
    "Instagram / Facebook Advertisement": "Paid Social",
    "Organic Social Media": "Organic Social",
    "Influencer / Content Creator": "Influencers",
    "Farmers Market": "Farmers Markets",
    "Pop-up Event": "Pop-up Events",
    "Friend / Family Recommendation": "Word of Mouth",
    "Google / Online Search": "Online Search",
    "Returning Customer": "Returning Customer",
    "Other": "Other",
    "I don't remember": "Unknown",
    "": "Unknown"
}

# These responses provide a recognizable source.
# Returning Customer alone does not identify
# the original discovery source.

KNOWN_SOURCES = {
    "Paid Social",
    "Organic Social",
    "Influencers",
    "Farmers Markets",
    "Pop-up Events",
    "Word of Mouth",
    "Online Search"
}


# ==================================================
# 3. READ CSV FILES
# ==================================================

def read_csv_file(file_path):

    if not file_path.exists():
        return []

    with open(
        file_path,
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


# ==================================================
# 4. CLEAN AND MAP SOURCE
# ==================================================

def get_reported_source(feedback):

    source = (
        feedback.get("reported_source") or ""
    ).strip()

    return SOURCE_MAPPING.get(source, "Unknown")


# ==================================================
# 5. CALCULATE FEEDBACK METRICS
# ==================================================

def calculate_feedback_metrics(orders, feedback):

    order_lookup = {
        row["order_id"]: row
        for row in orders
        if row.get("order_id")
    }

    # Retain one response per valid order ID.
    feedback_lookup = {}

    for response in feedback:

        order_id = response.get("order_id")

        if order_id in order_lookup:
            feedback_lookup[order_id] = response

    valid_feedback = list(feedback_lookup.values())

    total_orders = len(order_lookup)

    total_responses = len(valid_feedback)

    response_rate = (
        total_responses / total_orders * 100
        if total_orders else 0
    )

    ratings = []

    source_counts = Counter()

    recovered_orders = []

    matched_orders = []

    unattributed_orders = []

    pending_orders = []

    for order in order_lookup.values():

        status = (
            order.get("match_status") or ""
        ).strip().lower()

        if status == "matched":
            matched_orders.append(order)

        elif status == "unattributed":
            unattributed_orders.append(order)

        else:
            # Includes Needs Review and any unknown/pending state.
            pending_orders.append(order)

    for response in valid_feedback:

        order_id = response["order_id"]

        source = get_reported_source(response)

        source_counts[source] += 1

        # Calculate satisfaction rating.
        try:

            rating = int(
                response.get("shopping_rating", "")
            )

            if 1 <= rating <= 5:
                ratings.append(rating)

        except (ValueError, TypeError):
            pass

        order = order_lookup[order_id]

        status = (
            order.get("match_status") or ""
        ).strip().lower()

        # Only confirmed unattributed orders can
        # be counted as recovered through feedback.

        if (
            status == "unattributed"
            and source in KNOWN_SOURCES
        ):

            recovered_orders.append({
                "order_id": order_id,
                "source": source,
                "source_details": response.get(
                    "source_details", ""
                ),
                "order_total": order.get(
                    "order_total", "0"
                )
            })

    average_rating = (
        sum(ratings) / len(ratings)
        if ratings else None
    )

    matched_count = len(matched_orders)

    unattributed_count = len(unattributed_orders)

    recovered_count = len(recovered_orders)

    unknown_count = max(0, unattributed_count - recovered_count)

    pending_count = len(pending_orders)

    original_coverage = (
        matched_count / total_orders * 100
        if total_orders else 0
    )

    improved_coverage = (
        (matched_count + recovered_count)
        / total_orders * 100
        if total_orders else 0
    )

    return {
        "total_orders": total_orders,
        "total_responses": total_responses,
        "response_rate": response_rate,
        "average_rating": average_rating,
        "source_counts": source_counts,
        "rating_counts": Counter(ratings),
        "matched_count": matched_count,
        "unattributed_count": unattributed_count,
        "recovered_count": recovered_count,
        "unknown_count": unknown_count,
        "pending_count": pending_count,
        "original_coverage": original_coverage,
        "improved_coverage": improved_coverage,
        "coverage_improvement": (
            improved_coverage - original_coverage
        ),
        "recovered_orders": recovered_orders,
        "valid_feedback": valid_feedback
    }


# ==================================================
# 6. DISPLAY HORIZONTAL BAR CHART
# ==================================================

def display_bar_chart(data, color):

    if not data:
        st.info("No responses available yet.")
        return

    maximum = max(data.values())

    if maximum <= 0:
        st.info("No responses available yet.")
        return

    for label, value in data.items():

        width = value / maximum * 100

        safe_label = escape(str(label))

        st.markdown(
            f'<div style="margin-bottom:15px;">'
            f'<div style="display:flex;'
            f'justify-content:space-between;'
            f'margin-bottom:5px;">'
            f'<span>{safe_label}</span>'
            f'<strong>{value}</strong>'
            f'</div>'
            f'<div style="background:#88888822;'
            f'height:13px;border-radius:4px;">'
            f'<div style="background:{color};'
            f'width:{width}%;height:13px;'
            f'border-radius:4px;"></div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ==================================================
# 7. DISPLAY ATTRIBUTION COVERAGE
# ==================================================

def display_coverage_chart(metrics):

    total = metrics["total_orders"]

    if not total:
        st.info("No orders available.")
        return

    matched = metrics["matched_count"]

    recovered = metrics["recovered_count"]

    pending = metrics["pending_count"]

    matched_pct = matched / total * 100

    recovered_pct = recovered / total * 100

    pending_pct = pending / total * 100

    before_unknown = max(
        0, 100 - matched_pct - pending_pct
    )

    after_unknown = max(
        0,
        100 - matched_pct
        - recovered_pct - pending_pct
    )

    st.markdown(
        f"**Before Feedback — "
        f"{matched_pct:.1f}%**"
    )

    st.markdown(
        f'<div style="display:flex;'
        f'height:26px;border-radius:5px;'
        f'overflow:hidden;">'
        f'<div style="width:{matched_pct}%;'
        f'background:{BRAND_COLOR};"></div>'
        f'<div style="width:{before_unknown}%;'
        f'background:#D6D3D1;"></div>'
        f'<div style="width:{pending_pct}%;'
        f'background:#78716C;"></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    improved = metrics["improved_coverage"]

    st.markdown(
        f"**After Feedback — {improved:.1f}%**"
    )

    st.markdown(
        f'<div style="display:flex;'
        f'height:26px;border-radius:5px;'
        f'overflow:hidden;">'
        f'<div style="width:{matched_pct}%;'
        f'background:{BRAND_COLOR};"></div>'
        f'<div style="width:{recovered_pct}%;'
        f'background:{GOLD_COLOR};"></div>'
        f'<div style="width:{after_unknown}%;'
        f'background:#D6D3D1;"></div>'
        f'<div style="width:{pending_pct}%;'
        f'background:#78716C;"></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<span style="color:{BRAND_COLOR};">'
        f'■</span> Campaign Matched &nbsp;&nbsp;'
        f'<span style="color:{GOLD_COLOR};">'
        f'■</span> Self-Reported &nbsp;&nbsp;'
        f'<span style="color:#D6D3D1;">'
        f'■</span> Unknown &nbsp;&nbsp;'
        f'<span style="color:#78716C;">'
        f'■</span> Pending / Needs Review',
        unsafe_allow_html=True
    )

    improvement = metrics["coverage_improvement"]

    if improvement > 0:

        st.success(
            f"Customer feedback improved "
            f"known-source coverage by "
            f"{improvement:.1f} percentage points."
        )

    if pending:

        st.caption(
            f"{pending} orders are pending matching "
            f"or require review. These are not "
            f"counted as recovered sources."
        )


# ==================================================
# 8. DISPLAY CUSTOMER COMMENTS
# ==================================================

def display_recent_feedback(feedback):
    sorted_feedback = sorted(
        feedback,
        key=lambda row: row.get("submitted_at", ""),
        reverse=True
    )
    comments = [
        row for row in sorted_feedback
        if (row.get("customer_feedback") or "").strip()
    ]
    if not comments:
        st.info("No written feedback submitted yet.")
        return

    cards = []
    for response in comments[:8]:
        try:
            rating = int(response.get("shopping_rating", 0))
        except (TypeError, ValueError):
            rating = 0
        stars = "★" * max(0, min(rating, 5)) + "☆" * (5 - max(0, min(rating, 5)))
        comment = escape(response.get("customer_feedback", ""))
        source = escape(get_reported_source(response))
        order_id = escape(response.get("order_id", ""))
        cards.append(
            f'<article class="review-card">'
            f'<div class="review-top"><span class="review-stars">{stars}</span>'
            f'<span class="review-rating">{rating}/5</span></div>'
            f'<p class="review-comment">“{comment}”</p>'
            f'<div class="review-meta"><span>{source}</span><span>{order_id}</span></div>'
            f'</article>'
        )
    st.markdown(
        """
        <style>
        .review-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:8px;}
        .review-card{background:#FFFFFF;border:1px solid #EADFD5;border-top:3px solid #D65A31;border-radius:14px;padding:17px 18px;box-shadow:0 5px 16px rgba(80,45,25,.06);min-height:145px;}
        .review-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}
        .review-stars{color:#D99A2B;font-size:1.15rem;letter-spacing:2px;}
        .review-rating{color:#443630;font-weight:800;font-size:.9rem;}
        .review-comment{color:#30241F;font-size:1rem;line-height:1.5;margin:0 0 15px;}
        .review-meta{display:flex;justify-content:space-between;gap:10px;color:#806F64;font-size:.78rem;border-top:1px solid #F0E7DF;padding-top:9px;}
        @media(max-width:700px){.review-grid{grid-template-columns:1fr;}}
        </style>
        <div class="review-grid">""" + "".join(cards) + "</div>",
        unsafe_allow_html=True
    )


# ==================================================
# 9. DISPLAY RECOVERED ORDERS
# ==================================================

def display_recovered_orders(orders):

    if not orders:

        st.info(
            "No confirmed unattributed orders "
            "have been recovered through "
            "customer feedback yet."
        )

        return

    for order in orders:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [2, 2, 1]
            )

            with col1:
                st.text(order["order_id"])

            with col2:
                st.text(order["source"])

            with col3:

                try:

                    amount = float(
                        order["order_total"]
                    )

                    st.write(f"${amount:.2f}")

                except (ValueError, TypeError):
                    st.write("Unavailable")

            if order["source_details"]:

                st.caption("Reported source details")

                st.text(order["source_details"])

            st.caption(
                "Evidence: Self-Reported Attribution"
            )


# ==================================================
# 10. MAIN FEEDBACK DASHBOARD
# ==================================================

def display_feedback_dashboard(order_ids=None):
    st.divider()
    st.header("Customer satisfaction")

    try:
        orders = read_csv_file(ORDERS_FILE)
        processed_orders, _ = process_orders()
        status_by_order_id = {
            row.get("order_id"): row.get("status", "Needs Review")
            for row in processed_orders if row.get("order_id")
        }
        for order in orders:
            order["match_status"] = status_by_order_id.get(order.get("order_id"), "Needs Review")
        feedback = read_csv_file(FEEDBACK_FILE)
    except (OSError, csv.Error, UnicodeError):
        st.error("Unable to read customer feedback data.")
        return

    if order_ids is not None:
        selected = set(order_ids)
        orders = [row for row in orders if row.get("order_id") in selected]
    metrics = calculate_feedback_metrics(orders, feedback)
    st.caption(f"Early feedback · {metrics['total_responses']} responses from {metrics['total_orders']} selected demo orders. Self-reported discovery is separate from verified campaign attribution.")
    if not metrics["total_responses"]:
        st.info("Customer feedback will appear here after customers submit their surveys.")
        return

    ratings = metrics["rating_counts"]
    rated_total = sum(ratings.values())
    positive = sum(ratings.get(r, 0) for r in (4, 5))
    satisfaction = positive / rated_total * 100 if rated_total else 0
    average = metrics["average_rating"] or 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Average rating", f"{average:.1f} / 5" if rated_total else "N/A")
    k2.metric("Positive ratings", f"{satisfaction:.0f}%" if rated_total else "N/A")
    k3.metric("Survey responses", f"{metrics['total_responses']:,}")
    k4.metric("Response rate", f"{metrics['response_rate']:.1f}%")

    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Rating distribution")
        rating_frame = [
            {"Rating": f"{rating} stars", "Responses": ratings.get(rating, 0)}
            for rating in range(5, 0, -1)
        ]
        fig = px.bar(
            rating_frame, x="Responses", y="Rating", orientation="h",
            text="Responses", color="Rating",
            color_discrete_sequence=["#A92E2E", "#C84A32", "#D65A31", "#E6A04B", "#EADFD5"]
        )
        fig.update_layout(
            template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
            font=dict(color="#2D211D", size=13), showlegend=False,
            margin=dict(l=10, r=15, t=10, b=10), height=280,
            xaxis_title="Number of responses", yaxis_title=None
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, width="stretch")

    with right:
        st.subheader("How customers found HotVile")
        source_data = [
            {"Source": label, "Responses": count}
            for label, count in metrics["source_counts"].most_common()
        ]
        if source_data:
            fig = px.pie(
                source_data, names="Source", values="Responses", hole=.58,
                color_discrete_sequence=["#A92E2E", "#D65A31", "#D99A2B", "#6F8F72", "#8C6D62", "#C9B9AA"]
            )
            fig.update_layout(
                template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
                font=dict(color="#2D211D", size=12), legend_title=None,
                margin=dict(l=5, r=5, t=10, b=10), height=280
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No discovery-source responses yet.")

    st.subheader("Attribution insights from feedback")
    st.caption("Survey answers are self-reported. They add context but do not count as verified campaign matches or campaign ROAS.")
    a1, a2, a3 = st.columns(3)
    a1.metric("Campaign-matched orders", metrics["matched_count"])
    a2.metric("Unattributed orders with a known reported source", metrics["recovered_count"])
    a3.metric("Unknown source", metrics["unknown_count"])

    st.subheader("Recent customer reviews")
    display_recent_feedback(metrics["valid_feedback"])

    with st.expander("View recovered self-reported sources"):
        display_recovered_orders(metrics["recovered_orders"])
