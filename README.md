# AWS Lambda API Gateway EventBridge Scheduling

A comprehensive serverless application demonstrating AWS Lambda integration with API Gateway, S3 event triggers, and EventBridge scheduling. This project includes three Lambda functions for product ingestion, image processing, and scheduled maintenance tasks.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Implementation Approach](#implementation-approach)
- [Setup Guide](#setup-guide)
- [Testing](#testing)
- [Lambda Configuration Guide](#lambda-configuration-guide)
- [Additional Resources](#additional-resources)

---

## Overview

This project demonstrates a production-ready serverless architecture using AWS Lambda with multiple event sources:

- **API Gateway Integration**: REST API for product data ingestion
- **S3 Event Triggers**: Automatic image thumbnail generation on upload
- **EventBridge Scheduling**: Scheduled nightly maintenance tasks

The solution is built incrementally to help you understand each AWS Lambda configuration option and how they work together.

---

## Architecture

```
API Gateway (POST /products) → Lambda (ShopVerseApiIngest) → DynamoDB
S3 Bucket (image upload) → Lambda (ShopVerseImageThumb) → S3 (thumbnails)
EventBridge (cron schedule) → Lambda (ShopVerseNightlyMaintenance) → CloudWatch
```

### Components:
- **DynamoDB**: Stores product metadata
- **S3**: Stores product images and generated thumbnails
- **Lambda Functions**: Three serverless functions for different tasks
- **API Gateway**: HTTP API endpoint for product ingestion
- **EventBridge**: Scheduled rule for maintenance tasks
- **CloudWatch Logs**: Centralized logging for all functions

---

## Prerequisites

### AWS Account and Tools

- **AWS Account** with permissions to create:
  - IAM roles and policies
  - Lambda functions
  - S3 buckets
  - API Gateway
  - EventBridge rules
  - CloudWatch Logs
  - DynamoDB tables

- **AWS CLI v2** installed and configured with a profile

- **Python 3.11** installed locally

- **zip utility** (built-in on macOS/Linux; on Windows use PowerShell `Compress-Archive` or 7zip)

- **Optional**: AWS SAM CLI for local testing

### Required Knowledge

- Basic Python programming
- Fundamental AWS concepts (IAM, S3, regions, policies)
- Command-line interface experience
- Understanding of REST APIs and event-driven architectures

---

## Project Structure

```
Lambda-apigw-event-bridge-scheduling/
├── README.md                          # This file
└── shopverse-lambda/
    ├── common/
    │   └── utils.py                   # Shared utility functions
    ├── lambda_api_ingest/
    │   ├── app.py                     # API Gateway Lambda handler
    │   └── requirements.txt
    ├── lambda_image_thumb/
    │   ├── app.py                     # S3 trigger Lambda handler
    │   └── requirements.txt
    ├── lambda_nightly_maintenance/
    │   ├── app.py                     # EventBridge Lambda handler
    │   └── requirements.txt
    ├── scripts/
    │   └── package_and_deploy.sh      # Deployment automation script
    └── README.md                       # Detailed implementation guide
```

---

## Implementation Approach

We build this solution incrementally with deliberate configuration choices:

### Step 1: Create Core AWS Resources
Create an S3 bucket for product images and a DynamoDB table for product metadata. DynamoDB is serverless and minimal, perfect for persisting API writes.

### Step 2: Setup IAM Roles (Least Privilege)
Prepare dedicated IAM execution roles for each Lambda with minimum required permissions:
- CloudWatch Logs for all functions
- S3 read/write for image processing function
- DynamoDB write for API function

### Step 3: Scaffold Python Project
Create one folder per Lambda function. Plan to use a shared "layer" for common utilities.

### Step 4: Package and Deploy
Package functions using zip and deploy via AWS CLI and Console to understand how code and configurations relate.

### Step 5: Configure Event Sources
Wire up the triggers:
- **API Gateway** → `lambda_api_ingest`
- **S3 put-object event** → `lambda_image_thumb`
- **EventBridge schedule** → `lambda_nightly_maintenance`

### Step 6: Tune Lambda Configurations
Observe and adjust settings:
- Memory (MB) allocation
- Timeout (seconds)
- Ephemeral storage (`/tmp`)
- Environment variables
- Reserved concurrency
- Dead Letter Queues (DLQ/SNS)
- Logging format (structured JSON)

### Step 7: Test and Iterate
Test each integration path end-to-end, read CloudWatch Logs, and refine.

---

## Setup Guide

### A) Local Project Scaffolding

Create a workspace on your machine:

```bash
mkdir shopverse-lambda
cd shopverse-lambda
```

### B) Initialize AWS CLI

Configure your AWS CLI profile:

```bash
aws configure --profile shopverse
# Enter your AWS Access Key ID, Secret Key, default region (e.g., us-east-1)
```

### C) Create Core AWS Resources

**1. Create DynamoDB Table:**

```bash
aws dynamodb create-table \
  --table-name ShopVerseProducts \
  --attribute-definitions AttributeName=product_id,AttributeType=S \
  --key-schema AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 \
  --profile shopverse
```

**2. Create S3 Bucket:**

```bash
aws s3 mb s3://shopverse-product-images-<unique-suffix> \
  --region us-east-1 \
  --profile shopverse
```

Replace `<unique-suffix>` with a unique identifier (e.g., your account ID or timestamp).

### D) Create IAM Execution Roles (Least Privilege)

**1. Create trust policy file (`trust-policy.json`):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**2. Create role for API ingest Lambda:**

```bash
aws iam create-role \
  --role-name ShopVerseApiRole \
  --assume-role-policy-document file://trust-policy.json \
  --profile shopverse

aws iam put-role-policy \
  --role-name ShopVerseApiRole \
  --policy-name ShopVerseApiDynamoPolicy \
  --policy-document file://policy-api-dynamo.json \
  --profile shopverse
```

Repeat similar steps for `ShopVerseImageRole` and `ShopVerseMaintenanceRole` with appropriate policies.

### E) Write Initial Lambda Code

Refer to the `shopverse-lambda/` directory for detailed Lambda function implementations. Each Lambda includes an `app.py` handler and `requirements.txt` for dependencies.

### F) Package and Create Lambda Functions

**1. Install dependencies locally:**

```bash
cd lambda_api_ingest
pip install -r requirements.txt -t .
```

**2. Package the function:**

```bash
zip -r function.zip .
```

**3. Create Lambda function:**

```bash
aws lambda create-function \
  --function-name ShopVerseApiIngest \
  --runtime python3.11 \
  --role arn:aws:iam::<account-id>:role/ShopVerseApiRole \
  --handler app.handler \
  --zip-file fileb://function.zip \
  --region us-east-1 \
  --profile shopverse
```

Repeat for other Lambda functions (`ShopVerseImageThumb`, `ShopVerseNightlyMaintenance`).

### G) Configure Triggers

#### API Gateway (HTTP API) for ShopVerseApiIngest

**Console Steps:**

1. Open AWS Console → API Gateway
2. Create new HTTP API
3. Add integration: Lambda → ShopVerseApiIngest
4. Add route: `POST /products`
5. Deploy and note the invoke URL

**Add Lambda Permission:**

```bash
aws lambda add-permission \
  --function-name ShopVerseApiIngest \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --statement-id apigateway-invoke \
  --region us-east-1 \
  --profile shopverse
```

#### S3 Trigger for ShopVerseImageThumb

**Console Steps:**

1. Open S3 bucket `shopverse-product-images-<suffix>`
2. Properties → Event notifications → Create
3. Event types: PUT (All object create events)
4. Destination: Lambda → ShopVerseImageThumb

**Add Lambda Permission:**

```bash
aws lambda add-permission \
  --function-name ShopVerseImageThumb \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --statement-id s3-invoke \
  --source-arn arn:aws:s3:::shopverse-product-images-<suffix> \
  --region us-east-1 \
  --profile shopverse
```

#### EventBridge Schedule for ShopVerseNightlyMaintenance

**Console Steps:**

1. Open EventBridge → Rules → Create rule
2. Schedule pattern: `cron(0 2 * * ? *)` (2:00 AM UTC daily)
3. Target: Lambda → ShopVerseNightlyMaintenance

**Add Lambda Permission:**

```bash
aws lambda add-permission \
  --function-name ShopVerseNightlyMaintenance \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --statement-id eventbridge-invoke \
  --source-arn arn:aws:events:us-east-1:<account-id>:rule/<rule-name> \
  --region us-east-1 \
  --profile shopverse
```

---

## Testing

### H) Basic Testing

**1. Test API Function:**

```bash
curl -X POST https://<api-gateway-url>/products \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Sample Product"}'
```

Expected response: HTTP 201 with `product_id` in body.

**2. Test Image Processing:**

```bash
aws s3 cp sample-image.jpg s3://shopverse-product-images-<suffix>/sample-image.jpg \
  --region us-east-1 \
  --profile shopverse
```

Check CloudWatch Logs for `ShopVerseImageThumb` to verify processing.

**3. Test Scheduled Maintenance:**

Either wait for the scheduled time or manually trigger the EventBridge rule:

```bash
aws events put-events \
  --entries file://test-event.json \
  --region us-east-1 \
  --profile shopverse
```

Verify CloudWatch Logs for `ShopVerseNightlyMaintenance`.

---

## Lambda Configuration Guide

### I) Key Configuration Areas

After initial setup, focus on understanding and tuning these Lambda settings:

#### Memory and CPU
- **Memory size**: Directly impacts CPU allocation and cost
- More memory = more CPU power
- Monitor execution duration to optimize cost

#### Timeouts and Retries
- **Timeout**: Maximum execution duration (1 second to 15 minutes)
- Different event sources have different retry behaviors
- Configure based on expected workload

#### Storage
- **Ephemeral storage (`/tmp`)**: Size available for temporary files (512 MB to 10 GB)
- Useful for image processing, file downloads, etc.

#### Environment Variables
- Store configuration without code changes
- Can be encrypted with AWS KMS
- Access via `os.environ` in code

#### Concurrency
- **Reserved concurrency**: Guaranteed function capacity
- **Provisioned concurrency**: Pre-warmed instances to avoid cold starts
- Balance cost vs. performance

#### Error Handling
- **Dead-letter queues (DLQ)**: SNS or SQS for failed async invocations
- Essential for production workloads
- Enables retry mechanisms

#### Networking (Optional)
- **VPC**: Access private resources (RDS, ElastiCache)
- Impacts cold start time
- Consider VPC endpoints for AWS services

#### Logging
- **CloudWatch Logs**: Automatic integration
- Use structured JSON for better searchability
- Configure log retention policies
- Monitor CloudWatch metrics for insights

---

## Additional Resources

### Required Files

Create these files in your project:

- **`trust-policy.json`**: IAM trust policy for Lambda execution role
- **`policy-api-dynamo.json`**: IAM policy for DynamoDB access
- **`policy-s3-thumb.json`**: IAM policy for S3 access
- **`app.py`** (×3): Lambda handlers for each function
- **`requirements.txt`** (×3): Dependencies for each function
- **`scripts/package_and_deploy.sh`**: Automation script for packaging and deployment

### Quick Commands Reference

```bash
# List resources
aws dynamodb list-tables --region us-east-1 --profile shopverse
aws lambda list-functions --region us-east-1 --profile shopverse
aws s3 ls --region us-east-1 --profile shopverse

# Update Lambda code
aws lambda update-function-code \
  --function-name <FunctionName> \
  --zip-file fileb://function.zip \
  --region us-east-1 \
  --profile shopverse

# View Lambda logs
aws logs tail /aws/lambda/ShopVerseApiIngest --follow --region us-east-1 --profile shopverse
```

---

## Next Steps

1. Review the detailed implementation in `shopverse-lambda/README.md`
2. Explore individual Lambda function code
3. Experiment with configuration options
4. Monitor costs in AWS Cost Explorer
5. Implement additional features (authentication, validation, etc.)

For detailed implementation instructions and code samples, see the [shopverse-lambda README](./shopverse-lambda/README.md).

---

**License**: MIT  
**Author**: Harish  
**Repository**: [Lambda-apigw-event-bridge-scheduling](https://github.com/harishmsgit/Lambda-apigw-event-bridge-scheduling)
