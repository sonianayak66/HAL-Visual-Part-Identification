using System.IO;
using HAL_IMS_MVC.Models;
using HAL_IMS_MVC.Services;
using Microsoft.AspNetCore.Mvc;

namespace HAL_IMS_MVC.Controllers
{
    public class IdentifyController : Controller
    {
        private readonly HalApiService _api;

        public IdentifyController(HalApiService api)
        {
            _api = api;
        }

        [HttpGet]
        public IActionResult Index()
        {
            return View(new IdentifyViewModel());
        }

        [HttpPost]
        public async Task<IActionResult> Index(IFormFile? file, string? partNumberSearch)
        {
            var vm = new IdentifyViewModel();

            try
            {
                if (!string.IsNullOrWhiteSpace(partNumberSearch))
                {
                    var result = await _api.SearchPartAsync(partNumberSearch);
                    Console.WriteLine("RESULT COUNT: " + result?.Results?.Count);

                    if (result != null && result.Results.Any())
                    {
                        var r = result.Results.First();

                        vm.Results = result.Results;
                        vm.PartNumber = r.PartLabel;
                        vm.ComponentName = r.ComponentName;
                        vm.Description = r.Description;

                        if (r.Images != null && r.Images.Any())
                        {
                            vm.ImagePaths = r.Images
                                .Select(img => img.StartsWith("http")
                                    ? img
                                    : $"/imagedatabase/{r.PartLabel}/{img}")
                                .ToList();
                        }
                    }
                }
                else if (file != null)
                {
                    var result = await _api.SearchImageAsync(file);
                    Console.WriteLine("RESULT COUNT: " + result?.Results?.Count);

                    if (result != null && result.Results.Any())
                    {
                        var r = result.Results.First();

                        vm.Results = result.Results;
                        vm.PartNumber = r.PartLabel;
                        vm.ComponentName = r.ComponentName;
                        vm.Description = r.Description;

                        if (r.Images != null && r.Images.Any())
                        {
                            vm.ImagePaths = r.Images
                                .Select(img => img.StartsWith("http")
                                    ? img
                                    : $"/imagedatabase/{r.PartLabel}/{img}")
                                .ToList();
                        }
                    }
                    else if (result != null)
                    {
                        vm.Results = result.Results;
                    }
                }
                else
                {
                    vm.Error = "Provide part number or upload image.";
                }
            }
            catch (Exception ex)
            {
                vm.Error = ex.Message;
            }

            return View(vm);
        }
    }
}