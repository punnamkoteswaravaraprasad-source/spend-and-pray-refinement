import streamlit as st
from workspace_ui import workspace_header, apply_workspace

workspace_header('Business Overview', 'Follow the journey from a shared campaign to an order and its marketing results.', 'HOTVILE')

st.markdown('<div class="overview-route"><span>Business Overview</span><b>→</b><span>Order Matching</span><b>→</b><span>Marketing Dashboard</span></div>',unsafe_allow_html=True)
st.subheader('How it works')
steps = [
    ('01', 'Create and share a campaign', 'Choose the marketing channel, dates, and planned budget. Share the generated tracking link, promo code, or QR code.', 'pages/create_campaign.py', 'Create Campaign', ':material/add_circle:'),
    ('02', 'The customer places an order', 'The customer browses HotVile sauces, builds a cart, and completes a demo checkout. Available campaign signals are saved with the order.', None, None, None),
    ('03', 'Review order matching', 'Check which orders match a campaign and which are unattributed or need review. Record evidence when changing an attribution decision.', 'pages/order_matching.py', 'Order Matching', ':material/fact_check:'),
    ('04', 'Compare marketing results', 'Use filters and graphs to compare revenue, orders, channels, and campaign budgets. Budget-based ROAS compares matched revenue with planned budget.', 'pages/marketing_dashboard.py', 'Marketing Dashboard', ':material/bar_chart:'),
]
for offset in range(0,len(steps),2):
    columns=st.columns(2,gap='large')
    for column,(number,title,description,path,label,icon) in zip(columns,steps[offset:offset+2]):
        with column:
            with st.container(border=True,key=f'workspace_panel_overview_step_{number}'):
                st.markdown(f'<span class="overview-step-number">{number}</span>',unsafe_allow_html=True)
                st.subheader(title)
                st.write(description)
                if path: st.page_link(path,label=label,icon=icon)

with st.container(border=True,key='workspace_panel_overview_continue'):
    st.markdown('**Ready to review the orders?**')
    st.page_link('pages/order_matching.py',label='Continue to Order Matching',icon=':material/arrow_forward:')
with st.expander('About this demo'):
    st.write('Fictional seed data and demonstration orders only. Attribution indicates association, not causation. Planned budget is not actual advertising spend or profit. Demo access has no authentication; use fictional customer details.')
apply_workspace()
