import logging
import os

from azure.data.tables import TableServiceClient as TSC

from azure.core.exceptions import ResourceExistsError

#---------------------------------------------------------------------------------------# 
def create(name):
    """ utility to create an azure storage table.  If the table already exists then
        nothing will happen and the error will be ignored.
        Args:   
            name: a table name.
            return: the table client for later entity inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')

    logging.info(f'creating table {name}')
    table_client = TSC.from_connection_string(storage_conn_str)

    try:
        table_client.create_table(name)
    except ResourceExistsError:
        pass

    return table_client

