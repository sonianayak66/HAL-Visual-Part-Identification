using Microsoft.AspNetCore.Mvc;
using HAL_IMS_MVC.Models;
using HAL_IMS_MVC.Services;

namespace HAL_IMS_MVC.Controllers
{
    public class AssignController : Controller
    {
        private readonly HalApiService _api;

        public AssignController(HalApiService api)
        {
            _api = api;
        }

        [HttpGet]
        public IActionResult Index()
        {
            return View(new AssignViewModel());
        }

        [HttpPost]
        public async Task<IActionResult> Index(
            string? partNumber,
            string? description,
            List<IFormFile> files)
        {
            var vm = new AssignViewModel();

            if (string.IsNullOrWhiteSpace(partNumber))
            {
                vm.Error = "Part number is required.";
                return View(vm);
            }

            if (files == null || files.Count == 0)
            {
                vm.Error = "Please upload at least one image.";
                return View(vm);
            }

            try
            {
                await _api.AddPartAsync(partNumber.Trim(), description ?? "", files);

                vm.SuccessMessage = $"✓ Part \"{partNumber}\" added successfully.";
            }
            catch (Exception ex)
            {
                vm.Error = $"Assignment failed: {ex.Message}";
            }

            return View(vm);
        }
    }
}