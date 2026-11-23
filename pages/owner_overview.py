import streamlit as st
from html import escape
from attribution_engine import process_orders,calculate_kpis
from workspace_ui import apply_workspace,metric_tile

rows,campaigns=process_orders()
k=calculate_kpis(rows)
attention=k['unattributed_orders']+k['needs_review']
st.markdown('<span class="workspace-marker"></span>',unsafe_allow_html=True)
apply_workspace()
with st.container(key='owner_hero'):
    st.markdown('<div class="hero-kicker"><span></span> HOTVILE / BUSINESS OVERVIEW</div>',unsafe_allow_html=True)
    left,right=st.columns([1.5,1],vertical_alignment='center')
    with left:
        st.title('Your business, in focus.')
        st.write('Connect campaign activity to customer orders and focus on the tracking gaps that need attention.')
    with right:
        st.page_link('pages/create_campaign.py',label='Create campaign',icon=':material/add_circle:')
        st.page_link('pages/marketing_dashboard.py',label='Explore analytics',icon=':material/arrow_forward:')
a,b,c,d=st.columns(4)
metric_tile(a,'Total revenue',f'${k["total_revenue"]:,.2f}','Across recorded demo orders','overview_revenue',icon='money')
metric_tile(b,'Customer orders',str(k['total_orders']),'In the connected dataset','overview_orders',icon='orders')
metric_tile(c,'Attribution coverage',f'{k["coverage"]:.1f}%','Orders matched to a campaign','overview_coverage','green','check')
metric_tile(d,'Needs attention',str(attention),'Missing or conflicting tracking','overview_attention','orange','alert')
gap=k['total_revenue']-k['matched_revenue']
recommendation=('Review orders without a verified campaign match before comparing channel returns.' if attention else 'All orders have verified campaign matches. Explore campaign performance to compare results.')
st.markdown(f'<section class="tracking-brief"><div class="brief-title">Tracking briefing <span>CALCULATED SUMMARY</span></div><p>{attention} of {k["total_orders"]} orders have no verified campaign match, accounting for <b>${gap:,.2f}</b> in revenue.</p><div class="brief-recommendation">{escape(recommendation)}</div></section>',unsafe_allow_html=True)
left,right=st.columns([1.3,1])
with left:
    with st.container(border=True,key='workspace_panel_overview_channels'):
        st.subheader('Channel revenue')
        import plotly.express as px
        import pandas as pd
        from workspace_ui import chart_style,show_chart
        matched=[r for r in rows if r['status']=='Matched']
        if matched:
            summary=pd.DataFrame(matched).groupby('channel',as_index=False)['revenue'].sum().sort_values('revenue')
            fig=px.bar(summary,x='revenue',y='channel',orientation='h',color_discrete_sequence=['#EE512E'])
            chart_style(fig,height=310);fig.update_xaxes(title='Revenue ($)',tickprefix='$');fig.update_yaxes(title='')
            show_chart(fig,'overview_channel_revenue')
        else: st.info('No matched orders to compare yet.')
with right:
    with st.container(border=True,key='workspace_panel_overview_actions'):
        st.subheader('Next actions')
        st.page_link('pages/order_matching.py',label='Review order attribution',icon=':material/fact_check:')
        st.caption(f'{attention} orders need attention')
        st.divider()
        st.page_link('pages/create_campaign.py',label='Manage campaign links',icon=':material/link:')
        st.caption(f'{len(campaigns)} saved campaigns')
        st.divider()
        st.page_link('pages/marketing_dashboard.py',label='Filter and compare results',icon=':material/bar_chart:')
with st.expander('About these results'):
    st.write('Fictional seed data and demonstration orders. Attribution indicates association, not causation. Budget-based ROAS uses planned budget, not actual ad spend or profit. Demo access has no authentication; use fictional customer details.')
apply_workspace()
