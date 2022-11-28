import logging
import time

import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------#
def read_and_decode(qc, scan_outcode) -> int:
    record_count = 0
    queue_count = 0

    for stream_rec in http_reader.stream_file():
        record_count += 1
        rec = landreg_decoder.format_for_msg(stream_rec)

        # if the outcode exists and is the one we are searching for.
        if rec is not None:
            outcode = rec['Postcode'].split(' ')[0].lower()
            if outcode == scan_outcode:
                qc.send_message(rec)
                queue_count += 1

    logging.info(f'GET_OUTCODE. Input records = {record_count}')
    return queue_count

#---------------------------------------------------------------------------------------#
def main(msg: func.QueueMessage) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    outcode = msg.get_body().decode('utf-8')
    id = msg.id
    pop = msg.pop_receipt
    logging.info(f'GET_OUTCODE. Processing Outcode: {outcode}')

    # setup the outcode specific output queue
    scan_outcode = outcode.lower()
    queue_name = common.format_landreg_queue_name(scan_outcode)
    logging.info(f'GET_OUTCODE. Queue Name = {queue_name}')
    outcode_queue = storage_queue.get_queue_client(queue_name)

    # read the data and find all outcode records
    created_msg_count = read_and_decode(outcode_queue, scan_outcode)
    logging.info(f'GET_OUTCODE. Queue Messages sent = {created_msg_count}')

    # create a message on the load-postcode queue.
    postcode_queue = storage_queue.get_queue_client(common.load_postcode_trigger_queue_name())
    storage_queue.send_message(postcode_queue, outcode)

    # delete the message from the load-outcodes queue as this workload has completed.
    trigger_queue = storage_queue.get_queue_client(common.load_outcode_trigger_queue_name())
    storage_queue.delete_message(trigger_queue, id, pop)

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'GET_OUTCODE. Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
