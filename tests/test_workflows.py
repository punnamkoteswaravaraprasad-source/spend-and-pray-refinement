import tempfile
import unittest
from pathlib import Path
from datetime import date
from unittest.mock import patch
import attribution_engine as engine
from data_store import append_unique
from reporting import select_report

class WorkflowTests(unittest.TestCase):
    def test_report_filters_orders_and_campaign_budgets_together(self):
        campaigns=[dict(campaign_id='a',channel='Social'),dict(campaign_id='b',channel='Market')]
        rows=[dict(campaign_id='a',channel='Social',status='Matched',order_date='2026-10-27'),
              dict(campaign_id='b',channel='Market',status='Matched',order_date='2026-10-28'),
              dict(campaign_id='',channel='Unknown',status='Unattributed',order_date='invalid')]
        selected,budgets=select_report(rows,campaigns,['Social'],['a'],['Matched'],(date(2026,10,27),date(2026,10,27)))
        self.assertEqual([r['campaign_id'] for r in selected],['a'])
        self.assertEqual([c['campaign_id'] for c in budgets],['a'])
        self.assertEqual(select_report(rows,campaigns,[],[],['Matched']),([],[]))
        selected,_=select_report(rows,campaigns,['Unknown'],['__unassigned__'],['Unattributed'])
        self.assertEqual(len(selected),1)

    def test_review_history_preserves_original_tracking_and_can_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp); orders=directory/'orders.csv'; campaigns=directory/'campaigns.csv'
            order=dict(order_id='order1',campaign_id='missing',promo_code='',order_total='12',order_date='2026-10-27')
            campaign=dict(campaign_id='a',promo_code='PROMO',campaign_name='Test',channel='Market')
            append_unique(orders,list(order),order,'order_id')
            append_unique(campaigns,list(campaign),campaign,'campaign_id')
            original=orders.read_bytes()
            with patch.multiple(engine,DATA_DIR=directory,ORDERS_FILE=orders,CAMPAIGNS_FILE=campaigns):
                self.assertEqual(engine.process_orders()[0][0]['status'],'Needs Review')
                engine.save_review('order1','Matched','a','Verified receipt')
                self.assertEqual(engine.process_orders()[0][0]['status'],'Matched')
                engine.save_review('order1','Unattributed',None,'No evidence')
                self.assertEqual(engine.process_orders()[0][0]['status'],'Unattributed')
                engine.save_review('order1','Automatic',None,'Restore original signals')
                self.assertEqual(engine.process_orders()[0][0]['status'],'Needs Review')
                with self.assertRaises(ValueError): engine.save_review('order1','Matched','bad','Evidence')
            self.assertEqual(original,orders.read_bytes())

    def test_retry_does_not_duplicate_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'orders.csv'; row=dict(order_id='stable-token',order_total='10')
            append_unique(path,list(row),row,'order_id')
            append_unique(path,list(row),row,'order_id')
            self.assertEqual(len(engine.load_csv(path)),1)
