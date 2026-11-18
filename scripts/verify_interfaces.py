from pathlib import Path
import sys,shutil,csv,json
from tempfile import TemporaryDirectory
from streamlit.testing.v1 import AppTest
root=Path(__file__).resolve().parents[1]
with TemporaryDirectory(dir=root.parent) as tmp:
    copy=Path(tmp)/'app';shutil.copytree(root,copy,ignore=shutil.ignore_patterns('.git','.venv','__pycache__'))
    if not list(csv.DictReader((copy/'data/demo_orders.csv').open(encoding='utf-8-sig'))):
        shutil.copy(copy/'data/sample_orders.csv',copy/'data/demo_orders.csv')
        shutil.copy(copy/'data/sample_campaigns.csv',copy/'data/campaigns.csv')
    sys.path.insert(0,str(copy))
    def page(name):
        a=AppTest.from_file(str(copy/name),default_timeout=30); a.session_state['owner_data_scope']='Customer orders'; a.run();assert not a.exception,a.exception;return a
    def button(a,label):return next(b for b in a.button if b.label==label)
    a=page('pages/create_campaign.py')
    button(a,'Create Campaign Assets').click().run();assert a.error and not a.exception
    a.text_input[0].set_value('Bad dates')
    from datetime import date
    a.date_input[0].set_value(date(2026,11,20));a.date_input[1].set_value(date(2026,11,1))
    button(a,'Create Campaign Assets').click().run();assert a.error and not a.exception
    print('PASS blank campaign name and invalid date range validation')
    a=page('pages/hot_sauce_store.py')
    a.segmented_control[0].set_value('Extra Hot').run();assert len([b for b in a.button if b.label=='Add to Cart'])==1
    next(b for b in a.button if b.key=='add_6').click().run()
    a.text_input(key='checkout_name').set_value('QA Customer'); next(w for w in a.text_input if w.label=='Promo Code (optional)').set_value('NOT-A-CODE');button(a,'Place demo order').click().run();assert a.error and not a.exception
    a.number_input[0].set_value(99).run()
    assert next(b for b in a.button if b.key=='add_6').disabled
    assert a.session_state['cart'][6] == 99
    assert not a.exception,a.exception
    print('PASS heat filter, invalid promo and maximum cart quantity')
    button(a,'Clear Cart').click().run();assert not a.exception and not a.session_state['cart']
    print('PASS clear cart')
    a=page('pages/marketing_dashboard.py')
    assert len(a.get('plotly_chart'))>=8
    a.checkbox[0].check().run();assert not a.exception,a.exception
    a.date_input[0].set_value((date(2026,1,1),date(2026,1,2))).run();assert not a.exception
    assert a.metric[0].value=='$0.00', ([m.value for m in a.metric], a.date_input[0].value)
    print('PASS empty date-filter results')
    # Missing data should show useful empty states on every owner/customer screen.
    for path in (copy/'data').glob('*.csv'):path.rename(path.with_suffix('.backup'))
    for name in ['app.py','pages/create_campaign.py','pages/hot_sauce_store.py','pages/marketing_dashboard.py','pages/order_matching.py']:
        page(name)
    print('PASS missing CSV files on all five pages')
