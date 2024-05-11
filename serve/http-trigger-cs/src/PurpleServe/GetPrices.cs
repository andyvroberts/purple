using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Azure.Data.Tables;
using Azure;

namespace PurpleServe
{
    public class GetPrices
    {

        [Function("GetPrices")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "postcode/{outcode}/{postcode}")] HttpRequest req,
            string outcode, string postcode,
            [TableInput("prices", "{outcode}", "{postcode}")] TableClient postcodePrices,
            FunctionContext context)
        {
            var _logger = context.GetLogger(nameof(GetPrices));
            _logger.LogInformation($"C# HTTP trigger function processed a request to scan for outcode {outcode} and postcode {postcode}");

            // prepare for paginated calls to the Table service.
            var source = new System.Threading.CancellationTokenSource();
            var ct = source.Token;
            int maxPages = 4;

            // setup the search criteria.
            string partKey = outcode.ToUpper();
            string startScan = postcode.ToUpper();
            string endScan = startScan[..^1] + (char)(startScan.Last() + 1);

            // set the OData filters.
            var queryFilter = $"(PartitionKey eq '{partKey}') and ((RowKey ge '{startScan}') and (RowKey lt '{endScan}'))";
            _logger.LogInformation($"Search Filter = {queryFilter}");

            // setup the deferred query.
            AsyncPageable<PriceData> queryResults =
                postcodePrices.QueryAsync<PriceData>(
                    filter: queryFilter,
                    maxPerPage: 500,
                    cancellationToken: ct
                );

            List<PriceResult> returnData = await TableQueryPagination(_logger, maxPages, queryResults);

            if (returnData.Count != 0)
            {
                return new OkObjectResult(returnData);
            }
            else
            {
                return new NotFoundObjectResult($"No records found in Outcode partition of {postcodePrices.Name}.");
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="log"></param>
        /// <param name="maxPageCount"></param>
        /// <param name="queryResults"></param>
        /// <returns></returns>
        private static async Task<List<PriceResult>> TableQueryPagination(ILogger log, int maxPageCount, AsyncPageable<PriceData> queryResults)
        {
            List<PriceResult> returnData = [];
            int pageCounter = 0;

            await foreach (Page<PriceData> pricePage in queryResults.AsPages())
            {
                pageCounter++;
                foreach (PriceData landregPrice in pricePage.Values)
                {
                    returnData.Add(landregPrice.DataToPrices());
                }

                if (pageCounter == maxPageCount)
                {
                    log.LogInformation($"Maximum pages reached {pageCounter}.");
                    break;
                }
            }
            log.LogInformation($"Retrieved {returnData.Count} Localities from the data store.");
            return returnData;
        }
    }

}
