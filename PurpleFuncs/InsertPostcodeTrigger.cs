using System;
using Azure.Data.Tables;
using Azure.Storage.Queues.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace PurpleFuncs
{
    public class InsertPostcodeTrigger
    {
        private static TableClient? tabClient;

        [Function(nameof(InsertPostcodeTrigger))]
        public static void InsertPostcode(
            [QueueTrigger("prices")] QueueMessage msg,
            FunctionContext context)
        {
            var _logger = context.GetLogger(nameof(InsertPostcodeTrigger));
            var tabRow = new PriceData();

            if (msg.MessageText != null)
            {
                decimal msgLen = msg.MessageText.Length;
                var lenKb = Math.Round(msgLen, 2, MidpointRounding.ToEven);
                var msgParts = msg.MessageText.Split('~');
                var postcode = msgParts[0];
                var addressString = msgParts[1];

                tabRow.PartitionKey = postcode.Split(' ')[0];
                tabRow.RowKey = postcode;
                tabRow.Addresses = addressString;
                _logger.LogInformation("Message payload.is {lenKb} Kb.", lenKb);

                var tabClient = GetTableClient("prices");
                tabClient.UpsertEntity(tabRow);

                _logger.LogInformation("Postcode {postcode}: prices added.", postcode);
            }
            else
            {
                _logger.LogError("Queue Message Body is empty.");
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
