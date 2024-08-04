using System.Text.Json.Serialization;

namespace GuessTheCookie.Model
{
    public class Cookie
    {
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [JsonPropertyName("profile_image_url")]
        public string ProfileImageUrl { get; set; }
        [JsonPropertyName("rarity")]
        public string Rarity { get; set; }
        [JsonPropertyName("attack_type")]
        public string AttackType { get; set; }
        [JsonPropertyName("position")]
        public string Position { get; set; }
    }
}
