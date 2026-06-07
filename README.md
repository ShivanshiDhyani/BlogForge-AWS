# BlogForge AI — AWS Bedrock Blog Generator

A serverless AI-powered blog generator built on AWS.

## Architecture

User → S3/CloudFront (Frontend) → API Gateway → Lambda → Amazon Bedrock → S3 (Blog Storage)

## Tech Stack

- **Frontend** — HTML/CSS/JS hosted on Amazon S3
- **API Gateway** — HTTP API endpoint
- **AWS Lambda** — Python 3.12 serverless function
- **Amazon Bedrock** — Amazon Nova Micro foundation model
- **Amazon S3** — Blog file storage
- **Amazon CloudWatch** — Logs, metrics, and error monitoring
- **IAM** — Role-based access control for Lambda permissions

## Features

- Generate 200-word blogs on any topic instantly
- Automatic retry logic with exponential backoff
- Cross-region inference for better availability
- Blog saved to S3 with timestamped filename
- CloudWatch logging for every Lambda invocation
- Clean editorial UI with copy and download options

## Setup Instructions

### 1. Lambda Function
- Runtime: Python 3.12
- Timeout: 300 seconds
- Add boto3 Lambda layer (latest version)
- Attach IAM policies: AmazonBedrockFullAccess, AmazonS3FullAccess

### 2. API Gateway
- Type: HTTP API
- Route: POST /blog_generation
- Integration: Lambda function
- Enable CORS: Allow-Origin *

### 3. S3 Buckets
- `bedrockbucketoutput` — stores generated blog files
- `blog-frontend` — hosts the frontend (static website hosting enabled)

### 4. Monitoring with CloudWatch

All Lambda invocations are automatically logged to CloudWatch under:
`/aws/lambda/bedrockblog`

### 5. Frontend
- Update API_URL in index.html with your API Gateway endpoint
- Upload index.html to your frontend S3 bucket

## Challenges Faced

- New account token quota limits — solved with cross-region inference
- Lambda boto3 version outdated — solved with custom Lambda layer
- IAM permission debugging for bedrock:InvokeModel
- ThrottlingException handling — implemented exponential backoff with jitter

## Author

Shivanshi Dhyani
