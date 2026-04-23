using Microsoft.AspNetCore.Mvc;
using HAL_IMS_MVC.Models;
using HAL_IMS_MVC.Services;

namespace HAL_IMS_MVC.Controllers
{
    public class PartsController : Controller
    {
        private readonly HalApiService _api;

        public PartsController(HalApiService api)
        {
            _api = api;
        }

        [HttpGet]
        public async Task<IActionResult> Index()
        {
            try
            {
                var data = await _api.GetPartsAsync();
                return View(data ?? new PartsResponse { Parts = new List<PartEntry>() });
            }
            catch
            {
                return View(new PartsResponse { Parts = new List<PartEntry>() });
            }
        }

        [HttpPost]
        public async Task<IActionResult> Rebuild()
        {
            await _api.RebuildIndexAsync();
            return RedirectToAction("Index");
        }
    }
}