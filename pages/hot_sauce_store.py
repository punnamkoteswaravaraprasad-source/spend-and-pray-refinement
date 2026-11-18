import csv
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from data_store import append_unique

from ui import apply_theme, hero, image_data_uri, page_steps, section_label


apply_theme()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
ORDERS_FILE = DATA_DIR / "demo_orders.csv"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.csv"

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

from catalog import PRODUCTS



def load_campaigns():
    if not CAMPAIGNS_FILE.exists():
        return []
    with open(CAMPAIGNS_FILE, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def validate_promo_code(code):
    normalized = code.strip().upper()
    if not normalized:
        return True
    return any(
        normalized == (campaign.get("promo_code") or "").strip().upper()
        for campaign in load_campaigns()
    )


def save_order(customer_name, customer_email, promo_code, total):
    tracking = st.session_state.get("campaign_tracking", {})
    if 'checkout_token' not in st.session_state:
        st.session_state.checkout_token = 'ORD-' + uuid.uuid4().hex[:12].upper()
    order_id = st.session_state.checkout_token

    cart_items = []
    for product in PRODUCTS:
        quantity = st.session_state.cart.get(product["id"], 0)
        if quantity > 0:
            cart_items.append(f"{product['name']} x{quantity}")

    order = {
        "order_id": order_id,
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

    append_unique(ORDERS_FILE, ORDER_FIELDS, order, 'order_id')

    return order


params = st.query_params
if "campaign_tracking" not in st.session_state:
    st.session_state.campaign_tracking = {}

for key in ["campaign_id", "utm_source", "utm_medium", "utm_campaign"]:
    if key in params:
        st.session_state.campaign_tracking[key] = params[key]

if "cart" not in st.session_state:
    st.session_state.cart = {}


hero(
    "Fire, flavor, and a sauce for every table",
    "Find your flavor. Choose your heat. Build your perfect sauce collection.",
    "HotVile Hot Sauce Co.",
    icon="🛍️",
)

page_steps([
    ("🌶️", "Explore", "Filter sauces and compare flavor and heat."),
    ("🛒", "Build", "Add products and adjust quantities in the cart."),
    ("🎟️", "Complete", "Use an optional promo code and place a demo order."),
])

if st.session_state.get("last_order"):
    order = st.session_state.last_order
    with st.container(border=True):
        st.success("Your demonstration order was placed successfully.")
        st.text(f"Customer: {order.get('customer_name') or 'Name not recorded'}")
        st.markdown('**Your order**')
        for item in order['items'].split('; '):
            st.text(item)
        r1, r2, r3 = st.columns(3)
        r1.metric("Order", order["order_id"])
        r2.metric("Units", order.get("units", len(order["items"].split("; "))))
        r3.metric("Total", f"${order['order_total']:,.2f}")
        st.caption("No real payment was collected. This order supports the attribution demonstration.")
        if st.button("Start a New Order"):
            st.session_state.last_order = None
            st.session_state.pop("checkout_token", None)
            st.rerun()


section_label("Shop sauces")
filter_col, cart_col = st.columns([3, 1])
with filter_col:
    heat_filter = st.segmented_control(
        "Filter by heat level",
        options=["All", "Mild", "Medium", "Hot", "Extra Hot"],
        default="All",
    )
with cart_col:
    total_units = sum(st.session_state.cart.values())
    cart_total = sum(p['price'] * st.session_state.cart.get(p['id'], 0) for p in PRODUCTS)
    st.metric('Your bag', f'${cart_total:,.2f}', help=f'{total_units} bottle(s)')
    st.caption(f'{total_units} bottle(s) in your bag')
    st.markdown('[View bag & checkout](#your-bag)')

visible_products = [
    product
    for product in PRODUCTS
    if heat_filter in (None, "All") or product["heat"] == heat_filter
]

for index, product in enumerate(visible_products):
    if index % 3 == 0:
        product_columns = st.columns(3)
    column = product_columns[index % 3]
    heat_class = f"heat-{product['heat'].lower().replace(' ', '-')}"
    product_image = image_data_uri(product["image"]) if product["image"] else ""
    product_visual = (f'<img class="product-photo" src="{product_image}" alt="{product["name"]} hot sauce bottle">'
                      if product_image else f'<div class="flavor-visual" aria-label="{product["name"]} flavor illustration"><span>{product["emoji"]}</span><strong>{product["name"]}</strong><small>HOTVILE • SMALL BATCH</small></div>')
    with column:
        st.markdown(
            f"""
            <div class="product-card">
                <div class="product-photo-wrap">
                    {product_visual}
                </div>
                <span class="heat-pill {heat_class}">{product['heat']} heat</span>
                <h3>{product['name']}</h3>
                <p>{product['description']}</p>
                <h2>${product['price']:.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "Add to Cart",
            key=f"add_{product['id']}",
            help=f"Add one bottle of {product['name']} to your bag (maximum 99)",
            disabled=st.session_state.cart.get(product["id"], 0) >= 99,
            type="primary",
            width="stretch",
        ):
            product_id = product["id"]
            st.session_state.cart[product_id] = (
                min(99, st.session_state.cart.get(product_id, 0) + 1)
            )
            st.session_state.pop('checkout_token', None)
            st.session_state['cart_feedback'] = f"{product['name']} added to your bag."
            st.rerun()

feedback = st.session_state.pop('cart_feedback', None)
if feedback:
    st.success(feedback)
st.markdown('<span id="your-bag"></span>', unsafe_allow_html=True)
st.markdown("### Your bag")

if not st.session_state.cart:
    with st.container(border=True):
        st.info("Your cart is empty. Add a sauce to begin your demonstration order.")
else:
    total = 0.0
    for product in PRODUCTS:
        quantity = st.session_state.cart.get(product["id"], 0)
        if quantity <= 0:
            continue

        subtotal = quantity * product["price"]
        total += subtotal
        with st.container(border=True):
            st.write(f"**{product['name']}** · ${product['price']:,.2f} each")
            quantity_col, price_col = st.columns([2, 1])
            new_quantity = quantity_col.number_input(
                f"Quantity — {product['name']}", min_value=1, max_value=99,
                value=quantity, step=1, key=f"quantity_{product['id']}_{quantity}")
            if new_quantity != quantity:
                st.session_state.cart[product['id']] = new_quantity
                st.session_state.pop('checkout_token', None)
                st.rerun()
            price_col.metric('Subtotal', f'${subtotal:,.2f}')
            if st.button(f"Remove {product['name']}", key=f"remove_{product['id']}"):
                st.session_state.cart.pop(product['id'], None)
                st.session_state.pop('checkout_token', None)
                st.rerun()

    st.divider()
    total_col, clear_col = st.columns([3, 1])
    total_col.markdown(f"## Order total: ${total:,.2f}")
    if clear_col.button("Clear Cart", width="stretch"):
        st.session_state.cart = {}
        st.session_state.pop("checkout_token", None)
        st.rerun()

    st.markdown("### Checkout")
    st.caption("Your name connects this order to your bag. Email is optional; no payment is collected and no email is sent.")

    with st.form("checkout_form"):
        customer_name = st.text_input('Your name', placeholder='Name for this order', max_chars=80, key='checkout_name')
        customer_email = st.text_input('Email (optional)', placeholder='you@example.com', key='checkout_email')
        promo_code = st.text_input(
            "Promo Code (optional)",
            placeholder="Enter a campaign promo code",
        )
        check_promo = st.form_submit_button("Check Promo Code")
        if check_promo:
            if not promo_code.strip():
                st.info("Promo codes are optional. You can continue without one.")
            elif validate_promo_code(promo_code):
                st.success("Code recognized. It identifies the campaign; demo prices are unchanged.")
            else:
                st.error("Code not recognized. Check it or leave it blank.")
        place_order = st.form_submit_button(
            "Place demo order",
            type="primary",
            width="stretch",
        )

        if place_order:
            import re
            if not customer_name.strip():
                st.error('Enter your name so we can identify your order.')
            elif customer_email.strip() and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', customer_email.strip()):
                st.error('Enter a valid email address or leave it blank.')
            elif not validate_promo_code(promo_code):
                st.error("That promo code was not recognized. Check the code or leave it blank.")
            else:
                order = save_order(
                    customer_name,
                    customer_email,
                    promo_code,
                    total,
                )
                order["units"] = sum(st.session_state.cart.values())
                st.session_state.last_order = order
                st.session_state.cart = {}
                st.session_state.pop("checkout_token", None)
                st.rerun()

st.caption("Academic prototype • Demonstration orders only • No payment is collected")
