"""Exercise interfaces in a temporary copy without changing the project dataset."""
from pathlib import Path
import sys, shutil, csv, math
from tempfile import TemporaryDirectory
from datetime import date
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parents[1]
with TemporaryDirectory(dir=root.parent) as tmp:
    copy=Path(tmp)/'app'
    shutil.copytree(root,copy,ignore=shutil.ignore_patterns('.git','.venv','__pycache__'))
    sys.path.insert(0,str(copy))
    from attribution_engine import process_orders,calculate_kpis
    def read(name):
        with (copy/'data'/name).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
    orders,campaigns=process_orders()
    assert len(orders)==150 and len(campaigns)==6
    k=calculate_kpis(orders)
    assert (k['matched_orders'],k['unattributed_orders'],k['needs_review'])==(120,30,0)
    assert math.isclose(k['coverage'],80)
    feedback=read('customer_feedback.csv')
    assert len(feedback)==65 and len({r['order_id'] for r in feedback})==65
    assert all(r['order_id'] in {o['order_id'] for o in orders} for r in feedback)
    print('PASS baseline: 6 campaigns, 150 orders, 65 linked responses, 80% coverage')
    def page(name):
        a=AppTest.from_file(str(copy/name),default_timeout=40).run()
        assert not a.exception,a.exception
        return a
    def click(a,label):
        next(b for b in a.button if b.label==label).click().run()
        assert not a.exception,a.exception
    a=page('app.py');click(a,'Enter Business Owner View →')
    assert any(m.value=='150' for m in a.metric)
    print('PASS welcome and owner overview')
    a=page('pages/create_campaign.py')
    click(a,'Create Campaign Assets');assert a.error
    a.text_input[0].set_value('Date validation')
    a.date_input[0].set_value(date(2026,11,20));a.date_input[1].set_value(date(2026,11,1))
    click(a,'Create Campaign Assets');assert a.error
    a.date_input[1].set_value(date(2026,11,30))
    click(a,'Create Campaign Assets');assert not a.error
    assert len(read('campaigns.csv'))==7
    print('PASS campaign creation, blank-name and invalid-date validation')
    a=page('pages/order_matching.py')
    assert any(m.value=='150' for m in a.metric)
    a=page('pages/marketing_dashboard.py')
    assert len(a.get('plotly_chart'))>=6
    assert any(m.value=='150' for m in a.metric)
    selected=a.date_input[0].value[0]
    a.date_input[0].set_value((selected,selected)).run()
    assert not a.exception,a.exception
    assert any('not a trend' in c.value for c in a.caption)
    a.multiselect[2].set_value([]).run()
    assert not a.exception,a.exception
    assert a.metric[0].value=='$0.00'
    print('PASS matching totals, charts, single-date and empty filters')
    a=page('pages/hot_sauce_store.py')
    a.selectbox[0].set_value('Extra Hot').run()
    assert len([b for b in a.button if str(b.key).startswith('add_')])==1
    next(b for b in a.button if b.key=='add_6').click().run()
    a.text_input(key='checkout_name').set_value('QA Fictional Shopper')
    click(a,'Place order  →')
    assert a.session_state['last_order']['items']=='Ghost Pepper x1'
    assert len(read('demo_orders.csv'))==151
    assert not a.session_state['cart']
    print('PASS heat filter, cart, checkout, confirmation and linked order')
    for path in (copy/'data').glob('*.csv'):path.rename(path.with_suffix('.backup'))
    for name in ['app.py','pages/create_campaign.py','pages/hot_sauce_store.py','pages/marketing_dashboard.py','pages/order_matching.py']:page(name)
    print('PASS missing CSV files on all five interfaces')
    # A nonempty order file with no parseable date also needs a stable state.
    with (copy/'data/demo_orders.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['order_id','order_date','order_total','campaign_id','promo_code'])
        writer.writeheader();writer.writerow(dict(order_id='invalid-date',order_date='bad',order_total='10',campaign_id='',promo_code=''))
    a=page('pages/marketing_dashboard.py')
    assert a.warning and a.metric[0].value=='$0.00'
    print('PASS all-invalid order dates')
