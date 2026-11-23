from datetime import date
from textwrap import wrap
import csv
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from attribution_engine import process_orders, calculate_kpis
from dashboard_charts import revenue_chart
from components.feedback_analytics import display_feedback_dashboard
from reporting import amount
from workspace_ui import workspace_header, apply_workspace, chart_style, show_chart, RED, BLUE, GREEN, MUTED, metric_tile, progress_panel

workspace_header('Marketing Dashboard', 'Filter orders and compare sales, campaigns, and attribution.', 'HOTVILE')
results, campaigns = process_orders()
frame = pd.DataFrame(results, columns=['order_id','order_date','revenue','status','campaign_id','campaign_name','channel'])
frame['order_date'] = pd.to_datetime(frame['order_date'], errors='coerce', utc=True)
channels = sorted({c.get('channel') or 'Unknown' for c in campaigns})
campaign_names = sorted({c.get('campaign_name') or 'Unnamed' for c in campaigns})
valid_dates = frame['order_date'].dropna()
min_date,max_date = ((valid_dates.min().date(), valid_dates.max().date()) if not valid_dates.empty else (date.today(),date.today()))
with st.container(border=True, key="workspace_panel_marketing_dashboard_0"):
    f1,f2,f3,f4=st.columns([1.1,1.4,1.4,1])
    with f1: selected_channels=st.multiselect('Channel',channels,default=[],placeholder='All channels')
    with f2: selected_names=st.multiselect('Campaign',campaign_names,default=[],placeholder='All campaigns')
    with f3: dates=st.date_input('Order date range',value=(min_date,max_date),min_value=min_date,max_value=max_date)
    with f4: selected_types=st.multiselect('Order status', ['Matched','Unattributed','Needs Review'],default=['Matched','Unattributed','Needs Review'])
if isinstance(dates,(tuple,list)) and len(dates)!=2:
    st.info('Choose an end date to apply the range.');st.stop()
start,end=dates
if start>end:
    st.error('The start date must be on or before the end date.');st.stop()
selected_campaigns=[c for c in campaigns if (not selected_channels or c.get('channel') in selected_channels) and (not selected_names or c.get('campaign_name') in selected_names)]
ids={c['campaign_id'] for c in selected_campaigns}
filtered=frame[((frame['status']!='Matched') | frame['campaign_id'].isin(ids)) & frame['status'].isin(selected_types)].copy()
if not selected_types: filtered=filtered.iloc[0:0]
invalid=int(filtered['order_date'].isna().sum())
if invalid: st.warning(f'{invalid} order(s) have missing or invalid dates and are excluded from this date-filtered view.')
filtered=filtered[filtered['order_date'].dt.normalize().between(pd.Timestamp(start,tz='UTC'),pd.Timestamp(end,tz='UTC'))]
rows=filtered.to_dict('records')
k=calculate_kpis(rows)
budget=sum(amount(c.get('budget')) for c in selected_campaigns)
roas=k['matched_revenue']/budget if budget else None
with st.container(key="analytics_tiles"):
    a,b,c,d,e=st.columns(5)
    metric_tile(a,'Total revenue',f"${k['total_revenue']:,.2f}",'Across selected orders','analytics_revenue',icon='money')
    metric_tile(b,'Orders',str(k['total_orders']),'Orders in this selection','analytics_orders',icon='orders')
    metric_tile(c,'Matched orders',str(k['matched_orders']),'Verified campaign connection','analytics_matched','green','check')
    metric_tile(d,'Needs attention',str(k['unattributed_orders']+k['needs_review']),'Missing or conflicting tracking','analytics_attention','orange','alert')
    metric_tile(e,'Attribution coverage',f"{k['coverage']:.1f}%",'Matched share of all orders','analytics_coverage','purple','chart')
left,right=st.columns(2,gap='medium')
with left:
    progress_panel('Attribution quality','Rates across the selected orders.',[
        ('Matched',k['coverage'],f"{k['coverage']:.1f}%",'#343434'),
        ('Unattributed',k['unattributed_rate'],f"{k['unattributed_rate']:.1f}%",'#F4763C'),
        ('Needs Review',k['needs_review_rate'],f"{k['needs_review_rate']:.1f}%",'#B79C88')],'analytics_rates')
with right:
    share=k['matched_revenue']/k['total_revenue']*100 if k['total_revenue'] else 0
    progress_panel('Revenue distribution','Revenue with and without a verified match.',[
        ('Matched revenue',share,f"${k['matched_revenue']:,.2f}",'#EE512E'),
        ('Unverified revenue',100-share if k['total_revenue'] else 0,f"${k['total_revenue']-k['matched_revenue']:,.2f}",'#F4763C')],'analytics_revenue_split')
matched=filtered[filtered['status']=='Matched']
left,right=st.columns(2,gap='medium')
with left:
    with st.container(border=True, key="workspace_panel_marketing_dashboard_1"):
        st.subheader('Revenue over time')
        grouping=st.radio('Revenue grouping',['Daily','Weekly'],horizontal=True,label_visibility='collapsed')
        fig,note=revenue_chart(rows,weekly=grouping=='Weekly')
        chart_style(fig,currency=True,height=340)
        fig.update_layout(title_text='')
        show_chart(fig,'sales_trend')
        st.caption(note)
with right:
    with st.container(border=True, key="workspace_panel_marketing_dashboard_2"):
        st.subheader('Order volume over time')
        daily=filtered.dropna(subset=['order_date']).copy()
        daily['Date']=daily['order_date'].dt.strftime('%Y-%m-%d')
        counts=daily.groupby('Date').size()
        fig=go.Figure()
        if len(counts)==1: fig.add_bar(x=counts.index,y=counts.values,marker_color=BLUE)
        elif len(counts)>1: fig.add_scatter(x=counts.index,y=counts.values,mode='lines+markers',line_color=BLUE)
        chart_style(fig,height=340)
        fig.update_xaxes(title='Date',type='date' if len(counts)>1 else 'category',tickformat='%b %d')
        fig.update_yaxes(title='Orders',rangemode='tozero',dtick=1 if len(counts) and max(counts)<10 else None)
        show_chart(fig,'order_volume')
        if len(counts)==1: st.caption('Only one date is available; the bar shows its actual order count, not a trend.')
        elif counts.empty: st.caption('No valid dated orders in this selection.')


st.subheader('Channel performance')
channel=matched.groupby('channel',as_index=False).agg(revenue=('revenue','sum'),orders=('order_id','count')).sort_values('revenue')
left,right=st.columns(2,gap='medium')
for target,measure,title,color,currency in [(left,'revenue','Attributed revenue by channel',BLUE,True),(right,'orders','Matched orders by channel',GREEN,False)]:
    with target:
        with st.container(border=True, key=f"workspace_panel_marketing_dashboard_3_{measure}"):
            st.subheader(title)
            if channel.empty: st.info('No matched orders in this selection.')
            else:
                fig=px.bar(channel,x=measure,y='channel',orientation='h',color_discrete_sequence=[color],labels={measure:'Revenue ($)' if currency else 'Orders','channel':''})
                chart_style(fig,height=290)
                fig.update_xaxes(tickprefix='$' if currency else '',tickformat=',.0f',rangemode='tozero')
                fig.update_yaxes(showgrid=False)
                fig.update_traces(hovertemplate='%{y}<br>'+('$' if currency else '')+'%{x:,.2f}<extra></extra>' if currency else '%{y}<br>%{x} orders<extra></extra>')
                show_chart(fig,'channel_'+measure)

st.subheader('Campaign performance')
revenue_by_id=matched.groupby('campaign_id')['revenue'].sum().to_dict()
order_counts=matched.groupby('campaign_id').size().to_dict()
campaign_rows=[]
for campaign in selected_campaigns:
    revenue=revenue_by_id.get(campaign['campaign_id'],0)
    planned=amount(campaign.get('budget'))
    campaign_rows.append({'Campaign':campaign['campaign_name'],'Channel':campaign['channel'],'Attributed revenue':revenue,'Planned budget':planned,'Orders':order_counts.get(campaign['campaign_id'],0),'ROAS':revenue/planned if planned>0 else None})
performance=pd.DataFrame(campaign_rows,columns=['Campaign','Channel','Attributed revenue','Planned budget','Orders','ROAS'])
left,right=st.columns(2,gap='medium')
with left:
    with st.container(border=True, key="workspace_panel_marketing_dashboard_4"):
        st.subheader('Planned budget vs. matched revenue')
        if performance.empty: st.info('Select a campaign to compare results.')
        else:
            plot=performance.sort_values('Attributed revenue').melt(id_vars=['Campaign'],value_vars=['Planned budget','Attributed revenue'],var_name='Measure',value_name='Amount')
            fig=px.bar(plot,x='Amount',y='Campaign',color='Measure',orientation='h',barmode='group',color_discrete_map={'Planned budget':'#D6DDE8','Attributed revenue':BLUE})
            chart_style(fig,height=max(330,len(performance)*65))
            fig.update_xaxes(title='Amount ($)',tickprefix='$',rangemode='tozero')
            fig.update_yaxes(title='',showgrid=False,tickfont_size=14,tickmode='array',tickvals=performance['Campaign'].tolist(),ticktext=['<br>'.join(wrap(name,20)) for name in performance['Campaign']])
            fig.update_traces(hovertemplate='%{y}<br>$%{x:,.2f}<extra>%{fullData.name}</extra>')
            show_chart(fig,'campaign_comparison')
with right:
    with st.container(border=True, key="workspace_panel_marketing_dashboard_5"):
        st.subheader('Budget-based return')
        ranked=performance.dropna(subset=['ROAS']).sort_values('ROAS')
        if ranked.empty: st.info('ROAS is N/A for campaigns without a positive budget.')
        else:
            fig=px.bar(ranked,x='ROAS',y='Campaign',orientation='h',color_discrete_sequence=[RED])
            chart_style(fig,height=max(330,len(performance)*65))
            fig.update_xaxes(title='ROAS (x)',ticksuffix='x',tickangle=0,dtick=.5,rangemode='tozero')
            fig.update_yaxes(title='',showgrid=False,tickfont_size=14,tickmode='array',tickvals=performance['Campaign'].tolist(),ticktext=['<br>'.join(wrap(name,20)) for name in performance['Campaign']])
            fig.add_vline(x=1,line_dash='dot',line_color='#ACB5C3')
            fig.update_traces(hovertemplate='%{y}<br>%{x:.2f}x<extra></extra>')
            show_chart(fig,'campaign_return')
        st.caption('1.00x means revenue equals planned budget. It is not a profit break-even point. Zero-budget campaigns are N/A.')
with st.expander('View campaign details'):
    details=performance.copy()
    for name in ['Attributed revenue','Planned budget']: details[name]=details[name].map(lambda x:f'${x:,.2f}')
    details['ROAS']=details['ROAS'].map(lambda x:f'{x:.2f}x' if pd.notna(x) else 'N/A')
    st.dataframe(details,hide_index=True,width='stretch')

with st.container(border=True, key="workspace_panel_marketing_dashboard_7"):
    display_feedback_dashboard(filtered['order_id'].tolist())
with st.expander('Metric definitions and demo limitations'):
    st.write('Attribution coverage = matched orders ÷ selected orders × 100. Unattributed and Needs Review rates use the same order denominator. Average order value = total revenue ÷ selected orders.')
    st.write(f"Matched revenue: ${k['matched_revenue']:,.2f} · Planned budget: ${budget:,.2f} · Average order value: ${k['average_order_value']:,.2f}")
    st.write('Campaign/channel filters narrow verified matches; unverified orders remain unless excluded by status. Fictional seed data and demonstration checkouts only. Attribution is an association, not causation. No actual advertising spend, costs, authentication, payments, or durable cloud database are recorded.')
apply_workspace()
