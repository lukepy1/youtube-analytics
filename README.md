# YouTube Analytics Pipeline

This project collects and stores YouTube video analytics data in a serverless AWS architecture.

## Overview
The pipeline uses the YouTube Data API to retrieve video metadata and stores the results in Amazon S3. AWS Lambda handles the ingestion process, including basic cleaning and deduplication of records.

## Features
- Retrieve YouTube video metadata (title, views, likes, publish date, etc.)
- Remove duplicate records before storage
- Store data in S3 as CSV and Parquet files
- Runs on AWS Lambda without any server management

## Technologies Used
- Python
- AWS Lambda
- AWS S3
- YouTube Data API
- boto3
- google-api-python-client

