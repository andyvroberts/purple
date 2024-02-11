import logging
import os

from azure.storage.queue import QueueClient, TextBase64EncodePolicy, TextBase64DecodePolicy
from azure.core.exceptions import ResourceExistsError

#---------------------------------------------------------------------------------------# 
def get_client(name):
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
def send_message(client, payload, vistime: int=0):
    """ send a message to a queue.
        as we use base64 encoding, all payloads must be strings to avoid TypeError
        Args:   
            client: the storage queue client
            payload: a list of the payload data
            vistime: the visibility timeout in seconds
            return: None
    """
    string_payload = str(payload)
    client.send_message(string_payload, visibility_timeout=vistime)


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