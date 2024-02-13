import logging

log = logging.getLogger("purple.v2.src.local.model.formatter")
#---------------------------------------------------------------------------------------#
def postcode_mapping(outcode, postcodes):
    """ format input into mapping records of partitions (outcode) to row keys (postcode)

        Args:   
            outcode: the partition name (outcode)
            data: input Dict: List = "SO52: {'SO52 9GR', 'SO52 9AW', 'SO52 9DQ'}".
            Return: formatted records (list of dicts)
    """
    map_list = []

    for val in postcodes:
        new_rec = {}
        new_rec['PartitionKey'] = outcode
        new_rec['RowKey'] = val
        new_rec['Status'] = 'N'

        map_list.append(new_rec)

    log.debug(f'({outcode}) formatted {len(map_list)} properties')
    return map_list

#---------------------------------------------------------------------------------------#
def outcode_mapping(data):
    """ format input list of outcodes to partiton key (constant) and row keys (outcode)

        Args:   
            data: batch records (list)
            Return: formatted records (list of dicts)
    """
    map_list = []

    for outcode in data:
        new_rec = {}
        new_rec['PartitionKey'] = 'OUTCODE'
        new_rec['RowKey'] = outcode

        map_list.append(new_rec)

    log.debug(f'({outcode}) formatted {len(map_list)} properties')
    return map_list