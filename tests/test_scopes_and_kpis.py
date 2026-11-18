import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import attribution_engine as engine
from data_store import append_unique

class ScopeAndKpiTests(unittest.TestCase):
    def test_all_statuses_share_the_same_denominator(self):
        rows=[dict(status='Matched',revenue=20),dict(status='Matched',revenue=10),dict(status='Unattributed',revenue=5),dict(status='Needs Review',revenue=15)]
        k=engine.calculate_kpis(rows)
        self.assertEqual(k['coverage'],50)
        self.assertEqual(k['unattributed_rate'],25)
        self.assertEqual(k['needs_review_rate'],25)
        self.assertEqual(k['total_revenue'],50)
        self.assertEqual(k['matched_revenue'],30)
        self.assertEqual(k['average_order_value'],12.5)
        self.assertEqual(k['matched_orders']+k['unattributed_orders']+k['needs_review'],k['total_orders'])
        empty=engine.calculate_kpis([])
        self.assertEqual((empty['coverage'],empty['unattributed_rate'],empty['needs_review_rate']),(0,0,0))

    def test_scopes_do_not_cross_match_duplicate_campaign_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            customer=dict(campaign_id='C1',campaign_name='Customer campaign',promo_code='SAME',channel='Social',budget='30')
            sample=dict(customer,campaign_name='Sample campaign',channel='Market',budget='70')
            orders=[dict(order_id='O1',campaign_id='C1',promo_code='',order_total='20'),dict(order_id='O2',campaign_id='',promo_code='',order_total='5')]
            for name,row,key in [('campaigns.csv',customer,'campaign_id'),('sample_campaigns.csv',sample,'campaign_id'),('sample_orders.csv',dict(orders[0],order_total='40'),'order_id')]:
                append_unique(directory/name,list(row),row,key)
            for row in orders: append_unique(directory/'orders.csv',list(row),row,'order_id')
            with patch.multiple(engine,DATA_DIR=directory,ORDERS_FILE=directory/'orders.csv',CAMPAIGNS_FILE=directory/'campaigns.csv'):
                current,campaigns=engine.process_orders('Customer orders')
                examples,example_campaigns=engine.process_orders('Illustrative sample')
                both,both_campaigns=engine.process_orders('Combined')
                self.assertEqual(len(current),2);self.assertEqual(len(examples),1);self.assertEqual(len(both),3)
                self.assertEqual(examples[0]['channel'],'Market')
                self.assertEqual(current[0]['channel'],'Social')
                self.assertEqual(len({r['order_id'] for r in both}),3)
                self.assertEqual(sum(float(c['budget']) for c in both_campaigns),100)
                self.assertEqual(engine.calculate_kpis(both)['total_revenue'],65)
                (directory/'sample_orders.csv').unlink()
                (directory/'sample_campaigns.csv').unlink()
                self.assertEqual(engine.process_orders('Illustrative sample'),([],[]))
