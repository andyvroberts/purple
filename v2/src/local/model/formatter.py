import logging

log = logging.getLogger("purple.v2.src.local.model.formatter")
#---------------------------------------------------------------------------------------#
def outcode_mapping(outcode, postcodes):
    """ format input into mapping records of partitions (outcode) to row keys (postcode)

        Args:   
            outcode: the rowkey "S052"
            postcodes: {'SO52 9GR', 'SO52 9AW', 'SO52 9DQ'}".
            Return: a formatted record to insert into Azure Tables
    """
    map_list = []

    new_rec = {}
    new_rec['PartitionKey'] = 'OUTCODE'
    new_rec['RowKey'] = outcode
    new_rec['postcodes'] = postcodes
    new_rec['count'] = len(postcodes)
    new_rec['Status'] = 'A'

    return map_list
