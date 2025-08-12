output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "ecr_repo_url" {
  value = aws_ecr_repository.lambda_repo.repository_url
}