import logging
import time
import ast

import azure.functions as func

from utils import http_reader
from utils import storage_table
from utils import common

# ---------------------------------------------------------------------------------------#


def lookup_price_and_prep_record(price_table, price_record):
    # set the partition and rowkeys for searching the table entities.
    new_entity = storage_table.create_entity_from_price_record(price_record)

    # do the storage table related work
    return storage_table.lookup_price_entity(price_table, new_entity)

# ---------------------------------------------------------------------------------------#


def store_prices(outcode):
    # set up the queue client
    price_table = storage_table.get_table_client(common.price_table_name())

    # set up price table batch collection
    operation_batch = []
    batch_count = 0
    total_count = 0
    record_count = 0

    for stream_rec in http_reader.stream_file_for_outcode(outcode):
        record_count += 1
        price_rec = lookup_price_and_prep_record(price_table, stream_rec)

        if price_rec is not None:
            operation_batch.append(price_rec)
            batch_count += 1

            if batch_count == 100:
                storage_table.upsert_replace_batch(
                    price_table, operation_batch)
                operation_batch = []
                total_count += batch_count
                batch_count = 0

    # insert final batch that did not reach the batch limit of 100
    if len(operation_batch) > 0:
        storage_table.upsert_replace_batch(price_table, operation_batch)
        total_count += batch_count

    logging.info(
        f'PRICE_LOADER for {outcode}. Price File records used = {record_count}'
    )
    return total_count

# ---------------------------------------------------------------------------------------#


def main(msg: func.QueueMessage) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger('azure.storage.queue').setLevel(logging.ERROR)

    outcode = msg.get_body().decode('utf-8').lower()
    id = msg.id
    pop = msg.pop_receipt
    logging.info(f'PRICE_LOADER. Processing Outcode: {outcode}')

    # read the price records and process them
    stored = store_prices(outcode)
    logging.info(
        f'PRICE_LOADER for {outcode}. Table records created or modified = {stored}'
    )

    # delete the message from the load-outcodes queue as this workload has completed.
    # the SDK automatically deletes triggering messages which complete without error.

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(
        f'PRICE_LOADER for {outcode}. Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs'
    )
