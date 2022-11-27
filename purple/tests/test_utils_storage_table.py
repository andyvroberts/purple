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
        self.converted_1 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 4RL~309 - 311 BECKENHAM ROAD', 'Prices': ['2019-05-29~525000'], \
            'Address': '309 - 311 BECKENHAM ROAD', 'Postcode': 'BR3 4RL', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', \
            'County': 'GREATER LONDON'}

        self.price_entity_1 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1HE~1 EMBASSY GARDENS', 'Prices': ['2019-02-20~274500'], \
            'Address': '1 EMBASSY GARDENS', 'Postcode': 'BR3 1HE', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_entity_2 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1JW~4 VICARAGE DRIVE', 'Prices': ['2019-09-27~582000'], \
            'Address': '4 VICARAGE DRIVE', 'Postcode': 'BR3 1JW', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_entity_3 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 3FA~6 CHANCELLORS CLOSE', 'Prices': ['2019-05-24~375000', '2016-01-24~365000'], \
            'Address': '6 CHANCELLORS CLOSE', 'Postcode': 'BR3 3FA', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        
        # duplicate entity rec
        self.price_entity_4 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1HE~1 EMBASSY GARDENS', 'Prices': ['2019-02-20~274500'], \
            'Address': '1 EMBASSY GARDENS', 'Postcode': 'BR3 1HE', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}
        self.price_entity_5 = {'PartitionKey': 'BR3', 'RowKey': 'BR3 1HE~1 EMBASSY GARDENS', 'Prices': ['2011-01-01~274500'], \
            'Address': '1 EMBASSY GARDENS', 'Postcode': 'BR3 1HE', 'Locality': '', 'Town': 'BECKENHAM', 'District': 'BROMLEY', 'County': 'GREATER LONDON'}

    #------------------------------------------------------------------------------
    def test_convert_landreg_price_to_table_entity(self):
        result = storage_table.create_entity_from_price_record(self.price_rec_1)

        self.assertDictEqual(self.converted_1, result)

    #-----------------------------------------------------------------------------------#
    def test_format_rowkey_removes_invalid_chars(self):
        row_key1 = u"NW4 1TS~1\MILLS GROVE?"
        row_key2 = u"NW4 1TS~1 MILLS/GROVE#"

        correct_key = "NW4 1TS~1 MILLS GROVE"

        res_1 = storage_table.format_rowkey(row_key1)
        res_2 = storage_table.format_rowkey(row_key2)

        self.assertEqual(res_1, correct_key)
        self.assertEqual(res_2, correct_key)

    #------------------------------------------------------------------------------
    def test_convert_string_to_list(self):
        prices_string = "2019-02-20~274500, 2019-02-20~274500"
        result = storage_table.string_to_list(prices_string)

        self.assertIsInstance(result, list)
        
    #------------------------------------------------------------------------------
    def test_convert_string_to_list(self):
        prices_list = ['2019-02-20~274500', ' 2019-02-20~274500']
        result = storage_table.list_to_string(prices_list)

        self.assertIsInstance(result, str)

    #------------------------------------------------------------------------------
    def test_dedup_rowkey_and_merge_prices_can_group(self):
        bat = [self.price_entity_1, self.price_entity_2, self.price_entity_3, self.price_entity_4]

        result = storage_table.dedup_rowkey_and_merge_prices(bat)
        # the 4 input records should be reduced down to 3 as entity_4 is a duplicate
        expected_count = 3

        self.assertIsInstance(result, list)
        self.assertEqual(expected_count, len(result))

    #------------------------------------------------------------------------------
    def test_merge_2_single_prices_returns_correct_list(self):
        bat = [self.price_entity_1, self.price_entity_2]
        expected_price_list = ['2019-02-20~274500', '2019-09-27~582000']

        entity = storage_table.merge_prices(bat)
        result = list(entity['Prices'])

        # the ^ operator is used to test symmetric difference.
        difference = set(expected_price_list) ^ set(result)
        # diff should be empty if lists being compared contain same elements
        self.assertTrue(len(difference) == 0)

    #------------------------------------------------------------------------------
    def test_merge_multiple_prices_returns_correct_list(self):
        bat = [self.price_entity_1, self.price_entity_2, self.price_entity_3]
        # all 4 prices should be returned.
        expected_price_list = ['2019-02-20~274500', '2016-01-24~365000', '2019-09-27~582000', '2019-05-24~375000']

        entity = storage_table.merge_prices(bat)
        result = list(entity['Prices'])

        difference = set(expected_price_list) ^ set(result)
        # diff should be empty if lists contain same elements
        self.assertTrue(len(difference) == 0)

    #------------------------------------------------------------------------------
    def test_merge_multiple_prices_returns_sorted_list(self):
        bat = [self.price_entity_1, self.price_entity_2, self.price_entity_3]
        # all 4 prices should be returned in sorted order
        expected_price_list = ['2016-01-24~365000', '2019-02-20~274500', '2019-05-24~375000', '2019-09-27~582000' ]

        entity = storage_table.merge_prices(bat)
        result = list(entity['Prices'])

        self.assertListEqual(expected_price_list, result)

    #------------------------------------------------------------------------------
    def test_merge_3_prices_in_same_entity_returns_correct_prices(self):
        bat = [self.price_entity_1, self.price_entity_4, self.price_entity_5]
        # the final 
        expected_price_list = ['2019-02-20~274500', '2011-01-01~274500']
        
        result_list = storage_table.dedup_rowkey_and_merge_prices(bat)
        # the 3 input records should be reduced down to 1 as all are duplicates
        expected_entity_count = 1
        self.assertEqual(expected_entity_count, len(result_list))

        result = result_list[0]
        result_price_list = list(result['Prices'])

        difference = set(expected_price_list) ^ set(result_price_list)
        # diff should be empty as lists contain same prices
        self.assertTrue(len(difference) == 0)

    #------------------------------------------------------------------------------
    def test_when_price_exists_returns_true(self):
        matching_price = ['2019-02-20~274500']
        
        result = storage_table.price_exists(self.price_entity_1, matching_price)
        expected_true = True

        self.assertEqual(expected_true, result)

    #------------------------------------------------------------------------------
    def test_when_price_does_not_exist_returns_false(self):
        non_matching_price = ['2011-02-20~270000']
        
        result = storage_table.price_exists(self.price_entity_1, non_matching_price)
        expected_false = False

        self.assertEqual(expected_false, result)


#------------------------------------------------------------------------------
if __name__ == 'main':
    # py -m unittest test_utils_storage_table.py
    unittest.main()