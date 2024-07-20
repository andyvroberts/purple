namespace PurpleFuncs
{
    public static class Mappers
    {
        /// <summary>
        /// Create an extension method on the PriceData for mapping inputs (model) to outputs (DTO).
        /// </summary>
        /// <param name="pd">An Azure Table Storage PriceData Record</param>
        /// <returns></returns>
        public static PriceResult DataToPrices(this PriceData pd)
        {
            PriceResult res = new();
            res.Postcode = pd.RowKey;

            if (pd.Addresses != null)
            {
                List<PriceAddress> addresses = [];

                List<string> prices = [.. pd.Addresses.Split('#')];
                foreach (string p in prices)
                {
                    string[] priceParts = p.Split('|');
                    PriceAddress pa = new() 
                    {
                        Address = priceParts[0],
                        Price = priceParts[1],
                        PriceDate = priceParts[2],
                        Locality = priceParts[3],
                        Town = priceParts[4],
                        County = priceParts[6]
                    };

                    addresses.Add(pa);
                }

                res.PostcodePrices = addresses;
                return res;
            }
            else
            {
                return res;
            }
        }
    }
}