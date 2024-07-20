using Azure.Data.Tables;
using Azure;
using System.Runtime.Serialization;

namespace PurpleFuncs
{
    // Common Entities

    public class PriceData : ITableEntity
    {
        public string? PartitionKey { get; set; }
        public string? RowKey { get; set; }
        public DateTimeOffset? Timestamp { get; set; }
        public ETag ETag { get; set; }
        public string? Addresses { get; set; }
    }

    // HTTP Data Server Entities

    public class PriceResult
    {
        public string? Postcode { get; set; }
        public List<PriceAddress>? PostcodePrices { get; set; }
    }

    public class PriceAddress
    {
        // element [0]
        public string? Address { get; set; }
        // element [1]
        public string? PriceDate { get; set; }
        // element [2]
        public string? Price { get; set; }
        // element [3]
        public string? Locality { get; set; }
        // element [4]
        public string? Town { get; set; }
        // element [6]
        public string? County { get; set; }
    }

    /// <summary>
    /// The Outcode table entity. 
    /// Note, for example purposes, this table has one lowercase column name.
    /// </summary>
    public class OutcodeData : ITableEntity
    {
        public string? PartitionKey { get; set; }
        public string? RowKey { get; set; }
        public DateTimeOffset? Timestamp { get; set; }
        public ETag ETag { get; set; }
        public string? Status { get; set; }
        public int? Count { get; set; }
        [DataMember(Name = "postcodes")]
        public string? Postcodes { get; set; }
    }


    // Queue Trigger Entities

    public class Prices
    {
        public string? Postcode { get; set; }
        public List<Addresses>? PostcodePrices { get; set; }
    }

    public class Addresses
    {
        public string? AdddressRow { get; set; }
    }

}