import logging
import os
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
        logging.info(f'STORAGE_TABLE. created table {name}')
    except ResourceExistsError:
        pass

    return table_client


#---------------------------------------------------------------------------------------#
def format_rowkey(row_key):
    """ remove characters that cannot be included in a RowKey value
    """
    return row_key.replace('\\',' ').replace('/',' ').replace('#','').replace('?','')


#---------------------------------------------------------------------------------------#
def string_to_list(prices_string):
    """ convert the retrieved table entity prices string into a python list type
    """
    prices_array = prices_string.split(',')

    return list(prices_array)


#---------------------------------------------------------------------------------------#
def list_to_string(prices_list):
    """ convert a list of prices into a string as a column in table storage
    """
    prices_string = ','.join(item for item in prices_list)

    return prices_string


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
        logging.error(he.error)
        raise he


#---------------------------------------------------------------------------------------# 
def create_entity_from_price_record(price_rec):
    """ convert an input price price record into the format required for table storage.
        Args:   
            price_rec: the input source format
            return: table storage entity record for the price
    """
    new_entity = {}
    # force keys to be upper case.
    new_entity['PartitionKey'] = price_rec['Postcode'].split(' ')[0].upper()
    # Rowkey must be checked for invalid chars
    row_key = f"{price_rec['Postcode']}~{price_rec['Address']}".upper()
    new_entity['RowKey'] = format_rowkey(row_key)
    # Prices must be a list type.
    new_entity['Prices'] = [(f"{price_rec['Date']}~{price_rec['Price']}~{price_rec['RecStatus']}")]
    new_entity['Address'] = price_rec['Address']
    new_entity['Postcode'] = price_rec['Postcode']
    new_entity['Locality'] = price_rec['Locality']
    new_entity['Town'] = price_rec['Town']
    new_entity['District'] = price_rec['District']
    new_entity['County'] = price_rec['County']

    return new_entity


#---------------------------------------------------------------------------------------#
def price_exists(check_entity, new_price):
    """
        does the table entity already contain the new price.

        Args:   
            check_entity: an existing table entity being checked (dict)
            new_price: a single date~price string in a list ['2022-04-07~345000']
            Return: True or False
    """
    epl = check_entity['Prices']

    if new_price[0] in epl:
        return True
    else:
        return False


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

    # loop through the enitty list and within each entity the prices list
    for next_entity in entity_list:
    
        for price in next_entity['Prices']:
            price_set.add(price)

    # turn the set into a list and replace the 'Prices' field in the returned dict.
    merge_prices = list(price_set)
    sorted_prices = sorted(merge_prices)
    merged_price_entity['Prices'] = sorted_prices

    return merged_price_entity


#---------------------------------------------------------------------------------------#
def dedup_rowkey_and_merge_prices(batch):
    """
        A batch can have duplicate rowkeys.  If so, merge all the prices into a single
        record and discard the remaining duplicates.
        Args:   
            batch: the input list of table entity records
            Return: deduplicated list of table entity records
    """
    output_batch = []
    templist = []
    # can only groupby contiguous records so sort first.
    sorted_bat = sorted(batch, key=lambda x: x['RowKey'])
    
    # do the groupby and if we get a group with more than 1 record, send it off for 
    # the price merging process.
    for k, g in groupby(sorted_bat, key=lambda x: x['RowKey']):
        templist = list(g)
        if len(templist) > 1:
            merged = merge_prices(templist)
            output_batch.append(merged)
        else:
            output_batch.append(templist[0])
    
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
    dedup_bat = []

    dedup_bat = dedup_rowkey_and_merge_prices(batch)

    for rec in dedup_bat:
        # cannot store an embedded list in table storage, convert to string.
        rec['Prices'] = list_to_string(rec['Prices'])

        next_entry = ("upsert", rec,  {"mode": "replace"})
        ops_bat.append(next_entry)

    try:
        client.submit_transaction(operations=ops_bat)
        logging.info(f'STORAGE_TABLE. Batch inserted rows = {len(ops_bat)}')
    except TableTransactionError as txne:
        logging.error(txne.error)
        raise txne


#---------------------------------------------------------------------------------------# 
def lookup_price_entity(client, new_entity):
    """ read the price table for an existing record.
        if the record is found and the new price already exists return None.
        if the reocrd is found and the price does not exist return a record with merged prices
        if the record is not found return the new entity passed in

        Args: 
            client: the azure table client for the configuration table
            new_entity: the price record being checked for table insertion (dict)
            return: table entity | None
    """
    partkey = new_entity['PartitionKey']
    rowkey = new_entity['RowKey']

    try:
        price_entity = client.get_entity(partition_key=partkey, row_key=rowkey)
        # convert Prices string to a list for data manipulation.
        price_entity['Prices'] = string_to_list(price_entity['Prices'])

        if price_exists(price_entity, new_entity['Prices']):
            return None
        else:
            # price does not exist
            to_be_merged = [price_entity, new_entity]
            return merge_prices(to_be_merged)

    except ResourceNotFoundError as nfe:
        return new_entity

    except HttpResponseError as re:
        logging.error(re.error)
        raise re


#---------------------------------------------------------------------------------------# 
def have_outcode_rows_changed(client, partkey, rowkey, total_value):
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
        logging.error(f'Failed to create a table batch: {ex.error}')
        raise ex
