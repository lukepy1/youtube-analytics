resource "aws_secretsmanager_secret" "youtube_api_key" {
  name        = "youtube-api-key"
  description = "YouTube Data API key used by Lambda"
}

resource "aws_secretsmanager_secret_version" "youtube_api_key_version" {
  secret_id     = aws_secretsmanager_secret.youtube_api_key.id
  secret_string = var.youtube_api_key
}

variable "youtube_api_key" {
  description = "The YouTube API key to store in Secrets Manager"
  type        = string
  sensitive   = true
}