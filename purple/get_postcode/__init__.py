import logging
import time
import ast

import azure.functions as func

from utils import storage_table
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------#
def lookup_price_and_create_or_update(price_record):
    # read the price record from table storage.
    partition_key = price_record['Postcode']
    row_key = price_record['Address']

    price_dict = {}
    price_dict[price_record['Date']] = price_record['Price']
    price_table = storage_table.create(common.price_table_name())

    # do the storage table related work
    table_record = storage_table.match_price(price_table, partition_key, row_key, price_dict, price_record)

    if table_record is not None:
        storage_table.upsert_replace(price_table, table_record)
        return 1
    else:
        return 0


#---------------------------------------------------------------------------------------#
def read_prices_and_store(outcode):
    entity_stored_count = 0
    insert_or_update = {}

    # set up the queue client
    queue_name = common.format_landreg_queue_name(outcode)
    prices_queue = storage_queue.create(queue_name)
    logging.info(f'reading outcode queue: {queue_name}')

    # get multiple messages at one time (max 32), process them in a batch and then delete.
    msgs = prices_queue.receive_messages(messages_per_page=32, visibility_timeout=60)

    for msg_bat in msgs.by_page():
        for msg in msg_bat:
            rec_dict = ast.literal_eval(msg.content) # queue content is string so cast to dict
            entity_stored_count += lookup_price_and_create_or_update(rec_dict)
            prices_queue.delete_message(msg.id, msg.pop_receipt) 

    return entity_stored_count

#---------------------------------------------------------------------------------------#
def main(pcodes: func.QueueMessage) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    outcode = pcodes.get_body().decode('utf-8').lower()
    id = pcodes.id
    pop = pcodes.pop_receipt

    # read the price records and process them
    stored = read_prices_and_store(outcode)
    logging.info(f'Table records created or modified = {stored}')

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
