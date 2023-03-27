import unittest
import logging
from utils import http_reader


class TestUtilsLandregDecoder(unittest.TestCase):
    # ------------------------------------------------------------------------------
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

        self.csv_rec1 = '"{EC7AD099-C017-9200-E053-6C04A8C0E306}","139950","2002-07-08 00:00","TN34 2EB","S","N","F","68","","ELPHINSTONE ROAD","","HASTINGS","HASTINGS","EAST SUSSEX","A","A"'
        self.csv_rec2 = '"{0ED18E4B-9FBB-49E1-AB3C-E28D120672F6}","249900","2007-01-11 00:00","PL20 7QQ","D","N","F","HILLSIDE VIEW","","JORDAN LANE","HORRABRIDGE","YELVERTON","WEST DEVON","DEVON","A","C"'
        self.csv_rec3 = '"{E53EDD2D-7034-83EC-E053-6B04A8C03A59}","230000","2007-02-02 00:00","TR17 0AW","T","N","F","45a","ROSEVEAN","FORE STREET","","MARAZION","CORNWALL","CORNWALL","A","D"'

        self.msg_rec1 = {'Postcode': 'TN34 2EB', 'Address': '68 ELPHINSTONE ROAD', 'Price': 139950,
                         'Date': '2002-07-08', 'Locality': '', 'Town': 'HASTINGS', 'District': 'HASTINGS', 'County': 'EAST SUSSEX', 'RecStatus': 'A'}
        self.addr_rec3 = "45a ROSEVEAN FORE STREET"

    # ------------------------------------------------------------------------------
    def test_format_price_rec_returns_correct_dict(self):
        result = http_reader.format_price_rec(self.csv_rec1)

        self.assertDictEqual(self.msg_rec1, result)

    # ------------------------------------------------------------------------------
    def test_format_address_returns_correct_dict(self):
        result = http_reader.format_address('45a', 'ROSEVEAN', 'FORE STREET')

        self.assertEqual(self.addr_rec3, result)

    # ------------------------------------------------------------------------------
    def test_format_price_config_returns_correct_dict(self):
        outcode, price = http_reader.format_price_config(self.csv_rec2)

        # we should get a lower case outcode as these are used to create message queues.
        expected_outcode = 'pl20'
        expected_price = 249900

        self.assertEqual(outcode, expected_outcode)
        self.assertEqual(price, expected_price)


# ------------------------------------------------------------------------------
if __name__ == 'main':
    # py -m unittest test_utils_http_reader.py
    unittest.main()
