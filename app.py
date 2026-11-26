from branding import logo_html
import streamlit as st
from attribution_engine import process_orders, calculate_kpis
from ui import apply_theme, image_data_uri
from interaction_ui import apply_interactions

st.set_page_config(page_title="HotVile | Hot Sauce Co.", page_icon="H", layout="wide", initial_sidebar_state="auto")
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
    st.markdown('<span class="hotvile-landing-marker"></span><div class="landing-announcement">SMALL BATCH. BIG FLAVOR. THIS IS HOTVILE.</div>',unsafe_allow_html=True)
    brand,owner_entry=st.columns([3,1],vertical_alignment="center")
    with brand:
        st.markdown(logo_html(),unsafe_allow_html=True)
    with owner_entry:
        if st.button("Enter Business Owner View →",width="stretch"): enter("Business Owner")
    with st.container(key="hotvile_landing_hero"):
        story,visual=st.columns([1.05,1],gap="large",vertical_alignment="center")
        with story:
            st.markdown('<div class="landing-eyebrow">THIS IS HOTVILE.</div><h1 class="landing-headline">SMALL BATCH.<br><span class="flavor-orange">BIG FLAVOR.</span></h1><p class="landing-intro">Six bold sauces. From your first kick to your next obsession.</p>',unsafe_allow_html=True)
            if st.button("Shop HotVile sauces →",type="primary",width="stretch"): enter("Customer")
            st.markdown('<div class="landing-hero-notes">SIX SIGNATURE SAUCES <span>•</span> MILD TO EXTRA HOT</div>',unsafe_allow_html=True)
        with visual:
            st.markdown(f'<div class="landing-burst-stage"><img class="landing-lifestyle" src="{image_data_uri("images/hotvile-launch-burst.png")}" alt="HotVile sauce collection in a bright product launch display"><span class="landing-heat-stamp">FIND YOUR<br>HEAT.</span></div>',unsafe_allow_html=True)
    st.markdown('<section class="landing-collection-intro"><span>THE HOTVILE LINEUP</span><h2>A little heat. A lot of personality.</h2><p>Start with an everyday classic, go sweet and fiery, or turn up the heat.</p></section>',unsafe_allow_html=True)
    from catalog import PRODUCTS
    choices=st.columns(3,gap="large")
    for column,product in zip(choices,[PRODUCTS[0],PRODUCTS[1],PRODUCTS[5]]):
        with column:
            photo=image_data_uri(product['image'])
            st.markdown(f'''<article class="landing-flavor"><div class="landing-flavor-photo"><img src="{photo}" alt="HotVile {product['name']} branded sauce bottle"></div><div class="landing-flavor-details"><small>{product['heat'].upper()} HEAT</small><h3>{product['name']}</h3><p>{product['description']}</p></div></article>''',unsafe_allow_html=True)
    with st.container(key="landing_owner_band"):
        description,action=st.columns([2.5,1],vertical_alignment="center")
        with description:
            st.markdown('<div class="landing-eyebrow">BEHIND THE FLAVOR</div><h3>A clearer view of the business.</h3><p>Spend &amp; Pray is HotVile’s marketing workspace. Connect campaigns with orders and see which results need a closer look.</p>',unsafe_allow_html=True)
        with action:
            if st.button("Open owner workspace",width="stretch"): enter("Business Owner")
    st.caption("Academic demonstration · Fictional products and orders · No real payments · Use fictional details")

else:
    if st.session_state.user_role == "Business Owner":
        pages=[st.Page("pages/owner_overview.py",title="Business Process",default=True),
               st.Page("pages/order_matching.py",title="Order Matching"),
               st.Page("pages/marketing_dashboard.py",title="Marketing Dashboard"),
               st.Page("pages/create_campaign.py",title="Create Campaign")]
    else:
        pages=[st.Page("pages/hot_sauce_store.py",title="HotVile Store",url_path="hot_sauce_store",default=True)]
    navigation = st.navigation(pages, position="hidden")
    if st.session_state.user_role == "Business Owner":
        with st.sidebar:
            st.markdown(logo_html(),unsafe_allow_html=True)
            st.divider()
            owner_links=[(pages[0],"Business Process",":material/route:"),
                         (pages[3],"Create Campaign",":material/campaign:"),
                         (pages[1],"Order Matching",":material/fact_check:"),
                         (pages[2],"Marketing Dashboard",":material/bar_chart:")]
            for index,(page,label,icon) in enumerate(owner_links):
                with st.container(border=True,key=f"owner_nav_block_{index}"):
                    st.page_link(page,label=label,icon=icon)
                if index<len(owner_links)-1: st.divider()
            st.divider()
            st.markdown('<div class="sidebar-role">Business Owner</div>',unsafe_allow_html=True)
            if st.button("Customer Experience",width="stretch"):
                st.session_state.user_role="Customer"
                st.session_state.campaign_tracking={}
                st.session_state.last_campaign_signature=None
                st.query_params.clear()
                st.rerun()
    navigation.run()
    if st.session_state.user_role == "Customer":
        with st.expander("Customer Experience"):
            if st.button("Business Owner",width="stretch"):
                st.session_state.user_role="Business Owner"
                st.session_state.campaign_tracking={}
                st.session_state.last_campaign_signature=None
                st.query_params.clear()
                st.rerun()
    apply_interactions()
