import logging
import os

from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from azure.core.exceptions import ResourceExistsError

#---------------------------------------------------------------------------------------# 
def get_queue_client(name):
    """ utility to get a reference to an azure storage queue.
        try to create the queue in case it does not already exist.
        Args:   
            name: a queue name.
            return: the queue client for later message inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')
    queue_client = QueueClient.from_connection_string(storage_conn_str, name)

    try:
        queue_client.create_queue()
    except ResourceExistsError:
        pass

    return queue_client


#---------------------------------------------------------------------------------------# 
def get_base64_queue_client(name):
    """ utility to get a reference to an azure storage queue.
        try to create the queue in case it does not already exist.
        Args:   
            name: a queue name.
            return: the queue client for later message inserts
    """
    storage_conn_str = os.getenv('LandregDataStorage')
    queue_client = QueueClient.from_connection_string(
        conn_str=storage_conn_str, 
        queue_name= name,
        message_encode_policy=TextBase64EncodePolicy()
    )

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