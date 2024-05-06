import logging
import sys
from os import environ

from azure.data.tables import TableClient, TableTransactionError
from azure.core.exceptions import ResourceExistsError
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

# ---------------------------------------------------------------------------------------#
log = logging.getLogger("purple.v2.src.local.azu.table_storage")
# suppress or show messages from Azure loggers.
logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


# ---------------------------------------------------------------------------------------#
def get_table_client(name):
    """ utility to get a reference to an azure storage table.  
        try to create the table in case it does not already exist.
        Args:   
            name: a table name.
            return: the table client for later row manipulation
    """
    try:
        environ["LandregDataStorage"]
    except KeyError:
        log.error(f"Environment variable LandregDataStorage does not exist.")
        sys.exit(1)

    storage_conn_str = environ.get('LandregDataStorage')
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
            return: the number of rows inserted in the batch
    """
    ops_bat = []

    for rec in batch:
        next_entry = ("upsert", rec,  {"mode": "replace"})
        ops_bat.append(next_entry)

    try:
        client.submit_transaction(operations=ops_bat)
        return len(ops_bat)
    
    except TableTransactionError as txne:
        logging.error(f"Table Transaction Error: {txne.error}")
        raise txne
    except ResourceNotFoundError as rxne:
        logging.error(f"Resource Not Found: {rxne.error}")
        raise rxne
    

# ---------------------------------------------------------------------------------------#
def query_ready_outcodes(client):
    """ utility to query the outcode mapping table

        Args:   
            client: the azure table client for the configuration table
            return: a generator of outcode to postcode mapping table records
    """
    parms = {
        "pk": "OUTCODE",
        "ready": "R"
    }
    query = "PartitionKey eq @pk and Status eq @ready"

    try:
        oc_list = client.query_entities(query_filter=query, parameters=parms)

        for oc_entity in oc_list:
            yield oc_entity

    except ResourceNotFoundError as rxne:
        logging.error(f"Resource Not Found: {rxne.error}")
        raise rxne
    except HttpResponseError as qe:
        logging.error(f"HTTP Error: {qe.error}")
        raise qe


#---------------------------------------------------------------------------------------# 
def update(client, table_record):
    """ utility to update an existing table record
        Args:   
            client: the azure table client for the storage table
            table_record: a table record dict, including partition/row keys
    """
    try:
        client.update_entity(table_record)
    except HttpResponseError as he:
        logging.error(he)
        raise he

