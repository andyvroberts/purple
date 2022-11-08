import logging
import os

from azure.storage.queue import BinaryBase64EncodePolicy
from azure.storage.queue.aio import QueueClient as QCAIO
from azure.storage.queue import QueueClient as QC

from azure.core.exceptions import ResourceExistsError

#---------------------------------------------------------------------------------------# 
def create(name) -> None:
    """ utility to create an azure storage queue.  If the queue already exists then
        nothing will happen and the error will be ignored.
        Args:   
            name: a string queue name.
    """
    storage_conn_str = os.getenv('LandregDataStorage')

    logging.info(f'creating queue {name}')
    queue_client = QC.from_connection_string(storage_conn_str, name)

    try:
        queue_client.create_queue()
    except ResourceExistsError:
        pass


#---------------------------------------------------------------------------------------# 
def send(name, message) -> None:
    """ utility to send a message to the queue.
        Args:   
            name: a string queue name.
            messaage: the payload for the queue.
    """
    storage_conn_str = os.getenv('LandregDataStorage')

    logging.info(f'sending message to {name}')
    queue_client = QC.from_connection_string(storage_conn_str, name)

    queue_client.send_message(message)