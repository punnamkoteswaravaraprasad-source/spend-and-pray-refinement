import unittest
from product_metrics import product_units

class ProductMetricsTests(unittest.TestCase):
    def test_historical_names_and_malformed_items(self):
        counts,invalid=product_units([{'items':'Classic Red Hot Sauce x2; Mango Habanero x1'},
                                     {'items':'Classic Red x3; bad item; Ghost Pepper x0'}])
        self.assertEqual(counts,{'Classic Red':5,'Mango Habanero':1})
        self.assertEqual(invalid,2)
