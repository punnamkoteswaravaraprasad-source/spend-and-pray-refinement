import base64
from pathlib import Path

import streamlit as st


BRAND_RED = "#9E2A2B"
BRAND_ORANGE = "#D65A31"
BRAND_GOLD = "#D99A2B"
BRAND_CREAM = "#FFF8ED"
BRAND_CHARCOAL = "#252525"
BRAND_GREEN = "#2F7D5A"
ASSET_DIR = Path(__file__).resolve().parent / "images"


def image_data_uri(path):
    image_path = Path(path)
    if not image_path.is_absolute():
        image_path = Path(__file__).resolve().parent / image_path
    if not image_path.exists():
        return ""
    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def apply_theme():
    page_background = image_data_uri("images/bold-attribution-background-v4.png")
    st.markdown(
        """
        <style>
        :root {
            --brand-red: #9E2A2B;
            --brand-orange: #D65A31;
            --brand-gold: #D99A2B;
            --brand-cream: #FFF8ED;
            --brand-charcoal: #252525;
        }

        .stApp {
            background: #fffaf1;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 25% 12%, rgba(255,190,50,.28), transparent 24%),
                linear-gradient(180deg, #8f151e 0%, #c52f24 46%, #ea6429 100%);
            border-right: 1px solid rgba(255,211,90,.55);
            box-shadow: 8px 0 30px rgba(108,25,20,.18);
        }

        [data-testid="stSidebar"] * {
            color: #fff7eb;
        }

        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(255,255,255,.18);
            border-radius: 10px;
            box-shadow: inset 4px 0 0 #ffd34f;
        }

        [data-testid="stSidebarNav"] a {
            min-height: 48px;
            padding: .7rem 1rem;
            font-size: 1.04rem;
            font-weight: 650;
            transition: transform .18s ease, background .18s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            transform: translateX(5px);
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        h1, h2, h3 {
            color: #252525;
            letter-spacing: -0.02em;
        }

        div.stButton > button,
        div.stLinkButton > a,
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 10px;
            border: 1px solid #9E2A2B;
            font-weight: 700;
            min-height: 2.75rem;
        }

        div.stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #d7192d, #f45b25 62%, #ff9f1c);
            border: none;
            box-shadow: 0 8px 20px rgba(211,48,35,.25);
            transition: transform .18s ease, box-shadow .18s ease;
        }

        div.stButton > button:hover,
        div.stLinkButton > a:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(211,48,35,.28);
        }

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid rgba(255,255,255,.82);
            border-left: 6px solid #f04c2f;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 28px rgba(118,28,20,.15);
            transition: transform .18s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
        }

        [data-testid="stMetricLabel"] {
            color: #6f5b50;
        }

        [data-testid="stMetricValue"] {
            color: #9E2A2B;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(255,255,255,.8);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 12px 28px rgba(118,28,20,.13);
        }

        [data-testid="stForm"] {
            background: rgba(255,255,255,.96);
            border: 1px solid rgba(255,255,255,.8);
            border-top: 6px solid #f04c2f;
            border-radius: 18px;
            padding: 1.3rem;
            box-shadow: 0 14px 32px rgba(118,28,20,.15);
        }

        [data-baseweb="tab-list"] {
            gap: .45rem;
            background: rgba(255,255,255,.86);
            padding: .4rem;
            border-radius: 14px;
            box-shadow: 0 8px 20px rgba(118,28,20,.1);
        }

        [data-baseweb="tab"] {
            border-radius: 10px;
            font-weight: 800;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }

        [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #dc2334, #f46a24);
            color: white;
        }

        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,.96);
            border: 1px solid rgba(255,255,255,.82);
            border-radius: 20px;
            padding: .55rem;
            box-shadow: 0 14px 34px rgba(118,28,20,.15);
            overflow: visible;
        }

        .brand-hero {
            min-height: 210px;
            padding: 2rem;
            border-radius: 26px;
            color: white;
            background:
                radial-gradient(circle at top right, rgba(255,255,255,.18), transparent 35%),
                linear-gradient(135deg, #7f1d1d, #c2412d 62%, #d99a2b);
            background-position: center;
            background-size: cover;
            box-shadow: 0 18px 45px rgba(126, 35, 29, 0.22);
            margin-bottom: 1.4rem;
            display: flex;
            align-items: center;
            overflow: hidden;
            position: relative;
        }

        .hero-copy {
            max-width: 52%;
            position: relative;
            z-index: 1;
        }

        .hero-icon {
            position: absolute;
            right: 2rem;
            bottom: 1.7rem;
            width: 70px;
            height: 70px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 20px;
            background: linear-gradient(145deg, #ef2439, #ff7a18 68%, #ffc928);
            border: 2px solid rgba(255,255,255,.72);
            box-shadow: 0 15px 30px rgba(0,0,0,.22);
            font-size: 2.15rem;
            z-index: 2;
        }

        .brand-hero h1, .brand-hero h2, .brand-hero p {
            color: white;
            margin: 0;
        }

        .brand-hero h1 {
            font-size: clamp(1.6rem, 2.6vw, 2.2rem);
            margin-top: .35rem;
            margin-bottom: .55rem;
            text-shadow: 0 3px 22px rgba(0,0,0,.38);
        }

        .brand-hero p {
            font-size: 1rem;
            line-height: 1.58;
            max-width: 590px;
            text-shadow: 0 2px 14px rgba(0,0,0,.45);
        }

        .role-visual {
            display: flex;
            align-items: center;
            gap: .9rem;
            margin-bottom: .8rem;
        }

        .role-icon {
            width: 66px;
            height: 66px;
            flex: 0 0 66px;
            border-radius: 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(145deg, #e3192d, #ff7a18 70%, #ffc928);
            box-shadow: 0 12px 26px rgba(211,48,35,.3);
            font-size: 2rem;
        }

        .role-title {
            margin: 0;
            font-size: 1.65rem;
            color: #2b211d;
        }

        .role-kicker {
            margin: .15rem 0 0;
            color: #9E2A2B;
            font-size: .76rem;
            font-weight: 850;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .role-description {
            min-height: 0;
            color: #5d4b42;
            font-size: 1rem;
            line-height: 1.55;
        }

        .feature-chip {
            display: inline-flex;
            align-items: center;
            gap: .3rem;
            background: linear-gradient(135deg, #fff0d2, #ffe1c6);
            border: 1px solid #f3b372;
            color: #7c261f;
            border-radius: 999px;
            padding: .34rem .62rem;
            margin: 0 .3rem .42rem 0;
            font-size: .76rem;
            font-weight: 750;
        }

        .st-key-owner_role_card,
        .st-key-customer_role_card {
            background: rgba(255,255,255,.96);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255,255,255,.75) !important;
            border-top: 7px solid #f04c2f !important;
            border-radius: 20px;
            padding: 1.25rem;
            box-shadow: 0 16px 38px rgba(118,28,20,.2);
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
        }

        .st-key-owner_role_card:hover,
        .st-key-customer_role_card:hover {
            transform: translateY(-6px);
            box-shadow: 0 20px 42px rgba(74,42,29,.16);
            border-color: #ff8a22 !important;
        }

        .st-key-customer_role_card {
            border-top-color: #f4a21c !important;
        }

        [data-testid="stExpander"] {
            background: rgba(255,255,255,.9);
            border: 1px solid #e5c9af;
            border-radius: 15px;
            box-shadow: 0 8px 24px rgba(74,42,29,.06);
        }

        .eyebrow {
            display: inline-block;
            text-transform: uppercase;
            letter-spacing: .14em;
            font-weight: 800;
            font-size: .73rem;
            opacity: .9;
        }

        .section-label {
            display: inline-block;
            color: white;
            background: linear-gradient(135deg, #d7192d, #f45b25 70%, #f6a51f);
            border-radius: 999px;
            padding: .4rem .8rem;
            font-size: .75rem;
            font-weight: 800;
            letter-spacing: .06em;
            text-transform: uppercase;
            margin-bottom: .35rem;
            box-shadow: 0 7px 16px rgba(211,48,35,.22);
        }

        .page-step-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: .8rem;
            margin: .25rem 0 1.35rem;
        }

        .page-step {
            display: flex;
            align-items: center;
            gap: .75rem;
            padding: .85rem 1rem;
            border-radius: 15px;
            color: white;
            background: linear-gradient(135deg, rgba(192,28,39,.96), rgba(244,91,37,.96));
            border: 1px solid rgba(255,255,255,.45);
            box-shadow: 0 10px 24px rgba(118,28,20,.18);
            transition: transform .18s ease;
        }

        .page-step:nth-child(2) {
            background: linear-gradient(135deg, #e74b23, #ff8a1f);
        }

        .page-step:nth-child(3) {
            background: linear-gradient(135deg, #ef7d13, #f7b51b);
        }

        .page-step:hover {
            transform: translateY(-4px);
        }

        .page-step-icon {
            font-size: 1.55rem;
        }

        .page-step strong {
            display: block;
            font-size: .95rem;
        }

        .page-step span:last-child {
            display: block;
            font-size: .76rem;
            opacity: .9;
        }

        .info-card {
            min-height: 150px;
            background: linear-gradient(145deg, rgba(255,255,255,.98), rgba(255,247,235,.94));
            border: 1px solid #ead9c8;
            border-radius: 16px;
            padding: 1.1rem;
            box-shadow: 0 8px 24px rgba(55, 35, 25, 0.05);
        }

        .info-card h3 {
            margin: .4rem 0 .35rem 0;
            font-size: 1.08rem;
        }

        .info-card p {
            color: #6f5b50;
            margin: 0;
            line-height: 1.45;
        }

        .icon-circle {
            width: 50px;
            height: 50px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: #fde8dd;
            font-size: 1.55rem;
            box-shadow: inset 0 0 0 1px rgba(158,42,43,.09);
        }

        button:focus-visible, a:focus-visible, input:focus-visible { outline: 3px solid #275ca8 !important; outline-offset: 3px; }
        .product-card p { min-height: 74px; }
        .product-card {
            background: linear-gradient(180deg, #fffaf1 0%, white 60%);
            border: 1px solid #ead9c8;
            border-radius: 18px;
            padding: 1.2rem;
            min-height: 520px;
            box-shadow: 0 10px 28px rgba(55, 35, 25, 0.06);
            text-align: center;
            transition: transform .2s ease, box-shadow .2s ease;
            border-top: 7px solid #f04c2f;
        }

        .product-card:hover {
            transform: translateY(-7px);
            box-shadow: 0 20px 38px rgba(118,28,20,.2);
        }

        .product-photo-wrap {
            height: 330px;
            margin: -.3rem auto .75rem;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 16px;
            background: radial-gradient(circle, rgba(255,220,166,.58), rgba(255,248,237,.15) 65%, transparent 72%);
            overflow: hidden;
        }

        .product-photo {
            max-height: 325px;
            max-width: 88%;
            object-fit: contain;
            filter: drop-shadow(0 15px 17px rgba(62,31,20,.19));
        }

        .heat-pill, .status-pill {
            display: inline-block;
            border-radius: 999px;
            padding: .25rem .58rem;
            font-size: .72rem;
            font-weight: 800;
        }

        .heat-mild { background: #e5f5eb; color: #246b45; }
        .heat-medium { background: #fff0c7; color: #8a5a00; }
        .flavor-visual { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .6rem; width: 85%; height: 230px; border-radius: 70px 70px 25px 25px; background: linear-gradient(150deg, #ffdf87, #f47b35); color: #542216; box-shadow: 0 12px 20px #9e2a2b25; }
        .flavor-visual span { font-size: 5rem; }
        .flavor-visual strong { font-size: 1.3rem; }
        .flavor-visual small { font-size: .65rem; letter-spacing: .1em; }
        .heat-extra-hot { background: #562135; color: white; }
        .heat-hot { background: #fde2dd; color: #a83227; }
        .status-matched { background: #e5f5eb; color: #246b45; }
        .status-unattributed { background: #eceff3; color: #495463; }
        .status-review { background: #fff0c7; color: #8a5a00; }

        .st-key-story_setup, .st-key-story_conflict, .st-key-story_resolution { background: rgba(255,253,249,.97); border-radius: 20px; padding: 1.3rem; margin: 1rem 0 1.6rem; box-shadow: 0 12px 28px rgba(80,30,20,.12); }
        .chart-explanation { border-left: 4px solid #d99a2b; background: #fff5dc; border-radius: 12px; padding: .85rem 1rem; margin: .5rem 0 1.2rem; color: #593b27; }
        .chart-explanation p { margin: .35rem 0 0; line-height: 1.5; }
        .st-key-sales_kpis, .st-key-marketing_kpis, .st-key-tracking_kpis { background: #fffdfa; padding: 1rem; border-radius: 16px; border-top: 4px solid #9e2a2b !important; margin-bottom: 1rem; }
        .st-key-marketing_kpis { border-top-color: #d99a2b !important; }
        .st-key-tracking_kpis { border-top-color: #2f7d5a !important; }
        .insight-box {
            border-left: 5px solid #D99A2B;
            background: #fff6dc;
            border-radius: 10px;
            padding: .9rem 1rem;
            color: #5f4610;
            margin: .8rem 0;
        }

        @media (max-width: 760px), (pointer: coarse) and (max-width: 1100px) {
            .block-container { width: 100%; max-width: 100%; padding: 1.15rem .85rem 3rem; }
            [data-testid="stHorizontalBlock"] { flex-direction: column !important; align-items: stretch !important; gap: 1rem !important; }
            [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; min-width: 0 !important; }
            .brand-hero { min-height: 230px; padding: 1.35rem; border-radius: 16px; background-position: 64% center; }
            .hero-copy { max-width: 85%; }
            .product-card { min-height: auto; padding: 1rem; }
            .product-card p, .role-description { min-height: 0; }
            .product-photo-wrap { height: clamp(250px, 75vw, 330px); margin: 0 auto .75rem; }
            .product-photo { width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; }
            .page-step-grid { grid-template-columns: 1fr; }
            .hero-icon { width: 54px; height: 54px; right: 1rem; bottom: 1rem; font-size: 1.65rem; }
            .st-key-story_setup, .st-key-story_conflict, .st-key-story_resolution { padding: .8rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if page_background:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image:
                    linear-gradient(rgba(255,248,235,.38), rgba(255,248,235,.52)),
                    url('{page_background}');
                background-size: auto, cover;
                background-attachment: fixed;
                background-position: center, center top;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )


def hero(
    title,
    subtitle,
    eyebrow="Spend & Pray",
    background_image="images/hero-hotvile-v3.png",
    icon="🌶️",
):
    background_uri = image_data_uri(background_image) if background_image else ""
    if background_uri:
        background_style = (
            "background-image: linear-gradient(90deg, rgba(24,12,9,.93) 0%, "
            "rgba(24,12,9,.74) 37%, rgba(24,12,9,.16) 70%), "
            f"url('{background_uri}');"
        )
    else:
        background_style = ""
    st.markdown(
        f"""
        <div class="brand-hero" style="{background_style}">
            <div class="hero-copy">
                <span class="eyebrow">{eyebrow}</span>
                <h1>{title}</h1>
                <p>{subtitle}</p>
            </div>
            <div class="hero-icon">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(
        f'<span class="section-label">{text}</span>',
        unsafe_allow_html=True,
    )


def page_steps(items):
    """Compatibility hook for compact pages; guidance now lives beside actions."""
    return None


def info_card(icon, title, description):
    st.markdown(
        f"""
        <div class="info-card">
            <span class="icon-circle">{icon}</span>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_pill(status):
    css_class = {
        "Matched": "status-matched",
        "Unattributed": "status-unattributed",
        "Needs Review": "status-review",
    }.get(status, "status-unattributed")
    return f'<span class="status-pill {css_class}">{status}</span>'


def chart_layout(title, y_title=None, height=360):
    layout = dict(
        title=dict(text=title, font=dict(size=17, color=BRAND_CHARCOAL)),
        height=height,
        margin=dict(l=75, r=35, t=85, b=95, autoexpand=True),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color=BRAND_CHARCOAL, size=14),
        xaxis=dict(automargin=True, tickfont=dict(size=13), title=dict(standoff=20)),
        hoverlabel=dict(bgcolor="white"),
        legend=dict(orientation="h", yanchor="top", y=-0.35, x=0),
    )
    if y_title:
        layout["yaxis"] = dict(title=dict(text=y_title, standoff=18), automargin=True, type="linear", gridcolor="#ead9c8", tickfont=dict(size=13), rangemode="tozero")
        if "($)" in y_title:
            layout["yaxis"].update(tickprefix="$", tickformat=",.2f")
    return layout


def show_chart(fig):
    """Consistent clean chart controls and wrapped category labels."""
    from textwrap import wrap
    if not fig.layout.xaxis.tickmode:
        labels = list(dict.fromkeys(str(x) for trace in fig.data for x in (getattr(trace, 'x', None) or []) if isinstance(x, str)))
        if labels:
            from html import escape
            fig.update_xaxes(tickmode='array', tickvals=labels,
                             ticktext=['<br>'.join(escape(line) for line in wrap(label, 11)) for label in labels],
                             automargin=True, tickangle=0)
    fig.update_traces(selector=dict(type='bar'), cliponaxis=False)
    st.plotly_chart(fig, width='stretch', theme=None,
                    config={'displayModeBar': False, 'displaylogo': False, 'responsive': True, 'scrollZoom': False})


def chart_explanation(title, text):
    from html import escape
    st.markdown(f'<div class="chart-explanation"><strong>{escape(title)}</strong><p>{escape(text)}</p></div>', unsafe_allow_html=True)
