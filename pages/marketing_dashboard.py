from datetime import date, timedelta
from pathlib import Path
import csv

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from attribution_engine import process_orders, match_order
from components.feedback_analytics import display_feedback_dashboard


# ---------------------------------------------------------
# PAGE CONFIGURATION + BRAND STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="Marketing Dashboard", page_icon=None, layout="wide")

st.markdown(
    '''
    <style>
      :root {--hv-bg:#FFF9F1;--hv-panel:#FFFFFF;--hv-text:#2D211D;--hv-muted:#6B5A51;--hv-red:#A92E2E;--hv-orange:#D65A31;--hv-gold:#D99A2B;--hv-border:#EADFD5;}
      .stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#FFF9F1!important;color:#2D211D!important;}
      .block-container{max-width:1460px;padding-top:1.4rem;padding-bottom:3rem;}
      h1,h2,h3,h4{color:#2D211D!important;letter-spacing:-.025em;}
      p,label,[data-testid="stMarkdownContainer"]{color:#443630;}
      .dashboard-eyebrow{color:#A92E2E;font-size:.82rem;font-weight:900;letter-spacing:.16em;text-transform:uppercase;}
      .dashboard-subtitle{color:#6B5A51!important;font-size:1.12rem;line-height:1.5;margin-top:-.45rem;}
      .prototype-banner{background:#FFF0E7;color:#44291F;border:1px solid #F0C7B1;border-left:5px solid #D65A31;border-radius:12px;padding:14px 18px;margin:14px 0 22px;font-size:1rem;line-height:1.5;}
      .prototype-banner *{color:#44291F!important;}
      .section-note{color:#6B5A51!important;font-size:1rem;line-height:1.55;}
      .roas-explainer{background:#FFF0E7;border:1px solid #F0C7B1;border-left:4px solid #D65A31;border-radius:11px;padding:12px 15px;color:#4A3026;margin:10px 0 16px;line-height:1.55;font-size:.96rem;}
      div[data-testid="stMetric"]{background:#FFFFFF!important;border:1px solid #EADFD5!important;border-top:4px solid #D65A31!important;border-radius:14px!important;padding:16px 17px!important;box-shadow:0 5px 18px rgba(80,45,25,.07);min-height:112px;}
      div[data-testid="stMetric"] [data-testid="stMetricLabel"],div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,div[data-testid="stMetric"] [data-testid="stMetricValue"],div[data-testid="stMetric"] [data-testid="stMetricValue"] *,div[data-testid="stMetric"] [data-testid="stMetricDelta"],div[data-testid="stMetric"] [data-testid="stMetricDelta"] *{color:#2D211D!important;opacity:1!important;}
      div[data-testid="stMetric"] [data-testid="stMetricLabel"]{font-size:.95rem;font-weight:750;}
      div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-size:1.7rem;}
      div[data-testid="stExpander"]{border:1px solid #EADFD5!important;border-radius:12px!important;background:#FFFFFF!important;}
      div[data-testid="stExpander"] summary,div[data-testid="stExpander"] summary *{color:#2D211D!important;font-size:1rem;}
      [data-testid="stDataFrame"]{border:1px solid #EADFD5;border-radius:10px;}
      .dashboard-footnote{color:#6B5A51;font-size:.85rem;line-height:1.5;}
      hr{border-color:#EADFD5!important;}
    </style>
    ''',
    unsafe_allow_html=True,
)

st.markdown('<div class="dashboard-eyebrow">HotVile · Business intelligence</div>', unsafe_allow_html=True)
st.title("Marketing Performance")
st.markdown(
    '<p class="dashboard-subtitle">Track sales, campaign results, and attribution quality.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="prototype-banner"><b>CONNECTED DEMO DATA</b> · Fictional seed orders, new demo orders, campaigns, '
    'and customer reviews are connected to the same campaign and order data.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# REAL CUSTOMER ORDERS + REAL CAMPAIGNS FROM PROJECT CSVs
# ---------------------------------------------------------
results, real_campaigns = process_orders()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ORDERS_FILE = DATA_DIR / "demo_orders.csv"


def load_real_order_dates():
    if not ORDERS_FILE.exists():
        return pd.DataFrame(columns=["order_id", "order_date"])
    with open(ORDERS_FILE, "r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    frame = pd.DataFrame(rows)
    if frame.empty or "order_date" not in frame.columns:
        return pd.DataFrame(columns=["order_id", "order_date"])
    frame["order_date"] = pd.to_datetime(frame["order_date"], errors="coerce", utc=True)
    return frame[["order_id", "order_date"]]


real_orders_df = pd.DataFrame(results)
if real_orders_df.empty:
    real_orders_df = pd.DataFrame(
        columns=["order_id", "customer", "revenue", "status", "campaign_id", "campaign_name", "channel"]
    )

# Keep the dashboard resilient if an older attribution_engine.py is present.
# Prefer the order_date returned by the engine; otherwise recover it from the
# shared demo_orders.csv using order_id. Always create the column before filters.
if "order_date" not in real_orders_df.columns:
    real_orders_df["order_date"] = pd.NaT
real_dates = load_real_order_dates()
if not real_dates.empty:
    if "order_date" in real_orders_df.columns:
        real_orders_df = real_orders_df.drop(columns=["order_date"])
    real_orders_df = real_orders_df.merge(real_dates, on="order_id", how="left")
real_orders_df["order_date"] = pd.to_datetime(
    real_orders_df["order_date"], errors="coerce", utc=True
)
real_orders_df["revenue"] = pd.to_numeric(real_orders_df["revenue"], errors="coerce").fillna(0)
real_orders_df["data_type"] = "Demo order"


# All dashboard activity is loaded from the shared project CSV files.
# Campaigns, orders, and feedback are connected through campaign_id / promo_code
# and order_id respectively. No second in-memory sample dataset is added here.
orders_df = real_orders_df.copy()

campaign_df = pd.DataFrame(real_campaigns)
if campaign_df.empty:
    campaign_df = pd.DataFrame(columns=["campaign_id", "campaign_name", "channel", "budget", "promo_code"])
for col in ["campaign_id", "campaign_name", "channel", "budget", "promo_code"]:
    if col not in campaign_df.columns:
        campaign_df[col] = None
campaign_df = campaign_df.drop_duplicates(subset=["campaign_id"], keep="first")
campaign_df["budget"] = pd.to_numeric(campaign_df["budget"], errors="coerce").fillna(0)


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
with st.expander("Dashboard filters", expanded=False):
    f1, f2, f3, f4 = st.columns([1.05, 1.35, 1.35, 1])
    available_channels = sorted(
        c for c in orders_df["channel"].dropna().unique() if c and c != "Unknown"
    )
    with f1:
        selected_channels = st.multiselect(
            "Marketing channel", available_channels, default=available_channels
        )
    available_campaigns = campaign_df[
        campaign_df["channel"].isin(available_channels)
    ]["campaign_name"].dropna().astype(str).sort_values().unique().tolist()
    with f2:
        selected_campaign_names = st.multiselect(
            "Campaign", available_campaigns, default=available_campaigns
        )
    selected_campaign_ids = campaign_df[
        campaign_df["campaign_name"].isin(selected_campaign_names)
    ]["campaign_id"].dropna().tolist()
    with f3:
        date_values = orders_df["order_date"].dropna()
        min_date, max_date = ((date_values.min().date(), date_values.max().date()) if not date_values.empty else (date.today(), date.today()))
        selected_dates = st.date_input(
            "Order date range", value=(min_date, max_date),
            min_value=min_date, max_value=max_date,
        )
    with f4:
        data_types = ["Demo order"]
        selected_types = st.multiselect("Order source", data_types, default=data_types)

filtered_df = orders_df[orders_df["data_type"].isin(selected_types)].copy()
if selected_channels:
    # Keep unattributed / review records visible; channel filtering only narrows verified matches.
    filtered_df = filtered_df[
        (filtered_df["status"] != "Matched") | filtered_df["channel"].isin(selected_channels)
    ]
elif available_channels:
    filtered_df = filtered_df[filtered_df["status"] != "Matched"]

# Campaign filter narrows matched orders while retaining unattributed orders for context.
if selected_campaign_names:
    filtered_df = filtered_df[
        (filtered_df["status"] != "Matched")
        | filtered_df["campaign_id"].isin(selected_campaign_ids)
    ]
elif available_campaigns:
    filtered_df = filtered_df[filtered_df["status"] != "Matched"]

# Streamlit date_input returns either a date or a tuple while the range is being selected.
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    if start_date > end_date:
        st.error("The start date must be on or before the end date.")
        st.stop()
    dated = filtered_df["order_date"].notna()
    in_range = filtered_df["order_date"].dt.normalize().between(
        pd.Timestamp(start_date, tz="UTC"), pd.Timestamp(end_date, tz="UTC")
    )
    if (~dated).any():
        st.warning(f"{int((~dated).sum())} order(s) have missing or invalid dates and are excluded from the date-filtered view.")
    filtered_df = filtered_df[dated & in_range]

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) != 2:
    st.info("Choose an end date to apply the date range.")
    st.stop()
st.caption("All charts and feedback below use the selected date range. Unattributed and review orders remain visible during campaign/channel filtering because their source is not verified.")
matched_df = filtered_df[filtered_df["status"] == "Matched"].copy()
total_orders = len(filtered_df)
total_revenue = float(filtered_df["revenue"].sum())
average_order_value = total_revenue / total_orders if total_orders else 0
matched_orders = len(matched_df)
unattributed_orders = int((filtered_df["status"] == "Unattributed").sum())
needs_review = int((filtered_df["status"] == "Needs Review").sum())
coverage = matched_orders / total_orders * 100 if total_orders else 0
matched_revenue = float(matched_df["revenue"].sum())

# Budget denominator follows the selected channel and campaign filters.
visible_campaigns = campaign_df[
    campaign_df["channel"].isin(selected_channels)
] if selected_channels else campaign_df.iloc[0:0]
visible_campaigns = visible_campaigns[
    visible_campaigns["campaign_name"].isin(selected_campaign_names)
] if selected_campaign_names else visible_campaigns.iloc[0:0]
total_budget = float(visible_campaigns["budget"].sum())
overall_roas = matched_revenue / total_budget if total_budget > 0 else 0
unattributed_pct = unattributed_orders / total_orders * 100 if total_orders else 0


# ---------------------------------------------------------
# EXECUTIVE OVERVIEW — SIX CORE METRICS
# ---------------------------------------------------------
st.subheader("Business overview")
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total revenue", f"${total_revenue:,.2f}")
k2.metric("Total orders", f"{total_orders:,}")
k3.metric("Attributed revenue", f"${matched_revenue:,.2f}")
k4.metric("Attribution coverage", f"{coverage:.1f}%")
k5.metric("Budget-based ROAS", f"{overall_roas:.2f}x" if total_budget > 0 else "N/A")
k6.metric("Unattributed order rate", f"{unattributed_pct:.1f}%")
st.caption(
    "Attributed revenue includes only orders successfully matched to a saved campaign. "
    "Attribution coverage = matched orders ÷ all orders in this view. "
    "Budget-based ROAS = attributed revenue ÷ entered budgets for the selected campaigns."
)


# ---------------------------------------------------------
# CHANNEL PERFORMANCE — ATTRIBUTED REVENUE
# ---------------------------------------------------------
st.divider()
st.subheader("Channel performance")
st.markdown(
    '<p class="section-note">Revenue from orders successfully matched to each marketing channel.</p>',
    unsafe_allow_html=True,
)
if not matched_df.empty:
    channel_summary = (
        matched_df.groupby("channel", dropna=False)
        .agg(Orders=("order_id", "count"), Revenue=("revenue", "sum"))
        .reset_index().sort_values("Revenue", ascending=False)
    )
    fig = px.bar(
        channel_summary, x="channel", y="Revenue", text="Revenue",
        title="Attributed revenue by channel",
        labels={"channel": "Marketing channel", "Revenue": "Revenue ($)"},
        color="Revenue", color_continuous_scale=["#9D3024", "#E34B2F", "#F2A65A"],
    )
    fig.update_traces(texttemplate="$%{y:,.0f}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(color="#2D211D", size=13), showlegend=False, coloraxis_showscale=False,
        xaxis_title=None, yaxis_tickprefix="$",
        margin=dict(l=10, r=10, t=58, b=12), bargap=.35,
        xaxis=dict(tickfont=dict(color="#51443D"), gridcolor="rgba(255,255,255,.12)"),
        yaxis=dict(tickfont=dict(color="#51443D"), gridcolor="rgba(255,255,255,.12)"),
    )
    st.plotly_chart(fig, width="stretch")
else:
    st.info("No matched orders in this filtered view.")


# ---------------------------------------------------------
# CAMPAIGN PERFORMANCE — ROAS + COMPACT LEADERBOARD
# ---------------------------------------------------------
st.divider()
st.subheader("Campaign performance")
st.markdown(
    '<p class="section-note">Compare attributed revenue with each campaign’s entered budget.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="roas-explainer"><b>Budget-based ROAS = attributed revenue ÷ entered campaign budget.</b> '
    'Budget is a spend proxy, not verified advertising-platform spend; ROAS is not profit.</div>',
    unsafe_allow_html=True,
)

campaign_revenue = (
    matched_df.groupby("campaign_id")["revenue"].sum().reset_index(name="Attributed revenue")
    if not matched_df.empty else pd.DataFrame(columns=["campaign_id", "Attributed revenue"])
)
campaign_order_counts = (
    matched_df.groupby("campaign_id")["order_id"].count().reset_index(name="Attributed orders")
    if not matched_df.empty else pd.DataFrame(columns=["campaign_id", "Attributed orders"])
)
campaign_view = campaign_df.merge(campaign_revenue, on="campaign_id", how="left")
campaign_view = campaign_view.merge(campaign_order_counts, on="campaign_id", how="left")
campaign_view["Attributed revenue"] = campaign_view["Attributed revenue"].fillna(0)
campaign_view["Attributed orders"] = campaign_view["Attributed orders"].fillna(0).astype(int)
campaign_view["ROAS"] = campaign_view.apply(
    lambda row: row["Attributed revenue"] / row["budget"] if row["budget"] > 0 else None,
    axis=1,
)
campaign_view["Campaign"] = campaign_view["campaign_name"].fillna("Unnamed campaign")
campaign_view = campaign_view[
    campaign_view["channel"].isin(selected_channels)
] if selected_channels else campaign_view.iloc[0:0]
campaign_view = campaign_view[
    campaign_view["campaign_name"].isin(selected_campaign_names)
] if selected_campaign_names else campaign_view.iloc[0:0]

if not campaign_view.empty:
    st.markdown("#### Campaign budget, revenue & ROAS comparison")
    graph_filter_col, graph_note_col = st.columns([1, 2.2])
    with graph_filter_col:
        campaign_display = st.selectbox(
            "Campaigns to display",
            options=["Top 5", "Top 10", "All campaigns"],
            index=0,
            key="campaign_graph_top_n",
            help="Ranks campaigns by budget-based ROAS within the current dashboard filters.",
        )

    # Rank on ROAS first, then show all three measures for the selected campaigns.
    ranked_graph_df = campaign_view.sort_values(
        "ROAS", ascending=False
    ).copy()
    if campaign_display == "Top 5":
        ranked_graph_df = ranked_graph_df.head(5)
    elif campaign_display == "Top 10":
        ranked_graph_df = ranked_graph_df.head(10)
    graph_df = ranked_graph_df.copy()

    st.markdown(
        '<p class="section-note">Compare entered campaign budget and attributed revenue in dollars, alongside budget-based ROAS on the right axis. Hover over each measure for campaign details.</p>',
        unsafe_allow_html=True,
    )

    # Grouped dollar bars + ROAS line on a separate axis avoids mixing dollars and ratios.
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    campaign_names = graph_df["Campaign"].astype(str).tolist()
    revenues = graph_df["Attributed revenue"].astype(float).tolist()
    budgets = graph_df["budget"].astype(float).tolist()
    roas_values = graph_df["ROAS"].astype(float).tolist()
    order_counts = graph_df["Attributed orders"].astype(int).tolist()

    fig.add_trace(
        go.Bar(
            name="Attributed revenue ($)",
            x=campaign_names,
            y=revenues,
            marker_color="#F05A3A",
            offsetgroup="money",
            customdata=list(zip(budgets, roas_values, order_counts)),
            hovertemplate=(
                "<b>%{x}</b><br>Attributed revenue: $%{y:,.2f}"
                "<br>Entered budget: $%{customdata[0]:,.2f}"
                "<br>ROAS: %{customdata[1]:.2f}x"
                "<br>Attributed orders: %{customdata[2]}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            name="Entered budget ($)",
            x=campaign_names,
            y=budgets,
            marker_color="#F2A65A",
            offsetgroup="money2",
            customdata=list(zip(revenues, roas_values, order_counts)),
            hovertemplate=(
                "<b>%{x}</b><br>Entered budget: $%{y:,.2f}"
                "<br>Attributed revenue: $%{customdata[0]:,.2f}"
                "<br>ROAS: %{customdata[1]:.2f}x"
                "<br>Attributed orders: %{customdata[2]}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            name="Budget-based ROAS (x)",
            x=campaign_names,
            y=roas_values,
            mode="lines+markers+text",
            text=[f"{value:.2f}x" if pd.notna(value) else "N/A" for value in roas_values],
            textposition="top center",
            textfont=dict(color="#2D211D", size=11),
            line=dict(color="#2D211D", width=3),
            marker=dict(color="#2D211D", size=9, line=dict(color="#D62828", width=2)),
            customdata=list(zip(revenues, budgets, order_counts)),
            hovertemplate=(
                "<b>%{x}</b><br>ROAS: %{y:.2f}x"
                "<br>Attributed revenue: $%{customdata[0]:,.2f}"
                "<br>Entered budget: $%{customdata[1]:,.2f}"
                "<br>Attributed orders: %{customdata[2]}<extra></extra>"
            ),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#2D211D", size=13),
        barmode="group",
        legend=dict(
            title_text="Campaign measures",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis_title=None,
        margin=dict(l=15, r=25, t=65, b=95),
        height=520 if len(graph_df) <= 5 else 620,
        hovermode="x unified",
    )
    fig.update_xaxes(
        tickfont=dict(color="#51443D"),
        gridcolor="rgba(255,255,255,.06)",
        tickangle=-20,
        automargin=True,
    )
    fig.update_yaxes(
        title_text="Amount ($)",
        tickprefix="$",
        tickfont=dict(color="#51443D"),
        gridcolor="rgba(255,255,255,.12)",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Budget-based ROAS (x)",
        ticksuffix="x",
        tickfont=dict(color="#2D211D", size=13),
        showgrid=False,
        secondary_y=True,
    )
    st.plotly_chart(fig, width="stretch")
    with st.expander("View campaign details"):
        details=campaign_view[["Campaign","channel","budget","Attributed revenue","Attributed orders","ROAS"]].copy()
        for name in ("budget","Attributed revenue"):
            details[name]=details[name].map(lambda value: f"${value:,.2f}")
        details["ROAS"]=details["ROAS"].map(lambda value: f"{value:.2f}x" if pd.notna(value) else "N/A")
        st.dataframe(details.rename(columns={"channel":"Channel","budget":"Planned budget"}),hide_index=True,width="stretch")
else:
    st.info("Create a campaign or select a channel to see campaign-level performance.")

# ---------------------------------------------------------
# ATTRIBUTION QUALITY
# ---------------------------------------------------------
st.divider()
st.subheader("Attribution quality")
status_summary = pd.DataFrame({
    "Status": ["Matched", "Unattributed", "Needs Review"],
    "Orders": [matched_orders, unattributed_orders, needs_review],
})
q1, q2 = st.columns([1, 1.4])
with q1:
    fig = px.pie(
        status_summary, names="Status", values="Orders", hole=.62,
        title="Order attribution breakdown",
        color="Status",
        color_discrete_map={"Matched": "#F05A3A", "Unattributed": "#F2A65A", "Needs Review": "#87569A"},
    )
    fig.update_layout(margin=dict(l=55, r=35, t=85, b=75), legend_title=None)
    fig.update_layout(
        template="plotly_white", paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(color="#2D211D", size=13),
        xaxis=dict(tickfont=dict(color="#51443D"), gridcolor="rgba(255,255,255,.12)"),
        yaxis=dict(tickfont=dict(color="#51443D"), gridcolor="rgba(255,255,255,.12)"),
    )
    st.plotly_chart(fig, width="stretch")
with q2:
    st.metric("Unattributed order rate", f"{unattributed_pct:.1f}%", help="Unattributed orders ÷ all selected orders × 100")
    st.metric("Needs Review Rate", f"{needs_review / total_orders * 100 if total_orders else 0:.1f}%", help="Orders needing review ÷ all selected orders × 100")
    st.info(
        "Matched = a campaign ID or promo code matches a saved campaign. "
        "Unattributed = no campaign identifier or promo code was recorded. Needs Review = tracking signals are invalid or conflicting."
    )


# ---------------------------------------------------------
# REVENUE TREND
# ---------------------------------------------------------
st.divider()
st.subheader("Revenue over time")
from dashboard_charts import revenue_chart
period = st.radio("Revenue grouping", ["Daily", "Weekly"], horizontal=True)
fig, note = revenue_chart(filtered_df.to_dict("records"), weekly=period == "Weekly")
st.plotly_chart(fig, width="stretch")
st.caption(note)


# ---------------------------------------------------------
# CUSTOMER FEEDBACK & SELF-REPORTED DISCOVERY INSIGHTS
# ---------------------------------------------------------
display_feedback_dashboard(filtered_df["order_id"].tolist())

from interaction_ui import apply_interactions
apply_interactions()
