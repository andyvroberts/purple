using System;
using Azure.Storage.Queues.Models;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;

namespace PurpleIngest
{
    public class PostcodePrices
    {
        private readonly ILogger<PostcodePrices> _logger;

        public PostcodePrices(ILogger<PostcodePrices> logger)
        {
            _logger = logger;
        }

        [Function(nameof(PostcodePrices))]
        [TableOutput("prices")]
        public void Run(
            [QueueTrigger("prices")] QueueMessage message)
        {
            _logger.LogInformation($"C# Queue trigger function processed: {message.MessageText}");
        }
    }
}
