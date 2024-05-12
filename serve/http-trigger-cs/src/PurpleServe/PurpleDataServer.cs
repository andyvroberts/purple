using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.Logging;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Azure.Data.Tables;
using Azure;
using Microsoft.AspNetCore.Http.HttpResults;

namespace PurpleServe
{
    public class PurpleServerData
    {
        /// <summary>
        /// Return a variable number of postcode address+price records for a scan.
        /// Ideally, the consumer requests one postcode.
        /// Handle partial postcode inputs by using a scan.  Because scanning is allowed,
        /// the return dataset is restricted to 100 table entities (postcodes).
        /// </summary>
        /// <param name="req">Inbound HTTP request string</param>
        /// <param name="outcode">First part of the HTTP string with the outcode value</param>
        /// <param name="postcode">Second part of the HTTP string with the postcode value</param>
        /// <param name="postcodePrices">The Azure Table Storage prices table</param>
        /// <param name="context">Function app</param>
        /// <returns></returns>
        [Function("GetPrices")]
        public static async Task<IActionResult> GetPrices(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "prices/{outcode}/{postcode}")] HttpRequest req,
            string outcode, string postcode,
            [TableInput("prices")] TableClient postcodePrices,
            FunctionContext context)
        {
            var _logger = context.GetLogger(nameof(GetPrices));

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

            // setup the deferred query.  Azure Table Storage max entities returned per call = 1,000 but we use 25.
            AsyncPageable<PriceData> queryResults =
                postcodePrices.QueryAsync<PriceData>(
                    filter: queryFilter,
                    maxPerPage: 25,
                    cancellationToken: ct
                );

            List<PriceResult> returnData = await TableQueryPagination(_logger, maxPages, queryResults);

            return returnData.Count != 0 ?
                new OkObjectResult(returnData) :
                new NotFoundObjectResult(postcode);
        }

        /// <summary>
        /// Return a single Outcode Table Entity.
        /// note: TableInput bindings are not working as of worker.extensions.tables v1.3.0
        /// </summary>
        /// <param name="req">Inbound HTTP request string</param>
        /// <param name="outcode">final part of the HTTP string with the outcode value</param>
        /// <param name="outcodeData">The Azure Table Storage outcode table</param>
        /// <returns>200 with a list of postcodes or 404 with the searched outcode</returns>
        [Function("GetPostcodes")]
        public static IActionResult GetPostcodes(
            [HttpTrigger(AuthorizationLevel.Function, "get", Route = "postcodes/{outcode}")] HttpRequest req,
            string outcode,
            [TableInput("outcode")] TableClient outcodeData)
        {
            // this try-catch supresses the large amount of error logging thrown by the function app on a 404.
            try
            {
            var ocEntity =
                outcodeData.GetEntity<OutcodeData>("OUTCODE", outcode.ToUpper());
                return new OkObjectResult(ocEntity.Value.Postcodes);
            }
            catch (RequestFailedException e)
            {
                return new NotFoundObjectResult($"{e.Status} {outcode}");
            }
        }

        /// <summary>
        /// Manage multiple calls to Azure Table Storage based on Page size. This is an example, to show
        /// how paged retrieval works.
        /// </summary>
        /// <param name="_log">Function context logger</param>
        /// <param name="maxPageCount">maxPages set to 4</param>
        /// <param name="queryResults">The AsyncPageable deferred query, pagesize = 25 table entities</param>
        /// <returns></returns>
        private static async Task<List<PriceResult>> TableQueryPagination(ILogger _log, int maxPageCount, AsyncPageable<PriceData> queryResults)
        {
            List<PriceResult> returnData = [];
            int pageCounter = 0;

            // exeute query
            await foreach (Page<PriceData> pricePage in queryResults.AsPages())
            {
                pageCounter++;
                foreach (PriceData landregPrice in pricePage.Values)
                {
                    returnData.Add(landregPrice.DataToPrices());
                }

                if (pageCounter == maxPageCount)
                {
                    _log.LogWarning($"Maximum pages reached {pageCounter}.");
                    break;
                }
            }
            return returnData;
        }
    }

}
