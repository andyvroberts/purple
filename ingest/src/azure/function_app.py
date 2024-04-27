import azure.functions as func
import azure.data.tables as tab
from azure.core.exceptions import ResourceExistsError, HttpResponseError
from azure.monitor.opentelemetry import configure_azure_monitor
from logging import INFO, getLogger
import ast
import os

#------------------------------------------------------------------------------
app = func.FunctionApp()

#------------------------------------------------------------------------------
"""
    Define the Storage Queue details of this trigger function
    
"""
@app.queue_trigger(
    arg_name="azqueue", 
    queue_name="prices",
    connection="LandregDataStorage"
) 

#------------------------------------------------------------------------------
def prices_create(azqueue: func.QueueMessage):
    """
        Accept the prices message, decode it and store them in 
        an azure table.

        Args:
            azqueue: the incoming Azure Queue Message
            return: None
    """
    # setup logging using open telemetry library.
    configure_azure_monitor(logger_name = "prices_create")
    log = getLogger("prices_create")
    log.setLevel(INFO)

    # accept the message.
    msg_str = azqueue.get_body().decode('utf-8')

    # convert the string body into 2 fields. 
    # Field 1 = Postcode
    # Field 2 = List of Prices
    msg = ast.literal_eval(msg_str)
    postcode = msg[0]
    outcode = postcode.split(' ')[0]
    addresses = msg[1]

    # create a table client
    conn = os.environ['LandregDataStorage']
    cl = tab.TableClient.from_connection_string(conn, 'postcode')
    try:
        cl.create_table()
        log.info(f'PRICES_CREATE: created table postcode.')
    except ResourceExistsError:
        pass
    
    # insert the record
    entity = {}
    entity['PartitionKey'] = outcode
    entity['RowKey'] = postcode
    entity['PropertyPrices'] = str(addresses)
    try:
        cl.upsert_entity(entity)
    except HttpResponseError as uE:
        log.error(uE.message)
        raise uE  
    
    log.info(f"PRICES_CREATE: Inserted Postcode {postcode}")
