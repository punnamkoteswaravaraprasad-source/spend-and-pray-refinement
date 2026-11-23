import csv
import io
import os
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from campaign_links import campaign_link
from urllib.parse import urlsplit
from data_store import append_unique
from reporting import amount

import qrcode
import streamlit as st

from ui import apply_theme, hero, page_steps, section_label


apply_theme()

# Page-specific HotVile dark theme. This intentionally overrides the generic
# light theme so the campaign builder matches the branded sidebar/storefront.
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(ellipse at 12% 4%, rgba(214,40,40,.20), transparent 34%),
                    radial-gradient(ellipse at 90% 20%, rgba(240,90,40,.10), transparent 30%),
                    linear-gradient(145deg, #FFF9F1 0%, #FFFFFF 56%, #FFF9F1 100%) !important;
        color: #2D211D !important;
    }
    .main .block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 4rem; }
    .campaign-portfolio-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin: .8rem 0 1rem;
    }
    .campaign-portfolio-card {
        min-height: 98px;
        box-sizing: border-box;
        padding: 1.1rem 1.25rem;
        background: linear-gradient(145deg, #FFFFFF 0%, #FFF2E8 100%);
        border: 1px solid rgba(255,145,95,.28);
        border-left: 5px solid #F05A3A;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(80,45,25,.08);
    }
    .campaign-portfolio-label {
        color: #6B5A51 !important;
        font-size: .9rem;
        font-weight: 600;
        margin-bottom: .45rem;
    }
    .campaign-portfolio-value {
        color: #2D211D !important;
        -webkit-text-fill-color: #2D211D !important;
        font-size: 1.9rem;
        line-height: 1.2;
        font-weight: 750;
    }
    @media (max-width: 760px) {
        .campaign-portfolio-grid { grid-template-columns: 1fr; }
    }
    .main .block-container h1, .main .block-container h2,
    .main .block-container h3, .main .block-container h4,
    .main .block-container p, .main .block-container span,
    .main .block-container label, .main .block-container [data-testid=stMarkdownContainer],
    .main .block-container [data-testid=stCaptionContainer] {
        color: #2D211D;
    }
    .main .block-container [data-testid=stCaptionContainer] { color: #6B5A51 !important; }
    .main .block-container h3 { color: #2D211D !important; }
    /* Campaign portfolio metric cards: style the outer card and Streamlit's inner wrappers. */
    .main .block-container div[data-testid="stMetric"],
    .main .block-container div[data-testid="stMetric"] > div,
    .main .block-container div[data-testid="stMetric"] > div > div {
        background: linear-gradient(145deg, #FFFFFF 0%, #FFF2E8 100%) !important;
        background-color: #FFFFFF !important;
        border: 1px solid rgba(255,145,95,.28) !important;
        border-left: 5px solid #F05A3A !important;
        border-radius: 16px !important;
        padding: 1rem 1.1rem !important;
        box-shadow: 0 12px 28px rgba(0,0,0,.22) !important;
    }
    .main .block-container div[data-testid="stMetric"] * {
        color: #2D211D !important;
        -webkit-text-fill-color: #2D211D !important;
    }
    .main .block-container div[data-testid="stMetric"] label,
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricLabel"] * {
        color: #6B5A51 !important;
        -webkit-text-fill-color: #6B5A51 !important;
    }
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricValue"],
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
        color: #2D211D !important;
        -webkit-text-fill-color: #2D211D !important;
        font-size: 1.9rem !important;
        font-weight: 750 !important;
    }
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricDelta"],
    .main .block-container div[data-testid="stMetric"] [data-testid="stMetricDelta"] * {
        color: #F2A65A !important;
        -webkit-text-fill-color: #F2A65A !important;
    }
    [data-testid=stForm] {
        background: linear-gradient(150deg, rgba(255,255,255,.98), rgba(255,249,241,.98)) !important;
        border: 1px solid rgba(255,145,95,.22) !important;
        border-top: 5px solid #F05A3A !important;
        border-radius: 18px; padding: 1.3rem;
        box-shadow: 0 14px 32px rgba(0,0,0,.28);
    }
    [data-testid=stVerticalBlockBorderWrapper] {
        background: rgba(42,30,26,.96) !important;
        border: 1px solid rgba(255,145,95,.20) !important;
        border-radius: 16px;
    }
    [data-baseweb=tab-list] {
        gap: .45rem; background: rgba(255,255,255,.98) !important;
        padding: .4rem; border: 1px solid rgba(255,145,95,.18);
        border-radius: 14px;
    }
    [data-baseweb=tab] { color: #E9D9CE !important; font-weight: 800; }
    [data-baseweb=tab][aria-selected=true] {
        background: linear-gradient(135deg,#D62828,#F05A28) !important;
        color: #FFFFFF !important; border-radius: 10px;
    }
    [data-baseweb=tab][aria-selected=true] * { color: #FFFFFF !important; }
    /* Form labels and helper text */
    [data-testid=stWidgetLabel] p, [data-testid=stWidgetLabel] label,
    .stTextInput label, .stSelectbox label, .stDateInput label,
    .stNumberInput label, [data-testid=stMarkdownContainer] p {
        color: #F5E9DF !important;
    }
    [data-testid=stTextInput] input, [data-testid=stNumberInput] input,
    [data-testid=stDateInput] input, [data-baseweb=select] > div {
        background: #FFFFFF !important; color: #2D211D !important;
        border-color: rgba(255,180,130,.35) !important;
        border-radius: 9px !important;
    }
    [data-baseweb=select] input { color: #2D211D !important; }
    [data-baseweb=select] svg { fill: #2D211D !important; }
    [data-testid=stTextInput] input::placeholder { color: #B9AAA0 !important; }
    [data-testid=stAlert] {
        background: rgba(37,49,67,.95) !important;
        border: 1px solid rgba(130,170,220,.25) !important;
        color: #EAF2FF !important;
    }
    [data-testid=stAlert] * { color: #EAF2FF !important; }
    div.stButton > button, div.stLinkButton > a,
    [data-testid=stFormSubmitButton] > button,
    [data-testid=stDownloadButton] > button {
        border-radius: 10px; font-weight: 800; min-height: 2.7rem;
    }
    div.stButton > button[kind=primary],
    [data-testid=stFormSubmitButton] > button[kind=primary] {
        background: linear-gradient(90deg,#D62828,#F05A28) !important;
        color: #FFFFFF !important; border: 0 !important;
        box-shadow: 0 8px 20px rgba(211,48,35,.24);
    }
    [data-testid=stExpander] {
        background: rgba(43,31,27,.96) !important;
        border: 1px solid rgba(255,145,95,.22) !important;
        border-radius: 14px;
    }
    [data-testid=stExpander] summary, [data-testid=stExpander] summary * {
        color: #2D211D !important;
    }
    .brand-hero { margin-bottom: 1.4rem; }

    /* Ready-to-share asset presentation */
    .share-summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: .8rem;
        margin: .7rem 0 1rem;
    }
    .share-summary-card {
        background: linear-gradient(145deg, #FFFFFF 0%, #FFF2E8 100%);
        border: 1px solid rgba(255,145,95,.28);
        border-left: 5px solid #F05A3A;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        min-width: 0;
    }
    .share-summary-label {
        color: #6B5A51 !important;
        font-size: .84rem;
        font-weight: 650;
        margin-bottom: .4rem;
    }
    .share-summary-value {
        color: #2D211D !important;
        -webkit-text-fill-color: #2D211D !important;
        font-size: 1.35rem;
        line-height: 1.25;
        font-weight: 800;
        overflow-wrap: anywhere;
    }
    .share-asset-label {
        color: #2D211D !important;
        font-weight: 750;
        margin: .9rem 0 .35rem;
    }
    .share-note {
        color: #6B5A51 !important;
        font-size: .84rem;
        margin-top: .35rem;
    }
    [data-testid="stCodeBlock"] {
        background: #FFFFFF !important;
        border: 1px solid rgba(255,180,130,.28) !important;
        border-radius: 10px !important;
    }
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code {
        color: #2D211D !important;
        white-space: pre-wrap !important;
        overflow-wrap: anywhere !important;
    }
    .share-qr-panel {
        background: linear-gradient(145deg, #FFFFFF 0%, #FFF2E8 100%);
        border: 1px solid rgba(255,145,95,.28);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
    }
    @media (max-width: 760px) {
        .share-summary-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGNS_FILE = DATA_DIR / "campaigns.csv"

CAMPAIGN_FIELDS = [
    "campaign_id",
    "campaign_name",
    "channel",
    "start_date",
    "end_date",
    "budget",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "tracking_url",
    "promo_code",
    "created_at",
]

def configured_app_url():
    """Return the public app URL when configured, otherwise the current browser URL."""
    configured = os.getenv("APP_BASE_URL", "").strip()
    if not configured:
        try:
            configured = str(st.secrets.get("APP_BASE_URL", "")).strip()
        except Exception:
            configured = ""
    return configured.rstrip("/") if configured else (st.context.url or "")


def current_campaign_link(campaign):
    return campaign_link(campaign, configured_app_url())


CHANNEL_DETAILS = {
    "Paid Social": ("📱", "Track a paid social advertisement or promoted post."),
    "Influencer": ("🎥", "Track a creator partnership or influencer promotion."),
    "Farmers Market": ("🧺", "Use a QR code or promo code at an in-person market."),
    "Pop-up Event": ("🏪", "Track a temporary retail event or product activation."),
}


def load_campaigns():
    if not CAMPAIGNS_FILE.exists():
        return []
    with open(CAMPAIGNS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def save_campaign(campaign):
    append_unique(CAMPAIGNS_FILE, CAMPAIGN_FIELDS, campaign, 'campaign_id')



def generate_qr_code(url):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#251b18", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def campaign_status(campaign):
    try:
        start = date.fromisoformat(campaign.get("start_date") or "")
        end = date.fromisoformat(campaign.get("end_date") or "")
    except ValueError:
        return "Date unavailable"
    today = date.today()
    if today < start:
        return "Upcoming"
    if today > end:
        return "Completed"
    return "Active"


campaigns = load_campaigns()
total_budget = 0.0
for saved_campaign in campaigns:
    try:
        total_budget += float(saved_campaign.get("budget") or 0)
    except (ValueError, TypeError):
        pass

active_campaigns = sum(
    1 for saved_campaign in campaigns
    if campaign_status(saved_campaign) == "Active"
)

hero(
    "Build a trackable campaign",
    "Create only the information the founder knows, then let the prototype generate the technical tracking assets automatically.",
    "Campaign Builder",
    icon="📣",
)

page_steps([
    ("🎯", "Choose", "Select the channel, dates, and planned budget."),
    ("⚙️", "Generate", "Create the tracking link, QR code, and promo code."),
    ("🚀", "Share", "Use the campaign assets in the selected channel."),
])

section_label("Campaign portfolio")
st.markdown(
    f"""
    <div class="campaign-portfolio-grid">
      <div class="campaign-portfolio-card">
        <div class="campaign-portfolio-label">Saved Campaigns</div>
        <div class="campaign-portfolio-value">{len(campaigns)}</div>
      </div>
      <div class="campaign-portfolio-card">
        <div class="campaign-portfolio-label">Active Campaigns</div>
        <div class="campaign-portfolio-value">{active_campaigns}</div>
      </div>
      <div class="campaign-portfolio-card">
        <div class="campaign-portfolio-label">Total Planned Budget</div>
        <div class="campaign-portfolio-value">${total_budget:,.2f}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

active_app_url = configured_app_url()
current_host = urlsplit(active_app_url).hostname
if current_host in ('127.0.0.1', 'localhost', '::1'):
    st.info(
        "You're running locally, so campaign links currently use localhost. "
        "To generate shareable links, set APP_BASE_URL to your deployed "
        "Streamlit HTTPS address in .streamlit/secrets.toml or your hosting secrets."
    )

create_tab, saved_tab = st.tabs(["Create Campaign", "Saved Campaigns"])

with create_tab:
    st.markdown("### Campaign details")
    st.caption("The founder enters five business fields. Tracking IDs and link parameters are generated by the system.")

    with st.form("create_campaign_form"):
        campaign_name = st.text_input(
            "Campaign Name",
            placeholder="Fall Farmers Market Promotion",
        )
        channel = st.selectbox(
            "Marketing Channel",
            list(CHANNEL_DETAILS.keys()),
        )
        icon, channel_description = CHANNEL_DETAILS[channel]
        st.info(f"{icon} {channel_description}")

        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input("Start Date", value=date.today())
        with date_col2:
            end_date = st.date_input("End Date", value=date.today())

        budget = st.number_input(
            "Planned Campaign Budget ($)",
            min_value=0.0,
            value=50.0,
            step=10.0,
            help="Enter the planned or allocated budget. This is not confirmed advertising expenditure.",
        )

        create_button = st.form_submit_button(
            "Create Campaign Assets",
            type="primary",
            width="stretch",
        )

    if create_button:
        if not campaign_name.strip():
            st.error("Enter a campaign name.")
        elif any((c.get('campaign_name') or '').strip().casefold() == campaign_name.strip().casefold()
                 and c.get('channel') == channel and c.get('start_date') == str(start_date)
                 and c.get('end_date') == str(end_date) and amount(c.get('budget')) == budget
                 for c in campaigns):
            st.error('This campaign already exists. Open Saved Campaigns to use its sharing assets.')
        elif end_date < start_date:
            st.error("The end date cannot be before the start date.")
        else:
            campaign_id = "CMP-" + uuid.uuid4().hex[:8].upper()
            source_mapping = {
                "Paid Social": "paid_social",
                "Influencer": "influencer",
                "Farmers Market": "farmers_market",
                "Pop-up Event": "popup_event",
            }
            medium_mapping = {
                "Paid Social": "paid_social",
                "Influencer": "influencer",
                "Farmers Market": "qr",
                "Pop-up Event": "qr",
            }
            utm_source = source_mapping[channel]
            utm_medium = medium_mapping[channel]
            utm_campaign = "_".join(campaign_name.strip().lower().split())
            promo_code = "HOT" + uuid.uuid4().hex[:6].upper()
            tracking_params = {
                "campaign_id": campaign_id,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
            }
            tracking_url = current_campaign_link(tracking_params)

            campaign = {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name.strip(),
                "channel": channel,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "budget": round(budget, 2),
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_campaign": utm_campaign,
                "tracking_url": tracking_url,
                "promo_code": promo_code,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            save_campaign(campaign)
            st.session_state.last_campaign = campaign
            st.rerun()

    if st.session_state.get("last_campaign"):
        campaign = st.session_state.last_campaign
        st.markdown("### Ready to share")
        st.caption("Your campaign assets are ready. Copy the promo code or tracking link, or download the QR code.")

        share_url = current_campaign_link(campaign)
        details_col, qr_col = st.columns([1.45, 1], gap="large")

        with details_col:
            with st.container(border=True):
                st.markdown(f"**{campaign['campaign_name']}**")

                st.markdown(
                    f"""
                    <div class="share-summary-grid">
                      <div class="share-summary-card">
                        <div class="share-summary-label">Marketing Channel</div>
                        <div class="share-summary-value">{campaign['channel']}</div>
                      </div>
                      <div class="share-summary-card">
                        <div class="share-summary-label">Planned Budget</div>
                        <div class="share-summary-value">${float(campaign['budget']):,.2f}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("Internal reference"):
                    st.code(campaign["campaign_id"], language=None)

                st.markdown('<div class="share-asset-label">Customer Promo Code</div>', unsafe_allow_html=True)
                st.code(campaign["promo_code"], language=None)
                st.caption("Use this code at checkout. The copy button is available on the code block.")

                st.markdown('<div class="share-asset-label">Customer Tracking Link</div>', unsafe_allow_html=True)
                st.code(share_url, language=None)
                st.caption("The tracking link includes this campaign's ID and UTM parameters.")

                st.link_button(
                    "Open Customer Store",
                    share_url,
                    width="stretch",
                )

        with qr_col:
            with st.container(border=True):
                st.markdown("**Campaign QR Code**")
                qr_bytes = generate_qr_code(share_url)
                st.image(qr_bytes, width="stretch")
                st.download_button(
                    "⬇ Download QR Code",
                    data=qr_bytes,
                    file_name=f"{campaign['campaign_id']}.png",
                    mime="image/png",
                    width="stretch",
                    type="primary",
                )
                st.caption("Scan this code to open the customer store with campaign tracking.")

        if current_host in ("127.0.0.1", "localhost", "::1"):
            st.warning(
                "This QR code currently points to localhost and will only work on this computer. "
                "Configure APP_BASE_URL with your public HTTPS Streamlit URL before sharing it."
            )

with saved_tab:
    st.markdown("### Campaign portfolio")
    st.caption("Only decision-relevant campaign fields are shown. Technical UTM values remain in the backend.")

    if not campaigns:
        st.info("No campaigns have been created yet.")
    else:
        for saved_campaign in reversed(campaigns):
            status = campaign_status(saved_campaign)
            with st.container(border=True):
                name_col, channel_col, budget_col, status_col = st.columns(
                    [2.6, 1.5, 1.2, 1.2]
                )
                name_col.write(f"**{saved_campaign.get('campaign_name', 'Unnamed')}**")
                channel_col.write(saved_campaign.get("channel", "—"))
                try:
                    display_budget = float(saved_campaign.get("budget") or 0)
                except (ValueError, TypeError):
                    display_budget = 0
                budget_col.write(f"${display_budget:,.2f}")
                status_col.write(status)

                with st.expander("View sharing assets"):
                    st.write(f"Promo Code: `{saved_campaign.get('promo_code', '')}`")
                    st.code(current_campaign_link(saved_campaign), language=None)
                    st.image(generate_qr_code(current_campaign_link(saved_campaign)), width=180)
                    st.download_button('Download QR', generate_qr_code(current_campaign_link(saved_campaign)),
                                       file_name=f"{saved_campaign['campaign_id']}.png", mime='image/png', key=f"qr_{saved_campaign['campaign_id']}")
                    st.link_button(
                        "Open Store",
                        current_campaign_link(saved_campaign),
                    )

st.caption("Campaign budget is planned spending. The dashboard reports budget-based, not profit-based, ROAS.")

from interaction_ui import apply_interactions
apply_interactions()
