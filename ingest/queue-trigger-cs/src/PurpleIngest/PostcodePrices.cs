using System;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;
using Azure.Data.Tables;
using Azure.Storage.Queues.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace PurpleIngest
{
    public class PostcodePrices
    {
        [Function(nameof(PostcodePrices))]
        [TableOutput("prices")]
        public static void Run(
            [QueueTrigger("prices")] QueueMessage msg,
            FunctionContext context)
        {
            var _logger = context.GetLogger(nameof(PostcodePrices));
            //_logger.LogInformation($"C# Queue trigger function processed: {msg.MessageText}");

            if (msg.MessageText != null)
            {
                var _text = msg.MessageText;
                _text = _text.Replace('(','{').Replace(')','}');

                //var _data = JsonSerializer.Deserialize<Prices>(_text);
                _logger.LogInformation($"Converted: {_text}");
            }


            // return new PriceData()
            // {
            //     PartitionKey = "ANDY",
            //     RowKey = _data.Postcode,
            //     Addresses = msg.MessageText
            // };
        }
    }
}
