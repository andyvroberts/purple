import logging

log = logging.getLogger("purple.v2.src.local.ukio.file_reader")
#---------------------------------------------------------------------------------------#   
def stream_file(file_path):
    """create a generator to stream-read file lines (records) from the local file system.

        Args:
            path: the path to the data.
            Return: a generator of file records
    """
    log.info(f'Streaming price file from disk {file_path}.')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f: 
                yield line

    except FileNotFoundError as fnfe:
        log.error('Local file was not found: {}'.format(fnfe))
        logging.shutdown()
        raise fnfe
    except Exception as ex:
        log.error('Unable to load data from local file: {}'.format(ex))
        logging.shutdown()
        raise ex