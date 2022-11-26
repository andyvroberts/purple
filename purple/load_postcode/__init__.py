import logging
import time
import ast

import azure.functions as func

from utils import storage_table
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------#
def lookup_price_and_prep_record(price_table, price_record):
    # read the price record from table storage.
    partition_key = price_record['Postcode'].split(' ')[0]
    row_key = f"{price_record['Postcode']}~{price_record['Address']}"

    price_dict = {}
    price_dict[price_record['Date']] = price_record['Price']

    # do the storage table related work
    return storage_table.match_price(price_table, partition_key, row_key, price_dict, price_record)


#---------------------------------------------------------------------------------------#
def store_prices(outcode):
    # set up the queue client
    queue_name = common.format_landreg_queue_name(outcode)
    prices_queue = storage_queue.get_queue_client(queue_name)
    price_table = storage_table.get_table_client(common.price_table_name())

    # get multiple messages at one time (max 32), process them in a batch and then delete.
    msgs = prices_queue.receive_messages(messages_per_page=32, visibility_timeout=60)
    logging.info(f'21. reading message queue')

    # set up batch collection
    operation_batch = []
    batch_count = 0
    total_count = 0

    for msg_bat in msgs.by_page():
        for msg in msg_bat:
            rec_dict = ast.literal_eval(msg.content) # queue content is string so cast to dict
            price_rec = lookup_price_and_prep_record(price_table, rec_dict)

            if price_rec is not None:
                logging.info(f'23. {price_rec}')
                operation_batch.append(price_rec)
                batch_count += 1

                if batch_count == 100:
                    storage_table.upsert_replace_batch(price_table, operation_batch)
                    operation_batch = []
                    total_count += batch_count
                    batch_count = 0
                    logging.info(f'13. Inserted Batch.')

            storage_queue.delete_message(prices_queue, msg.id, msg.pop_receipt) 

    # insert final batch that did not reach the batch limit of 100
    if len(operation_batch) > 0:
        #storage_table.upsert_replace_batch(price_table, operation_batch)
        total_count += batch_count
        logging.info(f'15. total inserts = {total_count}')

    return total_count


#---------------------------------------------------------------------------------------#
def main(pcodes: func.QueueMessage) -> None:
    start_exec = time.time()
    stored = 0

    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    outcode = pcodes.get_body().decode('utf-8').lower()
    id = pcodes.id
    pop = pcodes.pop_receipt
    logging.info(f'01. triggered outcode = {outcode}')

    # read the price records and process them
    stored = store_prices(outcode)
    logging.info(f'99. Table records created or modified = {stored}')

    # delete the message from the load-postcodes queue as this workload has completed.
    trigger_queue = storage_queue.get_queue_client(common.load_postcode_trigger_queue_name())
    storage_queue.delete_message(trigger_queue, id, pop)

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
