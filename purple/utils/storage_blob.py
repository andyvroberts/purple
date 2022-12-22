import logging
import os

from azure.storage.blob import BlobClient
from azure.core.exceptions import ResourceExistsError

# ---------------------------------------------------------------------------------------#


def get_client(container, blob_name):
    """ utility to get a reference to an azure blob storage.
        Args:
            container: the blob folder
            blob_name: the blob file name
            return: the blob client for later reads & writes
    """
    storage_conn_str = os.getenv('LandregDataStorage')
    clnt = BlobClient.from_connection_string(
        storage_conn_str, container, blob_name)

    return clnt

# ---------------------------------------------------------------------------------------#


def store_config(client, data):
    """ save a file to a blob container.

        Args:
            client: the blob storage client
            data: a data string to be saved
            return: None.
    """
    meta = client.upload_blob(data, overwrite=True)

# ---------------------------------------------------------------------------------------#


def read_config(client):
    """ read a blob file and return its contents.
        note: content_as_text has default encoding of utf-8.

        Args:
            client: the blob storage client
            return: the string of the blob contents
    """
    # blob_str = client.download_blob().readall().decode("utf-8")
    blob_str = client.download_blob().content_as_text()

    return blob_str
