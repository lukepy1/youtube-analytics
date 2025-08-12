resource "aws_ecr_repository" "lambda_repo" {
  name = "youtube-ingest"
  image_scanning_configuration {
    scan_on_push = true
  }
  force_delete = true
}
