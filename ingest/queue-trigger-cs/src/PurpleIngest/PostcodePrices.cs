using Azure.Storage.Queues.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace PurpleIngest
{
    public class PostcodePrices
    {
        [Function(nameof(PostcodePrices))]
        [TableOutput("prices")]
        public static PriceData Run(
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

                _logger.LogInformation($"Postcode: {postcode}");

                tabRow.PartitionKey = postcode.Split(' ')[0];
                tabRow.RowKey = postcode;
                tabRow.Addresses = addressString;
            }
            else
            {
                _logger.LogError($"Queue Message Body is empty.");
            }
            
            return tabRow;
        }
    }
}
