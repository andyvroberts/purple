import csv
import logging


log = logging.getLogger("purple.v2.src.local.model.decoder")
#---------------------------------------------------------------------------------------#
def price_record(rec):
    """for CSV files, decode a single line that may be quote delimited with embedded 
       commas. Return the record as a dict with only the data you want.

        Args:   
            rec: a CSV string representing a data record of columns
            Return: the dict of usable column names and values
    """
    in_cols = ['RowKey','Price','PriceDate','Postcode','PropertyType',\
               'NewBuild','Duration','Paon','Saon','Street','Locality',\
               'Town','District','County','PpdCategory','RecStatus']
    
    out_cols = ['Price','PriceDate','Postcode','PropertyType',\
                'NewBuild','Duration','Paon','Saon','Street','Locality',\
                'Town','District','County']

    return record_from_dict(rec, in_cols, out_cols)


#---------------------------------------------------------------------------------------#
def mapping_postcode(rec):
    """for mapping outcodes to postcodes requires just the postcode property.

        Args:   
            rec: a CSV string representing a data record of columns
            Return: the dict of postcodes.
    """
    in_cols = ['RowKey','Price','PriceDate','Postcode','PropertyType',\
               'NewBuild','Duration','Paon','Saon','Street','Locality',\
               'Town','District','County','PpdCategory','RecStatus']
    
    out_cols = ['Postcode']

    return record_from_dict(rec, in_cols, out_cols)


#---------------------------------------------------------------------------------------#
def record_from_dict(rec, record_cols, required_cols):
    """for mapping outcodes to postcodes requires just the postcode property.

        Args:   
            rec: a CSV string representing a data record of columns
            Return: the dict of postcodes.
    """
    decoded_rec = csv.DictReader([rec], record_cols)
    in_dict = next(decoded_rec).copy()
    # use filter() function to remove unwanted columns 
    # (note, t[0] identifies the keys from in_dict but you could use t[1] for the values)
    out_dict = {k : v for k,v in filter(lambda t: t[0] in required_cols, in_dict.items())}
    return out_dict