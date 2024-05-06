import logging


log = logging.getLogger("purple.v2.src.local.model.formatter")
#---------------------------------------------------------------------------------------#
def list_to_string(data_list):
    """ convert a list data-type into a string for a column insert in table storage
    """
    data_string = ','.join(item for item in data_list)

    return data_string


# ---------------------------------------------------------------------------------------#
def string_to_list(data_string):
    """ convert the retrieved table entity list-of-values into a python list type
    """
    data_array = data_string.split(',')

    return list(data_array)


#---------------------------------------------------------------------------------------#
def outcode_mapping(outcode, postcodes):
    """ format input into an azure storage table record (entity)

        Args:   
            outcode: the rowkey "S052"
            postcodes: ['SO52 9GR', 'SO52 9AW', 'SO52 9DQ']".
            Return: a formatted record to insert into Azure Tables
    """
    new_rec = {}
    new_rec['PartitionKey'] = 'OUTCODE'
    new_rec['RowKey'] = outcode
    new_rec['postcodes'] = list_to_string(postcodes)
    new_rec['count'] = len(postcodes)
    new_rec['Status'] = 'A'

    return new_rec

#---------------------------------------------------------------------------------------#
def compact_price_rec(price_dict):
    """ compact the input price record which is a dict.

        Args:   
            price_dict: {'Price': '532500', 'PriceDate': '2021-11-05 00:00', etc.}
            Return: a compacted price record string: '57 NEWFIELDS|434000|2023-08-30||, etc
    """
    address = format_address(price_dict['Paon'], price_dict['Saon'], price_dict['Street'])
    date = price_dict['PriceDate'][:10]

    return (
        f"{address}|{price_dict['Price']}|{date}|{price_dict['Locality']}" 
        f"|{price_dict['Town']}|{price_dict['District']}|{price_dict['County']}|"
        f"{price_dict['PropertyType']}|{price_dict['NewBuild']}|{price_dict['Duration']}"
    )

# ---------------------------------------------------------------------------------------#
def format_address(paon, saon, street):
    """join the parts of the record that form the unique address component.
        Args:   
            paon, saon, street: strings representing components of address line 1
            Return: the address string
    """
    address_seq = []
    if paon:
        address_seq.append(saon)
    if saon:
        address_seq.append(paon)
    if street:
        address_seq.append(street)

    address_string = ' '.join(address_seq)
    return address_string