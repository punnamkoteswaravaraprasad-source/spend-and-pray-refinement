from branding import logo_html
import base64
import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from components.customer_feedback import display_customer_feedback


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="HotVile | Hot Sauce Store",
    page_icon=None,
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = DATA_DIR / "demo_orders.csv"
BANNER_FILE = BASE_DIR / "images" / "companybanner.png"


# ---------------------------------------------------------
# BRAND STYLING — PREMIUM HOT SAUCE STOREFRONT
# ---------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800&display=swap');

        .stApp {
            background:
                radial-gradient(ellipse at 15% 0%, rgba(214,40,40,.16), transparent 34%),
                linear-gradient(180deg, #FFF9F1 0%, #FFFFFF 48%, #FFF9F1 100%);
        }
        .block-container {
            max-width: 1280px;
            padding-top: 1.3rem;
            padding-bottom: 3.5rem;
        }
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }
        h1, h2, h3 { font-family: 'DM Sans', sans-serif; }
        .brand-topline {
            display:flex; align-items:center; justify-content:space-between;
            padding: 4px 0 18px; border-bottom: 1px solid rgba(95,60,40,.13);
            margin-bottom: 26px;
        }
        .brand-logo {
            color:#2D211D; font-weight:900; font-size:1.15rem;
            letter-spacing:.16em;
        }
        .brand-logo span { color:#F04432; }
        .brand-tag {
            color:#625148; font-size:.72rem; letter-spacing:.18em;
            text-transform:uppercase;
        }
        .six-sauce-banner {
            width: 100%;
            margin: 0 0 28px;
            overflow: hidden;
            border-radius: 22px;
            border: 1px solid rgba(255,255,255,.16);
            box-shadow: 0 22px 65px rgba(0,0,0,.42);
            background: #FFF9F1;
        }
        .six-sauce-banner img {
            display: block;
            width: 100%;
            height: auto;
            object-fit: contain;
        }
        .section-kicker {
            color:#A92E2E; font-size:.72rem; font-weight:800;
            letter-spacing:.18em; text-transform:uppercase;
        }
        .section-heading {
            color:#2D211D; font-size:2rem; font-weight:800;
            letter-spacing:-.04em; margin:.15rem 0 .25rem;
        }
        .section-copy { color:#625148; margin-bottom:1.1rem; }
        .product-card {
            background:linear-gradient(155deg,#FFF9F0 0%,#F0E3D4 100%);
            color:#FFFFFF; border-radius:20px; padding:20px;
            border:1px solid rgba(255,255,255,.4);
            box-shadow:0 14px 32px rgba(0,0,0,.22);
            min-height:300px; margin-bottom:10px;
            transition:transform .2s ease, box-shadow .2s ease;
        }
        .bottle-stage {
            height:190px; border-radius:15px; display:flex;
            align-items:center; justify-content:center; overflow:hidden;
            background:#FFFFFF; margin-bottom:16px; position:relative;
        }
        .product-photo-stage { padding:0; }
        .product-photo {
            width:100%; height:100%; object-fit:cover; display:block;
            transition:transform .35s ease;
        }
        .product-card:hover .product-photo { transform:scale(1.06); }
        /* Product images: shorter, contained, and consistently sized. */
        div[data-testid="stImage"] img {
            max-height: 270px !important;
            width: 100% !important;
            object-fit: contain !important;
            background: #FFFFFF;
            border-radius: 12px;
        }
        /* Heat-reactive glow around the complete product card and bottle photo. */
        .st-key-sauce_card_1, .st-key-sauce_card_2, .st-key-sauce_card_3,
        .st-key-sauce_card_4, .st-key-sauce_card_5, .st-key-sauce_card_6 {
            border-radius: 18px;
            padding: 10px;
            border: 1px solid rgba(95,60,40,.13);
            background: #FFFFFF;
            transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
        }
        .st-key-sauce_card_1:hover,
        .st-key-sauce_card_2:hover,
        .st-key-sauce_card_3:hover, .st-key-sauce_card_4:hover,
        .st-key-sauce_card_5:hover, .st-key-sauce_card_6:hover {
            transform: translateY(-5px);
        }
        .st-key-sauce_card_1 [data-testid="stImage"] img,
        .st-key-sauce_card_2 [data-testid="stImage"] img,
        .st-key-sauce_card_3 [data-testid="stImage"] img,
        .st-key-sauce_card_4 [data-testid="stImage"] img,
        .st-key-sauce_card_5 [data-testid="stImage"] img,
        .st-key-sauce_card_6 [data-testid="stImage"] img {
            border-radius: 13px;
            transition: transform .3s ease, filter .3s ease;
        }
        /* Classic Red — medium, warm red-orange glow. */
        .st-key-sauce_card_1:hover {
            border-color: rgba(255,105,48,.82);
            box-shadow: 0 0 12px rgba(255,89,35,.35), 0 0 28px rgba(255,89,35,.22);
        }
        .st-key-sauce_card_1:hover [data-testid="stImage"] img {
            transform: scale(1.025);
            filter: drop-shadow(0 0 9px rgba(255,91,36,.72));
        }
        /* Mango Habanero — strongest, vivid hot-orange glow. */
        .st-key-sauce_card_2:hover {
            border-color: rgba(255,75,25,.98);
            box-shadow: 0 0 16px rgba(255,65,15,.52), 0 0 36px rgba(255,65,15,.32);
        }
        .st-key-sauce_card_2:hover [data-testid="stImage"] img {
            transform: scale(1.035);
            filter: drop-shadow(0 0 14px rgba(255,65,15,.95));
        }
        /* Smoky Chipotle — soft amber ember glow. */
        .st-key-sauce_card_3:hover, .st-key-sauce_card_4:hover,
        .st-key-sauce_card_5:hover, .st-key-sauce_card_6:hover {
            border-color: rgba(255,159,72,.62);
            box-shadow: 0 0 8px rgba(255,145,55,.24), 0 0 19px rgba(255,145,55,.15);
        }
        .st-key-sauce_card_3:hover [data-testid="stImage"] img {
            transform: scale(1.02);
            filter: drop-shadow(0 0 7px rgba(255,151,65,.55));
        }
        @media (prefers-reduced-motion: reduce) {
            .st-key-sauce_card_1, .st-key-sauce_card_2, .st-key-sauce_card_3,
            .st-key-sauce_card_4, .st-key-sauce_card_5, .st-key-sauce_card_6,
            .st-key-sauce_card_1 [data-testid="stImage"] img,
            .st-key-sauce_card_2 [data-testid="stImage"] img,
            .st-key-sauce_card_3 [data-testid="stImage"] img,
        .st-key-sauce_card_4 [data-testid="stImage"] img,
        .st-key-sauce_card_5 [data-testid="stImage"] img,
        .st-key-sauce_card_6 [data-testid="stImage"] img {
                transition: none;
            }
        }
        /* Product cards sit on the dark storefront, so use high-contrast type. */
        .product-name {
            color:#2D211D !important; font-size:1.16rem; font-weight:850;
            letter-spacing:-.02em; margin:8px 0 5px;
        }
        .product-detail {
            color:#625148 !important; font-size:.9rem; line-height:1.5;
            min-height:42px;
        }
        .product-bottom {
            display:flex; justify-content:space-between; align-items:center;
            margin-top:12px; border-top:1px solid rgba(255,255,255,.2); padding-top:12px;
        }
        .product-price { color:#FF6248 !important; font-size:1.4rem; font-weight:900; }
        .heat-pill {
            background:#FFE0CC; color:#7F1D13; border-radius:30px;
            padding:5px 10px; font-size:.72rem; font-weight:800;
        }
        div[data-testid="stMetric"] {
            background:#2D211D; border:1px solid #E8DCCF;
            border-radius:14px; padding:12px 16px;
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
            color:#202020 !important; opacity:1 !important;
        }
        .prototype-note {
            background:rgba(255,248,239,.08); border:1px solid rgba(255,248,239,.18);
            border-radius:12px; padding:11px 15px; color:#625148;
            margin:15px 0 26px; font-size:.9rem;
        }
        div.stButton > button {
            border-radius:10px; font-weight:800; min-height:42px;
        }
        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            background:linear-gradient(90deg,#D62828,#F05A28);
            border:0; color:white;
        }
        div[data-testid="stExpander"] {
            border:1px solid rgba(255,255,255,.15);
            border-radius:12px; background:rgba(255,255,255,.035);
        }
        /* -------------------------------------------------
           HOTVILE STORE REFINEMENT
           ------------------------------------------------- */
        .six-sauce-banner {
            max-width: 1000px;
            margin: 0 auto 22px;
            border-radius: 18px;
            box-shadow: 0 18px 48px rgba(0,0,0,.34);
        }
        .six-sauce-banner img {
            max-height: 390px;
            object-fit: contain;
        }
        .store-kicker {
            color: #A92E2E;
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .2em;
            text-transform: uppercase;
            margin-top: 4px;
        }
        .store-title {
            color: #2D211D;
            font-size: clamp(2.3rem, 4vw, 3.35rem);
            font-weight: 900;
            letter-spacing: -.045em;
            margin: .15rem 0 .2rem;
        }
        .store-subtitle {
            color: #625148;
            font-size: 1.02rem;
            margin-bottom: 0;
        }
        .section-heading { margin-top: .2rem; }
        div[data-testid="stImage"] {
            background: rgba(255,248,239,.035);
            border-radius: 14px;
            padding: 5px;
        }
        .st-key-sauce_card_1, .st-key-sauce_card_2, .st-key-sauce_card_3,
        .st-key-sauce_card_4, .st-key-sauce_card_5, .st-key-sauce_card_6 {
            min-height: 100%;
            display: flex;
            flex-direction: column;
        }
        .sauce-card-copy { padding: 2px 2px 8px; }
        .product-detail { min-height: 54px; }
        .heat-pill { white-space: nowrap; }
        .empty-cart-panel {
            padding: 24px 26px;
            border-radius: 16px;
            border: 1px solid rgba(255,130,78,.28);
            background: linear-gradient(115deg, rgba(214,40,40,.12), rgba(255,248,239,.035));
            color: #625148;
        }
        .empty-cart-title {
            color: #2D211D;
            font-size: 1.05rem;
            font-weight: 800;
            margin-bottom: 5px;
        }
        .empty-cart-copy { color: #625148; font-size: .9rem; }
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, #FFFFFF, #FFFFFF);
            border: 1px solid rgba(255,159,105,.25);
            box-shadow: 0 8px 24px rgba(0,0,0,.18);
        }
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricLabel"] *,
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"] * {
            color: #2D211D !important;
        }
        div[data-testid="stTextInput"] input {
            background: #FFFFFF;
            color: #2D211D;
            border-color: rgba(255,255,255,.18);
        }
        div[data-testid="stExpander"] {
            background: rgba(255,255,255,.94);
        }
        .cart-count-pill {
            display:inline-block; margin:0 0 12px; padding:7px 13px;
            border-radius:999px; color:#8A2828; background:rgba(214,40,40,.18);
            border:1px solid rgba(255,112,70,.3); font-size:.78rem; font-weight:800;
        }
        [class*="st-key-cart_item_"] {
            padding:14px 16px 8px; margin:0 0 10px; border-radius:15px;
            border:1px solid rgba(255,255,255,.12);
            background:#FFFFFF;
        }
        .cart-unit-price { color:#625148; font-size:.82rem; }
        .cart-qty-label { color:#2D211D; font-weight:800; padding-top:8px; }
        .cart-line-subtotal {
            display:flex; justify-content:space-between; color:#625148;
            font-size:.78rem; padding:2px 0 4px; border-top:1px solid rgba(255,255,255,.08);
        }
        .cart-line-subtotal b { color:#FF7955; }
        .checkout-divider { height:1px; background:rgba(95,60,40,.13); margin:22px 0; }
        .order-summary-card {
            padding:20px 22px 8px; border-radius:18px;
            border:1px solid rgba(255,130,78,.3);
            background:linear-gradient(145deg,rgba(214,40,40,.16),rgba(255,248,239,.045));
            box-shadow:0 14px 35px rgba(0,0,0,.18);
        }
        .summary-kicker { color:#FF8A5B; font-size:.68rem; font-weight:900; letter-spacing:.16em; text-transform:uppercase; }
        .summary-title { color:#2D211D; font-size:1.12rem; font-weight:850; margin:5px 0 18px; }
        .summary-line,.summary-total { display:flex; justify-content:space-between; gap:12px; padding:10px 0; color:#625148; border-bottom:1px solid rgba(255,255,255,.1); }
        .summary-line b { color:#2D211D; }
        .summary-total { margin-top:6px; border:0; color:#2D211D; font-weight:800; font-size:1rem; }
        .summary-total b { color:#FF704D; font-size:1.45rem; }
        .summary-footnote { color:#625148; font-size:.76rem; line-height:1.5; padding:7px 0 10px; }
        @media(max-width:700px) {
            .hero-stamp { display:none; }
            .hero-panel { padding:28px 22px; }
            .six-sauce-banner { margin-bottom: 18px; }
            .six-sauce-banner img { max-height: 250px; }
            .store-title { font-size: 2.35rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Additional product-card details: heat meter, bestseller label, and distinct flavor glows.
st.markdown(
    """
    <style>
      .product-title-row { display:flex; align-items:center; justify-content:space-between; gap:8px; }
      .product-title-row .product-name { margin-top:8px; }
      .bestseller-badge {
        flex:0 0 auto; padding:5px 8px; border-radius:20px;
        color:#2A120B; background:linear-gradient(100deg,#FFD18A,#F29B42);
        font-size:.61rem; font-weight:900; letter-spacing:.07em;
      }
      .heat-meter {
        display:flex; align-items:center; gap:9px; margin-top:10px;
        min-height:25px;
      }
      .heat-meter-label, .heat-meter-value {
        color:#BFAFA3; font-size:.65rem; font-weight:800; letter-spacing:.08em;
      }
      .heat-flames { display:inline-flex; gap:2px; align-items:center; }
      .heat-flame { font-size:.83rem; line-height:1; }
      .heat-flame.active { filter:saturate(1.2); opacity:1; }
      .heat-flame.inactive { filter:grayscale(1); opacity:.24; }
      .heat-meter-value { color:#F2A65A; }
      /* Give every sauce its own ember tone on hover. */
      .st-key-sauce_card_4:hover {
        border-color:rgba(255,188,105,.72);
        box-shadow:0 0 12px rgba(255,173,91,.28),0 0 27px rgba(255,173,91,.16);
      }
      .st-key-sauce_card_4:hover [data-testid="stImage"] img {
        filter:drop-shadow(0 0 9px rgba(255,178,103,.68));
      }
      .st-key-sauce_card_5:hover {
        border-color:rgba(170,190,73,.78);
        box-shadow:0 0 12px rgba(160,185,67,.28),0 0 27px rgba(160,185,67,.16);
      }
      .st-key-sauce_card_5:hover [data-testid="stImage"] img {
        filter:drop-shadow(0 0 9px rgba(173,194,75,.7));
      }
      .st-key-sauce_card_6:hover {
        border-color:rgba(255,69,43,.9);
        box-shadow:0 0 15px rgba(255,55,31,.4),0 0 32px rgba(255,55,31,.23);
      }
      .st-key-sauce_card_6:hover [data-testid="stImage"] img {
        filter:drop-shadow(0 0 12px rgba(255,59,35,.82));
      }
      @media(max-width:700px) {
        .bestseller-badge { font-size:.55rem; padding:4px 6px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# Friend's textured background is scoped to this storefront page only.
# A light overlay preserves the original pattern while keeping dark type readable.
STORE_BACKGROUND = BASE_DIR / "images" / "bold-attribution-background-v4.png"
if STORE_BACKGROUND.exists():
    encoded_background = base64.b64encode(STORE_BACKGROUND.read_bytes()).decode("ascii")
    st.markdown(
        f"""
        <style>
            .stApp {{
                background-image:
                    linear-gradient(rgba(255, 249, 241, .86), rgba(255, 249, 241, .94)),
                    url("data:image/png;base64,{encoded_background}");
                background-size: cover;
                background-position: center top;
                background-attachment: fixed;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# CAMPAIGN TRACKING
# ---------------------------------------------------------
params = st.query_params

if "campaign_tracking" not in st.session_state:
    st.session_state.campaign_tracking = {}

for key in ["campaign_id", "utm_source", "utm_medium", "utm_campaign"]:
    if key in params:
        st.session_state.campaign_tracking[key] = params[key]


# ---------------------------------------------------------
# PRODUCT CATALOG
# ---------------------------------------------------------
from catalog import PRODUCTS as CATALOG_PRODUCTS

# Preserve the existing storefront's three original products and add the
# three new sauces from the friend's catalog.
products = []
for item in CATALOG_PRODUCTS:
    product = dict(item)
    if product["id"] == 1:
        product["name"] = "Classic Red Hot Sauce"
    products.append(product)


if "cart" not in st.session_state:
    st.session_state.cart = {}


# ---------------------------------------------------------
# ORDER STORAGE
# ---------------------------------------------------------
ORDER_FIELDS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_email",
    "items",
    "order_total",
    "promo_code",
    "campaign_id",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "match_status",
]


def save_order(customer_name, customer_email, promo_code, total):
    tracking = st.session_state.get("campaign_tracking", {})

    cart_items = []
    for product in products:
        quantity = st.session_state.cart.get(product["id"], 0)
        if quantity > 0:
            cart_items.append(f"{product['name']} x{quantity}")

    order = {
        "order_id": st.session_state.setdefault("checkout_token", "ORD-" + uuid.uuid4().hex[:12].upper()),
        "order_date": datetime.now(timezone.utc).isoformat(),
        "customer_name": customer_name.strip(),
        "customer_email": customer_email.strip(),
        "items": "; ".join(cart_items),
        "order_total": round(total, 2),
        "promo_code": promo_code.strip().upper(),
        "campaign_id": tracking.get("campaign_id", ""),
        "utm_source": tracking.get("utm_source", ""),
        "utm_medium": tracking.get("utm_medium", ""),
        "utm_campaign": tracking.get("utm_campaign", ""),
        "match_status": "Pending",
    }

    from data_store import append_unique
    append_unique(ORDERS_FILE, ORDER_FIELDS, order, 'order_id')
    st.session_state.last_order = order

    return order


# ---------------------------------------------------------
# STORE HEADER
# ---------------------------------------------------------
if st.session_state.get("last_order"):
    from html import escape
    confirmed = st.session_state.last_order
    st.success(f"Order confirmed · {confirmed['order_id']}")
    st.text(f"Customer: {confirmed['customer_name']}")
    st.text(f"Items: {confirmed['items']}")
    st.text(f"Total: ${float(confirmed['order_total']):.2f}")
    st.caption("Demonstration order only. No payment was collected.")
from ui import image_data_uri
bag_count=sum(st.session_state.cart.values())
feature_image=image_data_uri('images/hotvile-kitchen-bold.png')
st.markdown(f'''<div class="storefront-shell">
<div class="shop-announcement">SMALL BATCH. BIG FLAVOR. FIND YOUR HEAT.</div>
<nav class="shop-nav">{logo_html()}<div><a href="#sauce-collection">HOT SAUCES</a><a href="#your-bag">YOUR BAG ({bag_count})</a></div></nav>
<section class="shop-hero"><div class="shop-hero-copy"><h1 class="store-title">Small batch.<br>Big flavor.</h1><p>Find your heat.</p><a class="shop-cta" href="#sauce-collection">Shop sauces <span>→</span></a><small>Demonstration store · No real payments</small></div><div class="shop-feature"><img src="{feature_image}" alt="HotVile Classic Red hot sauce beside freshly prepared tacos"></div></section>
</div>''',unsafe_allow_html=True)

# ---------------------------------------------------------
# PRODUCT COLLECTION
# ---------------------------------------------------------
st.markdown('<div id="sauce-collection" class="section-kicker">The lineup</div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Find your heat</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">Six signature sauces. Find the flavor and heat that fit your table.</div>',
    unsafe_allow_html=True,
)

heat_options = ["All", "Mild", "Medium", "Hot", "Extra Hot"]
count = sum(st.session_state.cart.values())
cart_total = sum(p['price'] * st.session_state.cart.get(p['id'], 0) for p in products)
st.caption(f"Your bag · {count} item(s) · ${cart_total:.2f}")
selected_heat = st.selectbox("Filter by heat level", heat_options, index=0)
visible_products = products if selected_heat == "All" else [
    product for product in products if product["heat"] == selected_heat
]

# Display all six products in two rows of three; filters can return any count.
for row_start in range(0, len(visible_products), 3):
    row_products = visible_products[row_start:row_start + 3]
    columns = st.columns(3)

    for col, product in zip(columns, row_products):
        with col:
            with st.container(key=f"sauce_card_{product['id']}"):
                image_path = BASE_DIR / product["image"]
                if image_path.exists():
                    st.image(str(image_path), width="stretch")
                else:
                    st.info(f"Product image unavailable: {product['name']}")

                # Heat indicators are visual guidance for the six-sauce demo catalog.
                heat_scores = {
                    "Classic Red Hot Sauce": 2,
                    "Mango Habanero": 4,
                    "Smoky Chipotle": 1,
                    "Roasted Garlic": 1,
                    "Pineapple Jalapeño": 2,
                    "Ghost Pepper": 5,
                }
                heat_score = heat_scores.get(product["name"], 1)
                heat_icons = "".join(
                    f'<span class="heat-flame {"active" if level < heat_score else "inactive"}" aria-hidden="true"></span>'
                    for level in range(5)
                )
                bestseller_badge = (
                    '<span class="bestseller-badge">BESTSELLER</span>'
                    if product["name"] == "Mango Habanero" else ""
                )
                st.markdown(
                    f"""
                    <div class="sauce-card-copy">
                      <div class="product-title-row">
                        <div class="product-name">{product['name']}</div>
                        {bestseller_badge}
                      </div>
                      <div class="product-detail">{product['description']}</div>
                      <div class="heat-meter" aria-label="Heat intensity {heat_score} out of 5">
                        <span class="heat-meter-label">HEAT</span>
                        <span class="heat-flames">{heat_icons}</span>
                        <span class="heat-meter-value">{heat_score}/5</span>
                      </div>
                      <div class="product-bottom">
                        <div class="product-price">${product['price']:.2f}</div>
                        <div class="heat-pill">{product['heat'].upper()} HEAT</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "＋  Add to cart",
                    key=f"add_{product['id']}",
                    disabled=st.session_state.cart.get(product["id"], 0) >= 99,
                    width="stretch",
                    type="primary",
                ):
                    product_id = product["id"]
                    st.session_state.cart[product_id] = (
                        st.session_state.cart.get(product_id, 0) + 1
                    )
                    st.rerun()


# ---------------------------------------------------------
# INTERACTIVE CART + PREMIUM DEMO CHECKOUT
# ---------------------------------------------------------
st.markdown('<div id="your-bag" class="section-kicker">Your selections</div>', unsafe_allow_html=True)
st.markdown('<div class="section-heading">Your cart.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-copy">A few good choices. Review your sauces before placing your order.</div>',
    unsafe_allow_html=True,
)

cart_count = sum(st.session_state.cart.values())
subtotal = sum(
    product["price"] * st.session_state.cart.get(product["id"], 0)
    for product in products
)

if cart_count == 0:
    st.markdown(
        """
        <div class="empty-cart-panel">
          <div class="empty-cart-title">Your cart is waiting for a little heat.</div>
          <div class="empty-cart-copy">Choose a sauce from the lineup above and it will appear here.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="cart-count-pill">{cart_count} item(s) in your cart</div>',
        unsafe_allow_html=True,
    )

    for product in products:
        quantity = st.session_state.cart.get(product["id"], 0)
        if quantity <= 0:
            continue

        with st.container(key=f"cart_item_{product['id']}"):
            item_cols = st.columns([0.85, 2.8, 0.85, 0.85, 0.85, 1.25], vertical_alignment="center")
            image_path = BASE_DIR / product["image"]
            if image_path.exists():
                item_cols[0].image(str(image_path), width=82)
            else:
                item_cols[0].markdown("")
            item_cols[1].markdown(
                f"**{product['name']}**  \\n<span class='cart-unit-price'>${product['price']:.2f} each</span>",
                unsafe_allow_html=True,
            )
            item_cols[2].markdown(f"<div class='cart-qty-label'>Qty. {quantity}</div>", unsafe_allow_html=True)
            if item_cols[3].button("−", key=f"minus_{product['id']}", width="stretch"):
                new_quantity = quantity - 1
                if new_quantity <= 0:
                    st.session_state.cart.pop(product["id"], None)
                else:
                    st.session_state.cart[product["id"]] = new_quantity
                st.rerun()
            if item_cols[4].button("＋", key=f"plus_{product['id']}", width="stretch", disabled=quantity >= 99):
                st.session_state.cart[product["id"]] = quantity + 1
                st.rerun()
            if item_cols[5].button("Remove", key=f"remove_{product['id']}", width="stretch"):
                st.session_state.cart.pop(product["id"], None)
                st.rerun()
            st.markdown(
                f"<div class='cart-line-subtotal'>Item subtotal <b>${quantity * product['price']:.2f}</b></div>",
                unsafe_allow_html=True,
            )

    subtotal = sum(
        product["price"] * st.session_state.cart.get(product["id"], 0)
        for product in products
    )
    st.markdown('<div class="checkout-divider"></div>', unsafe_allow_html=True)
    checkout_left, checkout_right = st.columns([1.35, 0.85], gap="large")

    with checkout_left:
        st.markdown('<div class="section-kicker">Almost there</div>', unsafe_allow_html=True)
        st.markdown("### Customer details")
        with st.form("checkout_form"):
            customer_name = st.text_input("Full name", placeholder="Use a fictional name for this demo", key="checkout_name")
            customer_email = st.text_input("Email address (optional)", placeholder="you@example.com", key="checkout_email")
            promo_code = st.text_input("Promo code (optional)", placeholder="Enter your campaign promo code")
            st.caption("Promo codes are recorded with your order for campaign attribution. This demo does not calculate discounts.")
            place_order = st.form_submit_button(
                "Place order  →",
                type="primary",
                width="stretch",
            )

    with checkout_right:
        st.markdown(
            f"""
            <div class="order-summary-card">
              <div class="summary-kicker">Order summary</div>
              <div class="summary-title">A little heat, coming up.</div>
              <div class="summary-line"><span>Items</span><b>{cart_count}</b></div>
              <div class="summary-line"><span>Subtotal</span><b>${subtotal:.2f}</b></div>
              <div class="summary-line"><span>Shipping</span><b>Free</b></div>
              <div class="summary-total"><span>Order total</span><b>${subtotal:.2f}</b></div>
              <div class="summary-footnote">No payment is collected. This is a prototype checkout.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if place_order:
        if not customer_name.strip():
            st.error("Please enter your name.")
        elif customer_email.strip() and ("@" not in customer_email or "." not in customer_email.split("@")[-1]):
            st.error("Please enter a valid email address.")
        else:
            order = save_order(customer_name, customer_email, promo_code, subtotal)
            st.success(" Your order has been placed!")
            st.write(f"**Order ID:** {order['order_id']}")
            st.write(f"**Order total:** ${order['order_total']:.2f}")
            st.caption("No real payment was collected. Your order was saved to the prototype.")
            st.session_state.last_completed_order_id = order["order_id"]
            st.session_state.cart = {}
            st.session_state.pop("checkout_token", None)
            st.rerun()


# ---------------------------------------------------------
# PROTOTYPE TRANSPARENCY
# ---------------------------------------------------------
with st.expander("About this prototype"):
    st.write(
        "This storefront demonstrates the customer shopping journey and marketing campaign tracking. "
        "Orders are saved locally to the prototype data file so they can appear in the business dashboard. "
        "This is a demonstration checkout and does not process payments."
    )

if st.session_state.get("last_completed_order_id"):
    display_customer_feedback(st.session_state.last_completed_order_id)


# Keep tracking diagnostics available to the project team, not in the normal customer flow.
# Keep diagnostics out of the customer experience. Add ?debug=1 to the URL
# when the project team needs to inspect campaign tracking values.
if st.query_params.get("debug") == "1":
    with st.expander("Developer diagnostics", expanded=True):
        st.json(st.session_state.campaign_tracking)

from interaction_ui import apply_interactions
apply_interactions()
