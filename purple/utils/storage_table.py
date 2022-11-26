import logging
import os
import ast
from itertools import groupby

from azure.data.tables import TableClient, UpdateMode, TableTransactionError

from azure.core.exceptions import ResourceExistsError
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

#---------------------------------------------------------------------------------------# 
def get_table_client(name):
    """ utility to get a reference to an azure storage table.  
        try to create the table in case it does not already exist.
        Args:   
            name: a table name.
            return: the table client for later entity inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')
    table_client = TableClient.from_connection_string(storage_conn_str, name)

    try:
        table_client.create_table()
        logging.info(f'created table {name}')
    except ResourceExistsError:
        pass

    return table_client


#---------------------------------------------------------------------------------------# 
def upsert_replace(client, table_record):
    """ utility to upsert a table record
        Args:   
            client: the azure table client for the configuration table
            table_record: a table record dict, including partition/row keys
    """
    try:
        client.upsert_entity(mode=UpdateMode.REPLACE, entity=table_record)
    except HttpResponseError as he:
        logging.error(he)
        raise he


#---------------------------------------------------------------------------------------#
def merge_prices(entity_list):
    """
        The first record in the input list will be returned, with any additional prices
        appended in the 'Prices' field, as taken from the remaining records.

        Thewe are the merge conditions to cater for.
        1. an existing single price merge to a single price or multiple single prices
        2. an existing list of prices merge to a single price or multiple single prices
        3. an existing list of prices merge to a list of prices
        4. an existing list of prices merge to multiple lists of prices

        It is simplest just to gather the list of distinct prices using a set and 
        output them at the end.

        There is a risk here that we always do too much work, in those cases where there may
        not be any distinct prices, but records are true duplicates.  But lets avoid writting 
        too much code. This approach will at least, alwasy return the correct data.

        Args:   
            batch: the input list of table entity records (list)
            Return: a single table entity record with merged prices (dict)
    """
    merged_price_entity = entity_list[0]
    price_set = set()

    # loop through the enitty list and within each entity the price list
    for next_entity in entity_list:
        ep = next_entity['Prices']
        epl = ast.literal_eval(ep)

        for price_dict in epl:
            price_set.add(price_dict)

    # turn the set into a list and replace the 'Prices' field in the returned dict.
    merge_prices = list(price_set)
    merged_price_entity['Prices'] = str(merge_prices)

    return merged_price_entity


#---------------------------------------------------------------------------------------#
def dedup_rowkey_and_merge_prices(batch):
    """
        A batch can have duplicate rowkeys.  If so, merge all the prices into a single
        record and discard the rest.
        Args:   
            batch: the input list of table entity records
            Return: deduplicated list of table entity records
    """
    output_batch = []
    templist = []
    # can only groupby contiguous records so sort first.
    sorted_bat = sorted(batch, key=lambda x: x['RowKey'])
    
    for k, g in groupby(sorted_bat, key=lambda x: x['RowKey']):
        templist = list(g)
        if len(templist) > 1:
            logging.info(templist)
        else:
            output_batch.append(templist[0])

    logging.info(output_batch)

    return output_batch

#---------------------------------------------------------------------------------------# 
def upsert_replace_batch(client, batch):
    """ utility to upsert a batch.  Do not insert duplicate RowKey values.
        1. Limited to 100 table entity records
        2. Limited to 4MB total batch size
        Args:   
            client: the azure table client for the configuration table
            batch: a list of table record dicts
    """
    ops_bat = []
    rowkey_set = set()

    ops_bat = dedup_rowkey_and_merge_prices(batch)

    # for rec in batch:
    #     if rec['RowKey'] in rowkey_set:
    #         logging.warn(f"Duplicate rowkey detected: {rec['RowKey']} has price {rec['Prices']}")
    #     else:
    #         next_entry = ("upsert", rec,  {"mode": "replace"})
    #         ops_bat.append(next_entry)
    #         rowkey_set.add(rec['RowKey'])

    try:
        logging.info(f'38. Fake batch insert')
        #client.submit_transaction(operations=ops_bat)
    except TableTransactionError as txne:
        logging.error(txne)
        raise txne


#---------------------------------------------------------------------------------------# 
def have_outcode_rows_changed(client, partkey, rowkey, total_value, ready_status):
    """ read the configuration record for an outcode and if the total price is a different 
        value then return true, otherwise return false.
        Args: 
            client: the azure table client for the configuration table
            partition_key: the configuration level key
            row_key: the outcode entity key
            return: true | false
    """
    this_row = {}
    this_row['PartitionKey'] = partkey
    this_row['RowKey'] = rowkey
    this_row['Total'] = total_value
    this_row['Status'] = ready_status

    try:
        entity = client.get_entity(partition_key=partkey, row_key=rowkey)

        if entity['Total'] != this_row['Total']:
            client.insert_or_replace(this_row)
            return True
        else:
            return False

    except ResourceNotFoundError as nfe:
        # expected if no record in the table, create one and return true.
        client.create_entity(this_row)
        return True

    except HttpResponseError as re:
        # unexpected error
        logging.error(re.error)
        raise re


#---------------------------------------------------------------------------------------# 
def match_price(client, partkey, rowkey, new_price, price_record):
    """ read the price table for an existing record.
        if the record is found and the price exists return None.
        if the reocrd is found and the price does not exist return the modified table entity
        if the record is not found return a new table entity
        Args: 
            client: the azure table client for the configuration table
            partition_key: the outcode
            row_key: the address key
            new_price: the dict of the price we are searching for, eg {'2022-01-01': 456000}
            return: table entity | None
    """
    price_entity = {}

    try:
        price_entity = client.get_entity(partition_key=partkey, row_key=rowkey)
        # convert the prices string back into a list of dicts
        ep = price_entity['Prices']
        epl = ast.literal_eval(ep)

        if not next((item for item in epl if item == new_price), False):
            epl.append(new_price)
            price_entity['Prices'] = str(epl) # cannot store a list datatype in a table
            return price_entity
        else:
            # price alread exists in the table entity
            return None

    except ResourceNotFoundError as nfe:
        price_list = []
        price_list.append(new_price)
        price_entity['PartitionKey'] = partkey
        price_entity['RowKey'] = rowkey
        price_entity['Prices'] = str(price_list) # cannot store a list datatype in a table
        price_entity['Address'] = price_record['Address']
        price_entity['Postcode'] = price_record['Postcode']
        price_entity['Locality'] = price_record['Locality']
        price_entity['Town'] = price_record['Town']
        price_entity['District'] = price_record['District']
        price_entity['County'] = price_record['County']
        return price_entity

    except HttpResponseError as re:
        # unexpected error
        logging.error(re.error)
        raise re
#
# test_list = [{'2022-01-01':45000}, {'2022-03-10':37000}, {'2022-05-21': 670000}]
# new_price = {'2022-03-10':37000}
# false_price = {'2022-03-10':37600}
# next(item for item in test_list if item == new_price)
# next((item for item in test_list if item == new_price), False)
#

#-----------------------------------------------------------------------------------#
def table_batch(data, batch_size: int=100):
    """return a list of records of the required batch size until the input list is 
    exhausted.

        Args:
            data: the list of data records to batch
            batch_size: an integer that represents the required batch size
            Return: a generator that returns sets of the batch size
    """
    try:
        for i in range(0, len(data), batch_size):
            yield data[i:i+batch_size]

    except Exception as ex:
        logging.error(f'Failed to create a table batch: {ex}')
        raise ex
