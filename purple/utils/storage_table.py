import logging
import os
import ast

from azure.data.tables import TableClient
from azure.data.tables import UpdateMode

from azure.core.exceptions import ResourceExistsError
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

#---------------------------------------------------------------------------------------# 
def create(name):
    """ utility to create an azure storage table.  If the table already exists then
        nothing will happen and the error will be ignored.
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
            return: the count of records processed
    """
    try:
        return_meta = client.upsert_entity(mode=UpdateMode.REPLACE, entity=table_record)
    except HttpResponseError as he:
        logging.error(he)
        raise he


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
        logging.info(f'ENTITY] {entity}')

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
    logging.info(price_record)

    try:
        price_entity = client.get_entity(partition_key=partkey, row_key=rowkey)
        # convert the prices string back into a list of dicts
        ep = price_entity['Prices']
        epl = ast.literal_eval(ep)

        if not next((item for item in epl if item == new_price), False):
            epl.append(new_price)
            price_entity['Prices'] = str(epl) # cannot store a list datatype in a talbe
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
