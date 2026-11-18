from owner_scope import owner_scope
from collections import defaultdict
import plotly.graph_objects as go
import streamlit as st
from attribution_engine import calculate_kpis, process_orders
from dashboard_charts import order_day, revenue_chart, cumulative_revenue_chart
from reporting import select_report, amount
from ui import apply_theme, hero, section_label, chart_layout, BRAND_RED, BRAND_ORANGE, BRAND_GOLD, BRAND_GREEN, show_chart, chart_explanation

apply_theme()
all_results, all_campaigns = process_orders(owner_scope())
hero('The story behind your sales', 'See what sold, what marketing can explain, and what to investigate next.', 'Owner dashboard', icon='📊')
if not all_results:
    st.info('Place a demo order to start measuring performance.')
    st.stop()

with st.expander('KPI definitions and formulas'):
    st.markdown('**Coverage** = matched orders ÷ selected orders × 100. **Unattributed rate** = unattributed orders ÷ selected orders × 100. **Needs review rate** = review orders ÷ selected orders × 100. Counts include every selected status; the three percentages sum to 100% when orders exist. Empty selections show 0%. Revenue is USD; average order value is revenue ÷ orders. Budget-based ROAS is matched revenue ÷ selected full planned budgets; no positive budget means N/A.')

with st.expander('Filter this report', expanded=False):
    st.markdown('### Report filters')
    channels = sorted({r['channel'] for r in all_results} | {c.get('channel') or 'Unknown' for c in all_campaigns})
    chosen_channels = st.multiselect('Channels', channels, default=channels)
    campaign_map = {c['campaign_id']: c for c in all_campaigns}
    choices = list(campaign_map) + ['__unassigned__']
    chosen_campaigns = st.multiselect('Campaigns', choices, default=choices,
        format_func=lambda key: 'No verified campaign' if key == '__unassigned__' else f"{campaign_map[key]['campaign_name']} · {campaign_map[key].get('channel', 'Unknown')} · {key[-4:]}")
    statuses = ['Matched', 'Unattributed', 'Needs Review']
    chosen_statuses = st.multiselect('Attribution statuses', statuses, default=statuses)
    limit_dates = st.checkbox('Limit order dates', value=False)
    dates = None
    valid_days = sorted({order_day(r.get('order_date')) for r in all_results} - {None})
    if limit_dates and valid_days:
        selected_dates = st.date_input('Order dates (UTC)', (valid_days[0], valid_days[-1]))
        if len(selected_dates) != 2:
            st.info('Choose both a start and end date to run the report.')
            st.stop()
        dates = selected_dates
    elif limit_dates:
        st.warning('No valid order dates are available.')
        st.stop()
    weekly = st.selectbox('Revenue grouping', ['Daily', 'Weekly']) == 'Weekly'
    st.caption('All KPIs and charts use these filters. Unknown channel and No verified campaign include tracking gaps. Planned budgets are full allocations for selected campaigns, not prorated spending during the order-date range.')

results, campaigns = select_report(all_results, all_campaigns, chosen_channels, chosen_campaigns, chosen_statuses, dates)
if dates:
    before_date_filter, _ = select_report(all_results, all_campaigns, chosen_channels, chosen_campaigns, chosen_statuses)
    excluded_dates = sum(order_day(r.get('order_date')) is None for r in before_date_filter)
    if excluded_dates:
        st.warning(f'{excluded_dates} order(s) excluded from this date-limited report because their dates are missing or invalid. Turn off Limit order dates to include them in overall totals.')
kpis = calculate_kpis(results)
total_budget = sum(amount(c.get('budget')) for c in campaigns)
with st.container(border=True, key='story_setup'):
    section_label('Setup · Sales overview')
    st.markdown(f"### {kpis['total_orders']} orders generated ${kpis['total_revenue']:,.2f}")
    st.caption('This story describes the current report selection. Change filters to explore a different set of orders.')
    with st.container(border=True, key='sales_kpis'):
        section_label('Sales')
        a,b,c = st.columns(3)
        a.metric('Revenue', f"${kpis['total_revenue']:,.2f}")
        b.metric('Orders', kpis['total_orders'])
        c.metric('Average order value', f"${kpis['average_order_value']:,.2f}")

    if not results:
        st.info('No orders match this selection. Adjust the report filters; budget allocations may still exist for selected campaigns.')
        st.stop()


    view = st.radio('Revenue view', ['Daily / weekly totals', 'Cumulative by order'], horizontal=True,
                    help='Date totals are the default. Cumulative revenue shows a running total by order.')
    left, right = st.columns(2, gap='large')
    with left:
        fig,note = cumulative_revenue_chart(results) if view == 'Cumulative by order' else revenue_chart(results, weekly)
        show_chart(fig)
        st.caption(note)
    with right:
        fig, order_note = revenue_chart([dict(r, revenue=1) for r in results], weekly)
        fig.update_layout(title_text='Orders Over Time')
        fig.update_yaxes(title_text='Orders', tickprefix='', tickformat=',d', dtick=1)
        for trace in fig.data:
            trace.hovertemplate = ('%{customdata}' if getattr(trace, 'customdata', None) is not None else '%{x}') + '<br>Orders: %{y}<extra></extra>'
            if trace.type == 'bar':
                trace.text = [str(int(y)) for y in trace.y]
        show_chart(fig)
        st.caption(order_note.replace('revenue', 'orders').replace('Revenue', 'Orders'))

with st.container(border=True, key='story_conflict'):
    section_label('Conflict · What the sales total cannot explain')
    unresolved_revenue = kpis['total_revenue'] - kpis['matched_revenue']
    unresolved_orders = kpis['unattributed_orders'] + kpis['needs_review']
    if unresolved_orders:
        st.markdown(f"### ${unresolved_revenue:,.2f} in sales has no verified campaign match")
        st.write(f"{unresolved_orders} of {kpis['total_orders']} orders are unattributed or need review. Channel comparisons account for ${kpis['matched_revenue']:,.2f}, not every sale.")
    else:
        st.markdown('### Every selected order is matched, but attribution is not proof of impact')
        st.write('There are no tracking gaps in this selection. Planned budget is still different from actual spending, so this report cannot establish profitability or causation.')
    with st.container(border=True, key='marketing_kpis'):
        section_label('Marketing')
        a,b,c = st.columns(3)
        a.metric('Matched revenue', f"${kpis['matched_revenue']:,.2f}")
        b.metric('Planned campaign budget', f'${total_budget:,.2f}')
        c.metric('Budget-based ROAS', f"{kpis['matched_revenue']/total_budget:.2f}x" if total_budget > 0 else 'N/A')
        st.caption('ROAS here compares selected order revenue with full planned campaign budgets. Actual ad spend and profit are not recorded. Attribution shows association, not causation.')

    with st.container(border=True, key='tracking_kpis'):
        section_label('Tracking quality')
        a,b,c = st.columns(3)
        a.metric('Attribution coverage', f"{kpis['coverage']:.1f}%")
        b.metric('Unattributed order rate', f"{kpis['unattributed_rate']:.1f}%", help=f"{kpis['unattributed_orders']} of {kpis['total_orders']} selected orders")
        c.metric('Needs review rate', f"{kpis['needs_review_rate']:.1f}%", help=f"{kpis['needs_review']} of {kpis['total_orders']} selected orders")

    st.markdown('### Product demand and attribution tell different parts of the story')
    from product_metrics import product_units
    units, unparsed = product_units(results)
    if units:
        most_units = max(units.values())
        leaders = [name for name, count in units.items() if count == most_units]
        st.write(f"{' / '.join(leaders)} {'tie for the most' if len(leaders)>1 else 'has the most'} recorded bottles sold ({most_units}). Product demand alone does not identify which campaign brought those customers.")
    left,right=st.columns(2,gap='large')
    with left:
        if units:
            labels=sorted(units,key=units.get,reverse=True)
            fig=go.Figure(go.Bar(x=labels,y=[units[n] for n in labels],marker_color=BRAND_ORANGE,
                                hovertemplate='%{x}<br>Bottles: %{y}<extra></extra>'))
            fig.update_layout(**chart_layout('Bottles Sold by Sauce','Bottles',450))
            fig.update_xaxes(title_text='Sauce')
            fig.update_yaxes(dtick=1)
            show_chart(fig)
        else:
            st.info('No readable product quantities in the selected orders.')
        st.caption('Recorded item quantities. Product-level revenue is not estimated from current prices.')
        if unparsed:
            st.warning(f'{unparsed} item entry/entries could not be parsed and are excluded from product counts.')
    with right:
        counts=[sum(r['status']==s for r in results) for s in statuses]
        fig=go.Figure(go.Pie(labels=statuses,values=counts,hole=.65,sort=False,
                            marker_colors=[BRAND_GREEN,'#687587',BRAND_GOLD],textinfo='none',
                            hovertemplate='%{label}: %{value} orders (%{percent})<extra></extra>'))
        fig.update_layout(**chart_layout('Order Attribution Status',height=450))
        fig.update_layout(legend=dict(orientation='h',y=-.1,x=0),annotations=[dict(text=f"<b>{kpis['total_orders']}</b><br>Total orders",x=.5,y=.5,showarrow=False,font_size=20)])
        show_chart(fig)
        st.caption(f"{kpis['coverage']:.1f}% matched · {kpis['unattributed_orders']} unattributed · {kpis['needs_review']} need review")
    st.progress(kpis['coverage']/100,text=f"Attribution coverage: {kpis['coverage']:.1f}%")
    if kpis['needs_review'] or kpis['unattributed_orders']:
        chart_explanation('Next action', f"Review {kpis['needs_review']} uncertain and {kpis['unattributed_orders']} unattributed order(s) before adjusting campaign budgets.")
    else:
        chart_explanation('Next action', 'All selected orders are matched. Compare results with planned budgets, and collect more orders before drawing conclusions.')
    st.link_button('Review order attribution','order_matching',icon='🔎')
    with st.expander('View attribution details'):
        st.dataframe([{'Status':status,'Orders':count,'Share':f'{count/kpis["total_orders"]:.1%}'} for status,count in zip(statuses,counts)],hide_index=True,width='stretch')
    invalid=sum(order_day(r.get('order_date')) is None for r in results)
    if invalid:
        st.warning(f'{invalid} order(s) have missing or invalid dates. They remain in all-date KPIs but are excluded from dated charts.')

with st.container(border=True, key='story_resolution'):
    section_label('Resolution · Use the evidence to decide')
    if unresolved_orders:
        st.markdown('### Resolve the tracking gaps before changing campaign budgets')
    else:
        st.markdown('### Compare matched results and gather more evidence')
    st.write('Use the channel and campaign comparisons below to identify what to investigate. Budget-based ROAS is directional; it does not measure profit.')
    st.markdown('### Compare the verified results')
    summary = defaultdict(lambda: {'revenue':0.0, 'orders':0, 'budget':0.0})
    campaign_revenue = defaultdict(float)
    for row in results:
        if row['status']=='Matched':
            summary[row['channel']]['revenue'] += row['revenue']
            summary[row['channel']]['orders'] += 1
            campaign_revenue[row['campaign_id']] += row['revenue']
    for campaign in campaigns:
        summary[campaign.get('channel') or 'Unknown']['budget'] += amount(campaign.get('budget'))
    names = sorted(summary, key=lambda n: summary[n]['revenue'], reverse=True)
    if names and summary[names[0]]['revenue'] > 0:
        top_revenue = summary[names[0]]['revenue']
        leaders = [name for name in names if abs(summary[name]['revenue'] - top_revenue) < .005]
        chart_explanation('What this comparison shows',
            f"{' / '.join(leaders)} {'tie for the highest' if len(leaders)>1 else 'has the highest'} matched revenue at ${top_revenue:,.2f}. This ranking covers verified matches in the current selection, not proven advertising impact.")
    if names:
        left,right = st.columns(2,gap='large')
        with left:
            fig=go.Figure(go.Bar(x=names,y=[summary[n]['revenue'] for n in names],marker_color=BRAND_RED,
                                hovertemplate='%{x}<br>Revenue: $%{y:,.2f}<extra></extra>'))
            fig.update_layout(**chart_layout('Revenue by Channel','Revenue ($)',430))
            fig.update_xaxes(title_text='Channel')
            show_chart(fig)
        with right:
            fig=go.Figure(go.Bar(x=names,y=[summary[n]['orders'] for n in names],marker_color=BRAND_ORANGE,
                                hovertemplate='%{x}<br>Orders: %{y}<extra></extra>'))
            fig.update_layout(**chart_layout('Orders by Channel','Matched orders',430))
            fig.update_yaxes(dtick=1)
            fig.update_xaxes(title_text='Channel')
            show_chart(fig)
        fig=go.Figure()
        for name,key,color in [('Matched revenue','revenue',BRAND_RED),('Planned budget','budget',BRAND_GOLD)]:
            fig.add_trace(go.Bar(name=name,x=names,y=[summary[n][key] for n in names],marker_color=color,
                                hovertemplate='%{x}<br>$%{y:,.2f}<extra>%{fullData.name}</extra>'))
        fig.update_layout(**chart_layout('Channel Revenue vs Planned Budget','Amount ($)',450),barmode='group')
        fig.update_xaxes(title_text='Channel')
        show_chart(fig)
        chart_explanation('Budget context', 'Gold is the full planned allocation for selected campaigns; red is matched revenue in the selected orders. Actual spending and profit are not recorded.')
        with st.expander('View channel details'):
            st.dataframe([{'Channel':n,'Orders':summary[n]['orders'],'Revenue ($)':summary[n]['revenue'],'Planned budget ($)':summary[n]['budget']} for n in names],hide_index=True,width='stretch',column_config={'Revenue ($)':st.column_config.NumberColumn(format='$%.2f'),'Planned budget ($)':st.column_config.NumberColumn(format='$%.2f')})
    else:
        st.info('No verified channel data matches this selection.')

    if campaigns:
        ranked=sorted(campaigns,key=lambda c:campaign_revenue[c['campaign_id']],reverse=True)
        labels=[f"{c['campaign_name']} · {c['campaign_id'][-4:]}" for c in ranked]
        left,right=st.columns(2,gap='large')
        with left:
            fig=go.Figure(go.Bar(y=labels,x=[campaign_revenue[c['campaign_id']] for c in ranked],orientation='h',marker_color=BRAND_RED,
                                hovertemplate='%{y}<br>Revenue: $%{x:,.2f}<extra></extra>'))
            fig.update_layout(**chart_layout('Campaign Revenue Ranking',height=max(470,len(labels)*65+160)))
            fig.update_layout(margin=dict(l=155,r=30,t=85,b=75))
            fig.update_xaxes(title_text='Revenue ($)',tickprefix='$',tickformat=',.0f')
            from textwrap import wrap
            fig.update_yaxes(tickmode='array',tickvals=labels,ticktext=['<br>'.join(wrap(label,18)) for label in labels],autorange='reversed',automargin=True)
            show_chart(fig)
        with right:
            eligible=[c for c in ranked if amount(c.get('budget'))>0]
            if eligible:
                ratios=[campaign_revenue[c['campaign_id']]/amount(c.get('budget')) for c in eligible]
                fig=go.Figure(go.Bar(y=[f"{c['campaign_name']} · {c['campaign_id'][-4:]}" for c in eligible],x=ratios,orientation='h',
                                    marker_color=[BRAND_GREEN if r>=1 else BRAND_ORANGE for r in ratios],
                                    hovertemplate='%{y}<br>Budget-based ROAS: %{x:.2f}x<extra></extra>'))
                fig.update_layout(**chart_layout('Campaign Budget-Based ROAS',height=max(470,len(eligible)*65+160)))
                fig.update_layout(margin=dict(l=155,r=30,t=85,b=75))
                fig.update_xaxes(title_text='Budget-based ROAS',ticksuffix='x')
                ratio_labels=[f"{c['campaign_name']} · {c['campaign_id'][-4:]}" for c in eligible]
                fig.update_yaxes(tickmode='array',tickvals=ratio_labels,ticktext=['<br>'.join(wrap(label,18)) for label in ratio_labels],autorange='reversed',automargin=True)
                fig.add_vline(x=1,line_dash='dot',line_color=BRAND_GOLD)
                st.caption('1.00x: revenue equals planned budget. This is not a profit break-even point.')
                show_chart(fig)
            else:
                st.info('ROAS is N/A: no selected campaign has a positive planned budget.')
            if len(eligible)<len(ranked):
                st.caption(f'{len(ranked)-len(eligible)} campaign(s) have no positive budget; ROAS is N/A and excluded from this chart.')
        with st.expander('View campaign details'):
            st.dataframe([{'Campaign':c['campaign_name'],'Source':c['data_source'],'Revenue ($)':campaign_revenue[c['campaign_id']],
                           'Planned budget ($)':amount(c.get('budget')),
                           'Budget-based ROAS':f"{campaign_revenue[c['campaign_id']]/amount(c.get('budget')):.2f}x" if amount(c.get('budget'))>0 else 'N/A'} for c in ranked],hide_index=True,width='stretch',column_config={'Revenue ($)':st.column_config.NumberColumn(format='$%.2f'),'Planned budget ($)':st.column_config.NumberColumn(format='$%.2f')})

    st.markdown('### Choose the next step')
    left,right=st.columns(2,gap='large')
    with left:
        with st.container(border=True):
            st.markdown('#### Launch or refine a campaign')
            st.write('Create a campaign, then copy its tracking link or download its QR code. Test the customer journey before sharing.')
            st.link_button('Open campaign builder', 'create_campaign', icon='📣')
            st.caption('Local links work on this computer only. Public sharing requires the hosted app.')
    with right:
        with st.container(border=True):
            st.markdown('#### Close the tracking gaps')
            st.write(f"Review {kpis['needs_review']} uncertain and {kpis['unattributed_orders']} unattributed order(s) in this selection. Record evidence before assigning a campaign.")
            st.link_button('Open attribution review', 'order_matching', icon='🔎')
            st.caption('Revisit the report after reviews or new orders. Actual spending and profit are not tracked.')
