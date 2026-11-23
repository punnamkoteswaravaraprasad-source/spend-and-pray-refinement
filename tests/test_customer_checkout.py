import csv
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import attribution_engine as engine


class CustomerCheckoutTests(unittest.TestCase):
    def test_name_validation_and_cart_order_link(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp); (target/'pages').mkdir(); (target/'data').mkdir()
            shutil.copy(root/'pages/hot_sauce_store.py',target/'pages/hot_sauce_store.py')
            app=AppTest.from_file(str(target/'pages/hot_sauce_store.py'),default_timeout=30).run()
            def click(label):
                next(b for b in app.button if b.label==label).click().run()
                self.assertFalse(app.exception)
            next(b for b in app.button if b.key=='add_1').click().run()
            next(b for b in app.button if b.key=='plus_1').click().run()
            next(b for b in app.button if b.key=='add_6').click().run()
            click('Place order  →')
            self.assertTrue(app.error)
            self.assertFalse((target/'data/demo_orders.csv').exists())
            app.text_input(key='checkout_name').set_value('  Jordan Lee  ')
            app.text_input(key='checkout_email').set_value('invalid-email')
            click('Place order  →');self.assertTrue(app.error)
            self.assertFalse((target/'data/demo_orders.csv').exists())
            app.text_input(key='checkout_email').set_value('')
            click('Place order  →')
            order=app.session_state['last_order']
            self.assertEqual(order['customer_name'],'Jordan Lee')
            self.assertEqual(order['items'],'Classic Red Hot Sauce x2; Ghost Pepper x1')
            self.assertAlmostEqual(order['order_total'],30.97)
            with (target/'data/demo_orders.csv').open(newline='',encoding='utf-8-sig') as file:
                saved=list(csv.DictReader(file))
            self.assertEqual(len(saved),1)
            self.assertEqual(saved[0]['customer_name'],'Jordan Lee')
            self.assertEqual(saved[0]['order_id'],order['order_id'])
            self.assertEqual(saved[0]['items'],order['items'])
            self.assertTrue(any(t.value=='Customer: Jordan Lee' for t in app.text))
            self.assertFalse(app.session_state['cart'])
            with patch.multiple(engine,DATA_DIR=target/'data',ORDERS_FILE=target/'data/demo_orders.csv',CAMPAIGNS_FILE=target/'data/campaigns.csv'):
                rows,_=engine.process_orders()
                self.assertEqual(rows[0]['customer_name'],'Jordan Lee')
                self.assertEqual(rows[0]['items'],order['items'])
