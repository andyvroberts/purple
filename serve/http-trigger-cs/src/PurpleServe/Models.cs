
using Azure.Data.Tables;
using Azure;

namespace PurpleServe
{

    public class PriceData : ITableEntity
    {
        public string? PartitionKey { get; set; }
        public string? RowKey { get; set; }
        public DateTimeOffset? Timestamp { get; set; }
        public ETag ETag { get; set; }
        public string? Addresses { get; set; }
    }

    public class PriceResult
    {
        public string? Postcode { get; set; }
        public List<PriceAddress>? PostcodePrices { get; set; }
    }

    public class PriceAddress
    {
        // element [0]
        public string? Address {get;set;}
        // element [1]
        public string? PriceDate { get; set; }
        // element [2]
        public string? Price {get;set;}
        // element [3]
        public string? Locality {get;set;}
        // element [4]
        public string? Town {get;set;}
        // element [6]
        public string? County {get;set;}
    }
}