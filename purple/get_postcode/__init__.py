import logging
import time

import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------#
def group_by_postcode(qc, outcode):
    record_count = 0
    queue_count = 0

    for stream_rec in http_reader.stream_file(common.landreg_monthly_update_url()):
        record_count += 1
        rec = landreg_decoder.prune_rec_for_queue(stream_rec)

        # if the outcode exists and is the one we are searching for.
        if len(rec['Postcode']) > 0:
            outcode = rec['Postcode'].split(' ')[0].lower()
            
            if outcode == scan_outcode:
                qc.send_message(rec)
                queue_count += 1

    logging.info(f'Input records = {record_count}')
    return queue_count

#---------------------------------------------------------------------------------------#
def main(load_postcodes: func.QueueMessage) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    outcode = load_postcodes.get_body().decode('utf-8').lower()
    id = load_postcodes.id
    pop = load_postcodes.pop_receipt
    
    logging.info(f'Processing Outcode: {outcode}')
    logging.info(f'Next visible at: {load_postcodes.time_next_visible.isoformat()}')

    # setup the postcode blob details

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
