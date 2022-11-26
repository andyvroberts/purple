import time
import logging
import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------# 
def read_and_decode(url, outcode):
    record_count = 0
    queue_count = 0
    scan_outcode = outcode.lower()
    queue_name = common.format_landreg_resource_name(scan_outcode)

    # always create the queue for the queue client it returns.
    qc = storage_queue.get_queue_client(queue_name)

    for stream_rec in http_reader.stream_file(url):
        record_count += 1
        rec = landreg_decoder.prune_rec_for_queue(stream_rec)

        # if the outcode exists and is the one we are searching for.
        if len(rec['Postcode']) > 0:
            outcode = rec['Postcode'].split(' ')[0].lower()
            
            if outcode == scan_outcode:
                qc.send_message(rec)
                queue_count += 1

    logging.info(f'Queue Created = {queue_name}')
    logging.info(f'File records read = {record_count}')
    logging.info(f'Messages sent = {queue_count}')
    return record_count

#---------------------------------------------------------------------------------------# 
def main(getLandregUpdates: func.TimerRequest) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)

    url1 = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
    url2 = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-2020.csv"
    
    rec_count = read_and_decode(url2, "E14")

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
