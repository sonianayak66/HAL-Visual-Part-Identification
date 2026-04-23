using System.Text.Json.Serialization;

namespace HAL_IMS_MVC.Models
{
    // -----------------------------
    // IDENTIFY RESULT
    // -----------------------------
    public class IdentifyResult
    {
        [JsonPropertyName("rank")]
        public int Rank { get; set; }

        [JsonPropertyName("part_label")]
        public string PartLabel { get; set; } = "";

        [JsonPropertyName("confidence_pct")]
        public double ConfidencePct { get; set; }

        [JsonPropertyName("component_name")]
        public string? ComponentName { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("images")]
        public List<string>? Images { get; set; }

        [JsonPropertyName("verdict")]
        public string? Verdict { get; set; }

        public string BadgeClass
        {
            get
            {
                if (ConfidencePct >= 90) return "badge-high";
                if (ConfidencePct >= 70) return "badge-medium";
                return "badge-low";
            }
        }

        public string BarColor
        {
            get
            {
                if (ConfidencePct >= 90) return "#16a34a";
                if (ConfidencePct >= 70) return "#d97706";
                return "#dc2626";
            }
        }
    }

    // -----------------------------
    // IDENTIFY RESPONSE
    // -----------------------------
    public class IdentifyResponse
    {
        [JsonPropertyName("results")]
        public List<IdentifyResult> Results { get; set; } = new();
    }

    // -----------------------------
    // VIEW MODEL
    // -----------------------------
    public class IdentifyViewModel
    {
        public string? PartNumberSearch { get; set; }

        public string? PartNumber { get; set; }

        public string? Description { get; set; }
        public string? ComponentName { get; set; }

        public List<IdentifyResult>? Results { get; set; }

        public List<string>? ImagePaths { get; set; }

        public string? Error { get; set; }
    }

    // -----------------------------
    // ASSIGN VIEW MODEL
    // -----------------------------
    public class AssignViewModel
    {
        public string? SuccessMessage { get; set; }

        public string? WarningMessage { get; set; }

        public string? Error { get; set; }
    }

    // -----------------------------
    // PART REGISTRY ENTRY
    // -----------------------------
    public class PartEntry
    {
        [JsonPropertyName("part_number")]
        public string PartNumber { get; set; } = "";

        [JsonPropertyName("component_name")]
        public string ComponentName { get; set; } = "";

        [JsonPropertyName("description")]
        public string Description { get; set; } = "";

        [JsonPropertyName("image_count")]
        public int ImageCount { get; set; }
    }

    // -----------------------------
    // PART REGISTRY RESPONSE
    // -----------------------------
    public class PartsResponse
    {
        [JsonPropertyName("total_parts")]
        public int TotalParts { get; set; }

        [JsonPropertyName("parts")]
        public List<PartEntry> Parts { get; set; } = new();
    }
}