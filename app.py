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
        pages=[st.Page("pages/owner_overview.py",title="Dashboard",default=True),
               st.Page("pages/marketing_dashboard.py",title="Analytics"),
               st.Page("pages/create_campaign.py",title="Create Campaign"),
               st.Page("pages/order_matching.py",title="Order Matching")]
    else:
        pages=[st.Page("pages/hot_sauce_store.py",title="HotVile Store",url_path="hot_sauce_store",default=True)]
    navigation = st.navigation(pages, position="hidden")
    if st.session_state.user_role == "Business Owner":
        with st.sidebar:
            st.markdown('<div class="sidebar-lockup"><div class="sidebar-monogram">HV</div><div><strong>HOTVILE</strong><small>Marketing intelligence</small></div></div>',unsafe_allow_html=True)
            st.divider()
            if st.session_state.user_role == "Business Owner":
                st.caption("OVERVIEW")
                st.page_link(pages[0],label="Dashboard",icon=":material/dashboard:")
                st.caption("MARKETING OPERATIONS")
                st.page_link(pages[2],label="Create Campaign",icon=":material/add_circle:")
                st.page_link(pages[3],label="Order Matching",icon=":material/fact_check:")
                st.page_link(pages[1],label="Analytics",icon=":material/bar_chart:")
            else:
                st.page_link(pages[0],label="HotVile Store",icon=":material/storefront:")
            st.divider()
            st.markdown('<div class="sidebar-profile">Business owner demo<small>No authentication · Fictional data</small></div>' if st.session_state.user_role == "Business Owner" else '<div class="sidebar-profile">HotVile customer<small>Demonstration store</small></div>',unsafe_allow_html=True)
            if st.button("Switch demo experience",width="stretch"):
                st.session_state.user_role=None
                st.session_state.campaign_tracking={}
                st.session_state.last_campaign_signature=None
                st.query_params.clear()
                st.rerun()
    navigation.run()
    if st.session_state.user_role == "Customer":
        with st.expander("Demo navigation"):
            if st.button("Switch demo experience",width="stretch"):
                st.session_state.user_role=None
                st.session_state.campaign_tracking={}
                st.session_state.last_campaign_signature=None
                st.query_params.clear()
                st.rerun()
    apply_interactions()
