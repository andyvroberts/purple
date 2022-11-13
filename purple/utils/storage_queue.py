import logging
import os

from azure.storage.queue import BinaryBase64EncodePolicy
from azure.storage.queue.aio import QueueClient as QCAIO
from azure.storage.queue import QueueClient as QC

from azure.core.exceptions import ResourceExistsError

#---------------------------------------------------------------------------------------# 
def create(name):
    """ utility to create an azure storage queue.  If the queue already exists then
        nothing will happen and the error will be ignored.
        Args:   
            name: a queue name.
            return: the queue client for later message inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')

    logging.info(f'creating queue {name}')
    queue_client = QC.from_connection_string(storage_conn_str, name)

    try:
        queue_client.create_queue()
    except ResourceExistsError:
        pass

    return queue_client

#---------------------------------------------------------------------------------------# 
def send_message(client, payload):
    """ send a message to a queue.
        Args:   
            client: the storage queue client
            payload: a list of the payload data
            return: None
    """
    client.send_message(payload)
