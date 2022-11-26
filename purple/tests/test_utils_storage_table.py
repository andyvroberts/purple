import unittest
import logging
from utils import storage_table

class TestUtilsStorageTable(unittest.TestCase):
    #------------------------------------------------------------------------------
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

        # unique
        self.price_rec_1 = {'Postcode': 'BR3 4RL', 'Address': '309 - 311 BECKENHAM ROAD', 'Price': 525000, 'Date': '2019-05-29', \
            'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_rec_2 = {'Postcode': 'BR3 4SA', 'Address': '120A AVENUE ROAD', 'Price': 305000, 'Date': '2019-05-22', \
            'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_rec_3 = {'Postcode': 'BR3 1HT', 'Address': '6 BECK RIVER PARK', 'Price': 500000, 'Date': '2019-05-24', \
            'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        
        # duplicate price
        self.price_rec_4 = {'Postcode': 'BR3 4RL', 'Address': '309 - 311 BECKENHAM ROAD', 'Price': 525000, 'Date': '2019-05-29', \
            'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}

        self.price_entity_1 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1HE~1 EMBASSY GARDENS', 'Prices': "[{'2019-02-20': 274500}]", \
            'Address': '1 EMBASSY GARDENS', 'Postcode': 'BR3 1HE', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_entity_2 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1JW~4 VICARAGE DRIVE', 'Prices': "[{'2019-09-27': 582000}]", \
            'Address': '4 VICARAGE DRIVE', 'Postcode': 'BR3 1JW', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_entity_3 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 3FA~6 CHANCELLORS CLOSE', 'Prices': "[{'2019-05-24': 375000}]", \
            'Address': '6 CHANCELLORS CLOSE', 'Postcode': 'BR3 3FA', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        
        # duplicate entity rec
        self.price_entity_4 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1HE~1 EMBASSY GARDENS', 'Prices': "[{'2019-02-20': 274500}]", \
            'Address': '1 EMBASSY GARDENS', 'Postcode': 'BR3 1HE', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}

    #------------------------------------------------------------------------------
    def test_dedup_rowkey_and_merge_prices_can_group(self):
        bat = [self.price_entity_1, self.price_entity_2, self.price_entity_3, self.price_entity_4]

        result = storage_table.dedup_rowkey_and_merge_prices(bat)

        self.assertIs(list, type(result))

    #------------------------------------------------------------------------------
    def test_merge_2_single_prices_returns_correct_list(self):
        bat = [self.price_entity_1, self.price_entity_2]
        expected_price_string = "[{'2019-02-20': 274500}, {'2019-09-27': 582000}]"

        entity = storage_table.merge_prices(bat)
        result = entity['Prices']

        self.assertEqual(result, expected_price_string)

#------------------------------------------------------------------------------
if __name__ == 'main':
    # py -m unittest test_utils_storage_table.py
    unittest.main()