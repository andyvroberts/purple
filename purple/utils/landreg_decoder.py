import csv
#---------------------------------------------------------------------------------------#
def prune_rec_for_queue(rec):
    """for CSV files, decode a single line that may be quote delimited with embedded 
       commas. Return the record as a dict with only the data you want.
        Args:   
            rec: a CSV string representing a data record of columns
            Return: the dict of needed column names and values
    """
    in_cols = ['RowKey','Price','PriceDate','Postcode','PropertyType',\
               'NewBuild','Duration','Paon','Saon','Street','Locality',\
               'Town','District','County','PpdCategory','RecStatus']
    
    out_cols = ['Price','PriceDate','Postcode',\
                'Paon','Saon','Street','Locality',\
                'Town','District','County']

    decoded_rec = csv.DictReader([rec], in_cols)
    # shallow copy the next (actually, the only one) dictreader entry
    in_dict = next(decoded_rec).copy()
    # use filter() function to remove unwanted columns 
    # (note, t[0] identifies the keys from in_dict but you could use t[1] for the values)
    out_dict = {k : v for k,v in filter(lambda t: t[0] in out_cols, in_dict.items())}
    return out_dict