import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from attribution_engine import calculate_kpis,process_orders,save_review
from workspace_ui import workspace_header,apply_workspace,chart_style,show_chart

workspace_header('Order Matching','Campaign attribution totals and tracking quality.','HOTVILE')
results,campaigns=process_orders()
status=st.selectbox('Attribution status',['All','Needs attention','Needs Review','Unattributed','Matched'])
selected=[r for r in results if status=='All' or r['status']==status or status=='Needs attention' and r['status']!='Matched']
k=calculate_kpis(selected)
with st.container(key="workspace_metrics"):
    a,b,c,d=st.columns(4)
    a.metric('Total Orders',k['total_orders'])
    b.metric('Matched',k['matched_orders'])
    c.metric('Attribution Coverage',f"{k['coverage']:.1f}%")
    d.metric('Needs attention',k['unattributed_orders']+k['needs_review'])
st.caption(f"{len(selected)} of {len(results)} orders selected")
if st.session_state.pop('review_saved',None): st.success('Review saved. Dashboard totals are updated.')
left,right=st.columns(2,gap='large')
statuses=['Matched','Unattributed','Needs Review']
colors=['#C94817','#D9A43A','#A5AFAB']
counts=[sum(r['status']==s for r in selected) for s in statuses]
revenues=[sum(r['revenue'] for r in selected if r['status']==s) for s in statuses]
with left:
    with st.container(border=True,key='workspace_panel_matching_status'):
        st.subheader('Orders by attribution status')
        if selected:
            fig=go.Figure(go.Pie(labels=statuses,values=counts,hole=.65,sort=False,marker_colors=colors,textinfo='text',text=[f'{v/len(selected)*100:.0f}%' if v else '' for v in counts],hovertemplate='%{label}<br>%{value} orders · %{percent}<extra></extra>'))
            chart_style(fig,height=370)
            fig.update_layout(showlegend=False,margin=dict(l=10,r=10,t=15,b=20))
            show_chart(fig,'matching_status_breakdown')
            legend=''.join(f'<div><i style="background:{color}"></i><span>{label}</span><b>{count} · {count/len(selected)*100:.1f}%</b></div>' for label,count,color in zip(statuses,counts,colors))
            st.markdown(f'<div class="matching-legend">{legend}</div>',unsafe_allow_html=True)
        else: st.info('No orders in this selection.')
with right:
    with st.container(border=True,key='workspace_panel_matching_revenue'):
        st.subheader('Revenue by attribution status')
        if selected:
            fig=go.Figure(go.Bar(x=statuses,y=revenues,marker_color=colors,hovertemplate='%{x}<br>$%{y:,.2f}<extra></extra>'))
            chart_style(fig,currency=True,height=370)
            fig.update_xaxes(title='Attribution status')
            fig.update_yaxes(title='Revenue ($)')
            show_chart(fig,'matching_revenue_breakdown')
        else: st.info('No revenue in this selection.')

if st.checkbox('Open order review tools',key='show_order_review'):
    search=st.text_input('Search orders',placeholder='Customer, campaign, or order reference').strip().casefold()
    rows=[r for r in selected if not search or search in ' '.join(str(r.get(key,'')) for key in ['customer_name','campaign_name','order_id']).casefold()]
    def day(value):
        parsed=pd.to_datetime(value,errors='coerce',utc=True)
        return parsed.strftime('%b %d, %Y') if pd.notna(parsed) else 'Unavailable'
    table=pd.DataFrame([{'Customer':r['customer_name'],'Date':day(r.get('order_date')),'Total':f"${r['revenue']:,.2f}",'Status':r['status'],'Campaign':r['campaign_name'] if r['status']=='Matched' else 'Not verified','Channel':r['channel']} for r in rows],columns=['Customer','Date','Total','Status','Campaign','Channel'])
    st.dataframe(table,hide_index=True,width='stretch',height=380)
    st.subheader('Review an order')
    if not rows: st.info('No orders match these filters.')
    else:
        by_id={r['order_id']:r for r in rows}
        chosen=st.selectbox('Select an order to review',list(by_id),format_func=lambda key:f"{by_id[key]['customer_name']} · {key[-8:]} · ${by_id[key]['revenue']:,.2f}")
        order=by_id[chosen]
        left,right=st.columns([1,1.3],gap='medium')
        with left:
            with st.container(border=True, key="workspace_panel_order_matching_1"):
                st.subheader('Order details')
                st.write(order['customer_name'])
                st.caption(f"{day(order.get('order_date'))} · {order['order_id']}")
                st.write(order.get('items') or 'No item details recorded')
                st.metric('Order total',f"${order['revenue']:,.2f}")
                st.write(f"Status: {order['status']}")
                st.caption(order['reason'])
        with right:
            with st.form(f"review_{order['order_id']}"):
                st.subheader('Attribution decision')
                decision=st.selectbox('Review decision',['Assign to campaign','Keep unattributed','Restore automatic matching'])
                options={c['campaign_id']:c for c in campaigns}
                campaign_id=st.selectbox('Campaign to assign',list(options),format_func=lambda key:options[key]['campaign_name']) if options else None
                note=st.text_input('Evidence / review note',placeholder='Explain the evidence for this decision',help='Original tracking is preserved in the order record.')
                if st.form_submit_button('Save Review',type='primary'):
                    action={'Assign to campaign':'Matched','Keep unattributed':'Unattributed','Restore automatic matching':'Automatic'}[decision]
                    try: save_review(order['order_id'],action,campaign_id,note)
                    except ValueError as error: st.error(str(error))
                    else:
                        st.session_state['review_saved']=order['order_id'];st.rerun()

with st.expander('Status definitions'):
    st.write('Matched: verified campaign ID or promo code. Unattributed: no tracking signal. Needs Review: invalid or conflicting tracking. Attribution does not prove causation.')
apply_workspace()
