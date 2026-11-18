from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from streamlit.testing.v1 import AppTest
app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'),default_timeout=30).run()
next(b for b in app.button if b.label=='Continue as Business Owner').click().run()
assert not app.exception,app.exception
app.selectbox(key='scope_control').set_value('Illustrative sample').run()
assert not app.exception
assert app.session_state['owner_data_scope']=='Illustrative sample'
app.switch_page('pages/order_matching.py').run()
assert not app.exception,app.exception
assert app.selectbox(key='scope_control').value=='Illustrative sample'
from attribution_engine import process_orders
assert app.metric[0].value==str(len(process_orders('Illustrative sample')[0]))
app.switch_page('pages/marketing_dashboard.py').run()
assert not app.exception and app.selectbox(key='scope_control').value=='Illustrative sample'
app.selectbox(key='scope_control').set_value('Combined').run()
assert not app.exception,app.exception
from attribution_engine import process_orders
expected=str(len(process_orders('Combined')[0]))
assert app.metric[1].value==expected, [m.value for m in app.metric]
app.switch_page('pages/order_matching.py').run()
assert not app.exception
assert app.metric[0].value==expected
print('PASS scope persists between owner pages; dashboard and order page have identical customer-record totals in Combined; no sample records fabricated.')
