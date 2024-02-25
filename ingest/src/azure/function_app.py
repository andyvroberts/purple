import azure.functions as func
import azure.data.tables as tab
from azure.core.exceptions import ResourceExistsError, HttpResponseError
import ast
import os
import logging

#------------------------------------------------------------------------------
app = func.FunctionApp()

#------------------------------------------------------------------------------
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
            return: None
    """
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
        logging.info(f'PRICES_CREATE: created table postcode.')
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
        logging.error(uE.message)
        raise uE  
    
    logging.info(f"PRICES_CREATE: Inserted Postcode {postcode}")
