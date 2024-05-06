using System;
using System.Collections.Generic;
using Azure;
using Azure.Data.Tables;

public class PriceData : ITableEntity
{
    public string? Addresses { get; set; }
    public string? PartitionKey { get; set; }
    public string? RowKey { get; set; }
    public DateTimeOffset? Timestamp { get; set; }
    public ETag ETag { get; set; }
}

public class Prices
{
    public string? Postcode { get; set; }
    public List<Addresses>? PostcodePrices { get; set; }
}

public class Addresses
{
    public string? AdddressRow { get; set; }
}