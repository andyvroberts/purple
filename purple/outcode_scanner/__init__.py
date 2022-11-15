import time
import logging
from collections import defaultdict
import azure.functions as func

from utils import http_reader
from utils import landreg_decoder
from utils import config_table
from utils import storage_queue
from utils import common

#---------------------------------------------------------------------------------------#
def read_file_and_check_config():
    record_count = 0
    queue_count = 0
    outcode_check = defaultdict(float)
    partition_key = common.config_outcode_changes_partition()
    outcode_status = common.config_ready_status()

    # get references for the table client and queue client
    tc = config_table.create(common.config_table_name())
    qc = storage_queue.create(common.load_trigger_queue_name())

    for stream_rec in http_reader.stream_file(common.landreg_monthly_update_url()):
        record_count += 1
        outcode, price = landreg_decoder.get_outcode(stream_rec)

        if outcode is not None:
            outcode_check[outcode] += price

    for k, v in outcode_check.items():
        row_key = common.format_landreg_resource_name(k)
        
        if config_table.have_outcode_rows_changed(tc, partition_key, row_key, v, outcode_status):
            queue_count += 1
            storage_queue.send_message(qc, k)

    logging.info(f'Number of outcodes = {len(outcode_check)}')
    logging.info(f'File records read = {record_count}')
    logging.info(f'{common.load_trigger_queue_name()} Queue messages sent = {queue_count}')
    return record_count


#---------------------------------------------------------------------------------------# 
def main(outcodeScanner: func.TimerRequest) -> None:
    start_exec = time.time()
    # suppress or show messages from Azure loggers.
    logging.getLogger("azure.core.pipeline").setLevel(logging.ERROR)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    #logging.getLogger('azure.storage.queue').setLevel(logging.DEBUG)
    
    rec_count = read_file_and_check_config()

    end_exec = time.time()
    duration = end_exec - start_exec
    hours, hrem = divmod(duration, 3600)
    mins, secs = divmod(hrem, 60)
    logging.info(f'Execution Duration: {hours}hrs, {mins}mins, {round(secs,0)}secs')
