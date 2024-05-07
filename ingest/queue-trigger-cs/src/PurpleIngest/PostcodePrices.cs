using System;
using Azure.Data.Tables;
using Azure.Storage.Queues.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;


namespace PurpleIngest
{
    public class PostcodePrices
    {
        private static TableClient? tabClient;

        [Function(nameof(PostcodePrices))]
        public static void Run(
            [QueueTrigger("prices")] QueueMessage msg,
            FunctionContext context)
        {
            var _logger = context.GetLogger(nameof(PostcodePrices));
            var tabRow = new PriceData();

            if (msg.MessageText != null)
            {
                var msgParts = msg.MessageText.Split('~');
                var postcode = msgParts[0];
                var addressString = msgParts[1];

                tabRow.PartitionKey = postcode.Split(' ')[0];
                tabRow.RowKey = postcode;
                tabRow.Addresses = addressString;

                var tabClient = GetTableClient("prices"); 
                tabClient.UpsertEntity(tabRow);

                _logger.LogInformation($"Postcode {postcode}: table entity updated or inserted.");
            }
            else
            {
                _logger.LogError($"Queue Message Body is empty.");
            }
        }

        private static TableClient GetTableClient(string tabName)
        {
            if (tabClient == null)
            {
                var connectionString = Environment.GetEnvironmentVariable("AzureWebJobsStorage");
                tabClient = new TableClient(connectionString, tabName);
            }
            return tabClient;

        }
    }
}
