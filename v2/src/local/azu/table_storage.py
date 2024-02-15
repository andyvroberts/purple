import logging
import os

from azure.data.tables import TableClient, TableTransactionError
from azure.core.exceptions import ResourceExistsError
# from azure.core.exceptions import HttpResponseError
# from azure.core.exceptions import ResourceNotFoundError

# ---------------------------------------------------------------------------------------#
log = logging.getLogger("purple.v2.src.local.azu.table_storage")
# suppress or show messages from Azure loggers.
logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger('azure.storage.queue').setLevel(logging.ERROR)

# ---------------------------------------------------------------------------------------#
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

# ---------------------------------------------------------------------------------------#
def upsert_replace_batch(client, batch):
    """ utility to upsert a batch.  Do not insert duplicate RowKey values.
        1. Limited to 100 table entity records
        2. Limited to 4MB total batch size
        Args:   
            client: the azure table client for the configuration table
            batch: a list of table record dicts
    """
    ops_bat = []

    for rec in batch:
        next_entry = ("upsert", rec,  {"mode": "replace"})
        ops_bat.append(next_entry)
    try:
        client.submit_transaction(operations=ops_bat)
        logging.info(f'STORAGE_TABLE. Batch inserted rows = {len(ops_bat)}')
    except TableTransactionError as txne:
        logging.error(txne.error)
        raise txne