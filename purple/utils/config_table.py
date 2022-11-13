import logging
import os

from azure.data.tables import TableClient

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
