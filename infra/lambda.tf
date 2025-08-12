data "aws_ecr_image" "lambda_image" {
  repository_name = aws_ecr_repository.lambda_repo.name
  image_tag       = "latest"
}

resource "aws_lambda_function" "ingest_youtube_data" {
  function_name = "youtube_ingest"
  role          = aws_iam_role.lambda_exec.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.lambda_repo.repository_url}@${data.aws_ecr_image.lambda_image.image_digest}"
  timeout       = 300

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_bucket.bucket
    }
  }
}