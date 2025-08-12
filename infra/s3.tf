resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-youtube-data-12"
  force_destroy = true
}