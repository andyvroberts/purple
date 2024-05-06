import logging
import os

from azure.storage.queue import QueueClient, TextBase64EncodePolicy, TextBase64DecodePolicy
from azure.core.exceptions import ResourceExistsError

# ---------------------------------------------------------------------------------------#
log = logging.getLogger("purple.v2.src.local.azu.queue_storage")
# suppress or show messages from Azure loggers.
logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
logging.getLogger('azure.storage.queue').setLevel(logging.ERROR)


#---------------------------------------------------------------------------------------# 
def get_base64_queue_client(name):
    """ utility to get a reference to an azure storage queue client which reads and
        writes text converted to base64 (binary) data.
        try to create the queue in case it does not already exist.
        Args:   
            name: a queue name.
            return: the queue client for later message inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')
    queue_client = QueueClient.from_connection_string(
        conn_str=storage_conn_str, 
        queue_name= name,
        message_encode_policy=TextBase64EncodePolicy(),
        message_decode_policy=TextBase64DecodePolicy()
    )

    try:
        queue_client.create_queue()
    except ResourceExistsError:
        pass

    return queue_client

#---------------------------------------------------------------------------------------# 
def send_price_message(client, payload, vistime: int=0):
    """ send a message to a queue.
        as we use base64 encoding, all payloads must be strings to avoid TypeError
        Args:   
            client: the storage queue client
            postcode: the postcode group
            prices: the price records in the postcode
            vistime: the visibility timeout in seconds
            return: None
    """
    string_payload = str(payload)
    try:
        msg_object = client.send_message(string_payload, visibility_timeout=vistime)
    
        content_size = len(msg_object.content)
        if round(content_size/1024,2) > 40:
            log.warn(f"Message size GT 40k {round(content_size/1024,2)}")
        elif round(content_size/1024,2) > 48:
            log.error(f"Message size GT 48k {round(content_size/1024,2)}. Max Q payload size exceeded.")
    
    except Exception as qe:
        log.error(qe)
        raise qe

#---------------------------------------------------------------------------------------# 
def delete_message(client, id, pop_receipt):
    """ send a message to a queue.
        Args:   
            client: the storage queue client
            id: the identifier from a retrieved message
            pop_receipt: the pop receipt from a retrieved message
            return: None
    """
    client.delete_message(id, pop_receipt)