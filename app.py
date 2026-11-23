import streamlit as st
from attribution_engine import process_orders, calculate_kpis
from ui import apply_theme, image_data_uri
from interaction_ui import apply_interactions

st.set_page_config(page_title="Spend & Pray | HotVile", page_icon="H", layout="wide", initial_sidebar_state="collapsed")
apply_theme()
apply_interactions()
st.session_state.setdefault("user_role", None)
st.session_state.setdefault("campaign_tracking", {})
keys = ("campaign_id", "utm_source", "utm_medium", "utm_campaign")
if any(k in st.query_params for k in keys):
    incoming = {k: st.query_params.get(k, "") for k in keys}
    signature = tuple(incoming.values())
    if st.session_state.get("last_campaign_signature") != signature:
        st.session_state.user_role = "Customer"
        st.session_state.last_campaign_signature = signature
    st.session_state.campaign_tracking = incoming

def enter(role):
    st.session_state.user_role = role
    st.rerun()

def owner_home():
    rows, campaigns = process_orders()
    metrics = calculate_kpis(rows)
    st.caption("HOTVILE / OWNER WORKSPACE")
    st.title("Your marketing, connected.")
    st.write("See what sold, where tracking is missing, and which campaigns to review next.")
    st.info("Demo workspace · Fictional seed data and demonstration orders. No real payments or authentication.")
    a,b,c,d = st.columns(4)
    a.metric("Total revenue", f"${metrics['total_revenue']:,.2f}")
    b.metric("Orders", metrics['total_orders'])
    c.metric("Attribution coverage", f"{metrics['coverage']:.1f}%")
    d.metric("Orders needing attention", metrics['unattributed_orders'] + metrics['needs_review'])
    st.subheader("Choose your next action")
    for path,title,copy in [
        ("pages/create_campaign.py","Create a campaign","Set your budget and generate a tracking link, promo code, and QR code."),
        ("pages/order_matching.py","Review order matching","Check missing or conflicting tracking signals and record a review decision."),
        ("pages/marketing_dashboard.py","Explore performance","Compare channels, campaign returns, and customer feedback.")]:
        with st.container(border=True):
            st.page_link(path,label=title)
            st.caption(copy)
    with st.expander("How the demo works"):
        st.write("Create a campaign → share its link → place a demo order → review attribution → compare results.")
        st.write("Budget-based ROAS compares matched revenue with planned budget. It does not measure profit or prove that marketing caused a sale.")

if st.session_state.user_role is None:
    # Register the welcome route too, disabling legacy automatic pages discovery.
    st.navigation([st.Page(lambda: None, title="Welcome", default=True)], position="hidden").run()
    left,right=st.columns([1.35,1],gap="large",vertical_alignment="center")
    with left:
        banner=image_data_uri("images/companybanner.png")
        st.markdown(f'''<section class="welcome-panel">
          <div class="welcome-wordmark">HOTVILE <span>× SPEND &amp; PRAY</span></div>
          <p class="welcome-kicker">BOLD FLAVOR. CLEARER DECISIONS.</p>
          <h1>Know what brings<br>customers to your store.</h1>
          <p>Connect campaigns, customer orders, and feedback in one focused workspace.</p>
          <img src="{banner}" alt="The six branded HotVile sauce bottles" />
          <div class="welcome-features"><span>Campaign tracking</span><span>Order attribution</span><span>Customer insights</span></div>
        </section>''',unsafe_allow_html=True)
    with right:
        with st.container(border=True,key="entry_card"):
            st.caption("SPEND & PRAY / INTERACTIVE DEMO")
            st.header("Welcome to HotVile")
            st.write("Choose an experience to get started.")
            st.markdown("#### Shop the sauce collection")
            st.caption("Find your heat, build a cart, and try a demonstration checkout.")
            if st.button("Enter Customer Store →",type="primary",width="stretch"): enter("Customer")
            st.divider()
            st.markdown("#### Explore the owner workspace")
            st.caption("Create campaigns, review order matches, and compare performance.")
            if st.button("Enter Business Owner View →",width="stretch"): enter("Business Owner")
            st.caption("Demo access · No authentication · Use fictional customer details only.")
else:
    with st.sidebar:
        st.markdown("### HOTVILE")
        st.caption("SPEND & PRAY")
        st.divider()
        st.write(st.session_state.user_role)
        st.caption("Demo access · No authentication")
        if st.button("Switch demo experience",width="stretch"):
            st.session_state.user_role=None
            st.session_state.campaign_tracking={}
            st.session_state.last_campaign_signature=None
            st.query_params.clear()
            st.rerun()
    if st.session_state.user_role == "Business Owner":
        pages=[st.Page(owner_home,title="Owner Overview",default=True),
               st.Page("pages/create_campaign.py",title="Create Campaign"),
               st.Page("pages/order_matching.py",title="Order Matching"),
               st.Page("pages/marketing_dashboard.py",title="Marketing Dashboard")]
    else:
        pages=[st.Page("pages/hot_sauce_store.py",title="HotVile Store",url_path="hot_sauce_store",default=True)]
    st.navigation(pages).run()
    apply_interactions()
