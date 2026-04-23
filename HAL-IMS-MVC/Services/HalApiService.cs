using System.Net.Http.Headers;
using System.Text.Json;
using HAL_IMS_MVC.Models;

namespace HAL_IMS_MVC.Services
{
    public class HalApiService
    {
        private readonly HttpClient _http;
        private readonly string _baseUrl = "http://127.0.0.1:8000";

        public HalApiService(HttpClient http)
        {
            _http = http;
        }

        // ------------------------------------
        // SEARCH BY PART NUMBER
        // ------------------------------------
        public async Task<IdentifyResponse?> SearchPartAsync(string partNumber)
        {
            var content = new MultipartFormDataContent();

            content.Add(new StringContent(partNumber), "part_number");

            var response = await _http.PostAsync($"{_baseUrl}/search/part", content);

            if (!response.IsSuccessStatusCode)
                return null;

            var json = await response.Content.ReadAsStringAsync();

            return JsonSerializer.Deserialize<IdentifyResponse>(json,
                new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
        }

        // ------------------------------------
        // SEARCH BY IMAGE
        // ------------------------------------
        public async Task<IdentifyResponse?> SearchImageAsync(IFormFile file)
        {
            using var content = new MultipartFormDataContent();

            using var stream = file.OpenReadStream();

            var fileContent = new StreamContent(stream);

            fileContent.Headers.ContentType =
                new MediaTypeHeaderValue(file.ContentType);

            content.Add(fileContent, "file", file.FileName);

            var response =
                await _http.PostAsync($"{_baseUrl}/search/image", content);

            var json = await response.Content.ReadAsStringAsync();

            Console.WriteLine("API RESPONSE:");
            Console.WriteLine(json);

            return JsonSerializer.Deserialize<IdentifyResponse>(json,
                new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
        }

        // ------------------------------------
        // ADD PART (ASSIGN PART)
        // ------------------------------------
        public async Task AddPartAsync(string partNumber,
                                       string description,
                                       List<IFormFile> files)
        {
            using var content = new MultipartFormDataContent();

            content.Add(new StringContent(partNumber), "part_number");
            content.Add(new StringContent(description ?? ""), "description");

            foreach (var file in files)
            {
                var stream = file.OpenReadStream();

                var fileContent = new StreamContent(stream);

                fileContent.Headers.ContentType =
                    new MediaTypeHeaderValue(file.ContentType);

                content.Add(fileContent, "files", file.FileName);
            }

            await _http.PostAsync($"{_baseUrl}/add_part", content);
        }

        // ------------------------------------
        // REBUILD INDEX
        // ------------------------------------
        public async Task RebuildIndexAsync()
        {
            await _http.GetAsync($"{_baseUrl}/rebuild_index");
        }

        // ------------------------------------
        // PART REGISTRY
        // ------------------------------------
        public async Task<PartsResponse?> GetPartsAsync()
        {
            var response = await _http.GetAsync($"{_baseUrl}/parts");

            if (!response.IsSuccessStatusCode)
                return null;

            var json = await response.Content.ReadAsStringAsync();

            return JsonSerializer.Deserialize<PartsResponse>(json,
                new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });
        }
    }
}