import pandas as pd
import streamlit as st
from attribution_engine import calculate_kpis,process_orders,save_review
from workspace_ui import workspace_header,apply_workspace
workspace_header('Order matching','Review tracking signals and resolve orders with missing or conflicting attribution.','ATTRIBUTION')
results,campaigns=process_orders()
k=calculate_kpis(results)
with st.container(key="workspace_metrics"):
    a,b,c,d=st.columns(4)
    a.metric('Total Orders',k['total_orders'])
    b.metric('Matched',k['matched_orders'])
    c.metric('Attribution Coverage',f"{k['coverage']:.1f}%")
    d.metric('Needs attention',k['unattributed_orders']+k['needs_review'])
st.caption(f"Unattributed: {k['unattributed_orders']} ({k['unattributed_rate']:.1f}%) · Needs Review: {k['needs_review']} ({k['needs_review_rate']:.1f}%) · Matched revenue: ${k['matched_revenue']:,.2f}")
if st.session_state.pop('review_saved',None): st.success('Review saved. Dashboard metrics now reflect the updated attribution; original tracking is preserved.')
with st.container(border=True, key="workspace_panel_order_matching_0"):
    left,right=st.columns([1,2])
    with left: status=st.selectbox('Attribution status',['All','Needs attention','Needs Review','Unattributed','Matched'])
    with right: search=st.text_input('Search orders',placeholder='Customer, campaign, or order reference').strip().casefold()
    rows=[r for r in results if (status=='All' or r['status']==status or status=='Needs attention' and r['status']!='Matched') and (not search or search in ' '.join(str(r.get(key,'')) for key in ['customer_name','campaign_name','order_id']).casefold())]
    st.caption(f'{len(rows):,} of {len(results):,} orders')
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
with st.expander('How attribution works'):
    st.write('Matched: verified campaign ID or promo code. Unattributed: no tracking signal. Needs Review: invalid or conflicting signals. Attribution indicates an association; it does not prove that a campaign caused a purchase.')
apply_workspace()
