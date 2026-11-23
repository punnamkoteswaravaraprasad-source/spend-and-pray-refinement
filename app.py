import streamlit as st
from attribution_engine import process_orders, calculate_kpis
from ui import apply_theme, image_data_uri
from interaction_ui import apply_interactions

st.set_page_config(page_title="Spend & Pray | HotVile", page_icon="H", layout="wide", initial_sidebar_state="auto")
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
    if st.session_state.user_role == "Business Owner":
        pages=[st.Page("pages/marketing_dashboard.py",title="Performance overview",default=True),
               st.Page("pages/create_campaign.py",title="Create Campaign"),
               st.Page("pages/order_matching.py",title="Order Matching")]
    else:
        pages=[st.Page("pages/hot_sauce_store.py",title="HotVile Store",url_path="hot_sauce_store",default=True)]
    navigation = st.navigation(pages, position="hidden")
    with st.sidebar:
        st.markdown("### HOTVILE")
        st.caption("SPEND & PRAY")
        st.divider()
        for page in pages:
            st.page_link(page, label=page.title)
        st.divider()
        st.caption(st.session_state.user_role)
        st.caption("Demo access · No authentication")
        if st.button("Switch demo experience",width="stretch"):
            st.session_state.user_role=None
            st.session_state.campaign_tracking={}
            st.session_state.last_campaign_signature=None
            st.query_params.clear()
            st.rerun()
    navigation.run()
    apply_interactions()
