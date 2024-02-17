import logging

log = logging.getLogger("purple.v2.src.local.model.formatter")
#---------------------------------------------------------------------------------------#
def list_to_string(data_list):
    """ convert a list data-type into a string for a column insert in table storage
    """
    data_string = ','.join(item for item in data_list)

    return data_string

#---------------------------------------------------------------------------------------#
def outcode_mapping(outcode, postcodes):
    """ format input into an azure storage table record (entity)

        Args:   
            outcode: the rowkey "S052"
            postcodes: {'SO52 9GR', 'SO52 9AW', 'SO52 9DQ'}".
            Return: a formatted record to insert into Azure Tables
    """
    new_rec = {}
    new_rec['PartitionKey'] = 'OUTCODE'
    new_rec['RowKey'] = outcode
    new_rec['postcodes'] = list_to_string(postcodes)
    new_rec['count'] = len(postcodes)
    new_rec['Status'] = 'A'

    return new_rec
