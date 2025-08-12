terraform {
  backend "s3" {
    bucket         = "my-tf-backend-26722be1"
    key            = "youtube-data.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}