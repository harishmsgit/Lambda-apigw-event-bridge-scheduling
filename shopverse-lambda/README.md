# Shopverse Lambda Project

This repository contains AWS Lambda functions for the Shopverse application, designed to handle product ingestion, image thumbnail generation, and nightly maintenance tasks. The project demonstrates a modular serverless architecture on AWS Lambda with multiple event triggers.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [AWS Setup](#aws-setup)
- [Local Development](#local-development)
- [Packaging and Deployment](#packaging-and-deployment)
- [Configuring Triggers](#configuring-triggers)
- [Testing](#testing)
- [Lambda Configuration](#lambda-configuration)
- [Quick Command Reference](#quick-command-reference)

---

## Overview

This project implements three Lambda functions that work together to create a complete serverless application:

1. **lambda_api_ingest**: Handles product data ingestion via API Gateway
2. **lambda_image_thumb**: Processes images uploaded to S3 and generates thumbnails
3. **lambda_nightly_maintenance**: Performs scheduled maintenance tasks via EventBridge

### Key Features

- **Modular Architecture**: Each Lambda is self-contained with its own dependencies
- **Shared Utilities**: Common code in the `common/` directory for reusability
- **Event-Driven**: Responds to multiple AWS event sources (API Gateway, S3, EventBridge)
- **Production-Ready**: Follows AWS best practices for Lambda development

---

## Project Structure

```
shopverse-lambda/
├── common/
│   └── utils.py                  # Shared utility functions
├── lambda_api_ingest/
│   ├── app.py                    # Lambda for API ingestion
│   └── requirements.txt          # Dependencies for API ingest
├── lambda_image_thumb/
│   ├── app.py                    # Lambda for image thumbnailing
│   └── requirements.txt          # Dependencies for image thumbnail
├── lambda_nightly_maintenance/
│   ├── app.py                    # Lambda for nightly maintenance
│   └── requirements.txt          # Dependencies for maintenance
├── scripts/
│   └── package_and_deploy.sh     # Script to package and deploy all Lambdas
└── README.md                     # This file
```

---

## Prerequisites

### Required Tools

- **AWS Account** with appropriate permissions
- **AWS CLI v2** configured with a profile (e.g., `shopverse`)
- **Python 3.11** installed locally
- **zip utility** for packaging Lambda functions

### EC2 Instance (Optional)

An AWS EC2 instance can be used for:
- Development environment
- Deployment automation
- Bastion/jump host for secure AWS resource access

Ensure your EC2 instance has:
- IAM role or credentials for AWS service access
- Python 3.11 and AWS CLI installed
- Network access to required AWS services

---

## AWS Setup

### 1. DynamoDB Table for Metadata

Create a DynamoDB table to store product metadata:

```bash
aws dynamodb create-table \
  --table-name ShopVerseProducts \
  --attribute-definitions AttributeName=product_id,AttributeType=S \
  --key-schema AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 \
  --profile shopverse
```

### 2. S3 Bucket for Images

Create an S3 bucket for product images:

```bash
aws s3 mb s3://shopverse-product-images-<suffix> \
  --region us-east-1 \
  --profile shopverse
```

Replace `<suffix>` with a unique identifier (e.g., your AWS account ID).

### 3. IAM Roles and Permissions

Create IAM roles for each Lambda function with least-privilege permissions.

**Create trust policy** (`trust-policy.json`):

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

**Create API Lambda role:**

```bash
aws iam create-role \
  --role-name ShopVerseApiRole \
  --assume-role-policy-document file://trust-policy.json \
  --region us-east-1 \
  --profile shopverse

aws iam put-role-policy \
  --role-name ShopVerseApiRole \
  --policy-name ShopVerseApiDynamoPolicy \
  --policy-document file://policy-api-dynamo.json \
  --region us-east-1 \
  --profile shopverse
```

Repeat for other roles:
- `ShopVerseImageRole` with S3 read/write permissions
- `ShopVerseMaintenanceRole` with required maintenance permissions

All roles should include CloudWatch Logs permissions.

---

## Local Development

### 1. Clone the Repository

```bash
git clone <repo-url>
cd shopverse-lambda
```

### 2. Install Dependencies

Install dependencies for each Lambda function locally:

```bash
pip install -r lambda_api_ingest/requirements.txt -t lambda_api_ingest/
pip install -r lambda_image_thumb/requirements.txt -t lambda_image_thumb/
pip install -r lambda_nightly_maintenance/requirements.txt -t lambda_nightly_maintenance/
```

### 3. Lambda Handler Structure

Each Lambda's `app.py` defines a handler function:

```python
def handler(event, context):
    # Your logic here
    return {
        "statusCode": 200,
        "body": "Success"
    }
```

---

## Packaging and Deployment

### Automated Deployment

Use the provided script to package and deploy all Lambda functions:

```bash
cd scripts
sh package_and_deploy.sh
```

The script handles:
- Zipping code and dependencies
- Uploading to AWS Lambda using AWS CLI
- Updating existing functions

### Manual Deployment

**Create a new Lambda function:**

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

**Update existing Lambda code:**

```bash
aws lambda update-function-code \
  --function-name <FunctionName> \
  --zip-file fileb://function.zip \
  --region us-east-1 \
  --profile shopverse
```

---

## Configuring Triggers

### API Gateway (HTTP API) for ShopVerseApiIngest

**Console Steps:**

1. Open AWS Console → API Gateway
2. Create a new HTTP API
3. Add integration: Lambda → ShopVerseApiIngest
4. Add route: `POST /products`
5. Deploy the API and note the invoke URL

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

### S3 Trigger for ShopVerseImageThumb

**Console Steps:**

1. Open the S3 bucket (e.g., `shopverse-product-images-...`)
2. Go to Properties → Event notifications → Create event notification
3. Set event types: PUT (All object create events)
4. Set destination: Lambda → ShopVerseImageThumb

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

### EventBridge Schedule for ShopVerseNightlyMaintenance

**Console Steps:**

1. Open EventBridge in the AWS Console
2. Go to Rules → Create rule
3. Set schedule pattern: `cron(0 2 * * ? *)` (runs at 2:00 AM UTC daily)
4. Set target: Lambda → ShopVerseNightlyMaintenance

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

### API Function Testing

Invoke the API Gateway endpoint:

```bash
curl -X POST https://<api-gateway-url>/products \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Sample Product"}'
```

Expected response:
- HTTP Status: 201
- Body: `{"product_id": "..."}`

Check CloudWatch Logs for `ShopVerseApiIngest` for execution details.

### Image Lambda Testing

Upload an image to the S3 bucket:

```bash
aws s3 cp ./sample.jpg s3://shopverse-product-images-<suffix>/sample.jpg \
  --region us-east-1 \
  --profile shopverse
```

Check CloudWatch Logs for `ShopVerseImageThumb` for processing results.

### Nightly Maintenance Lambda Testing

**Option 1**: Wait for the scheduled EventBridge time

**Option 2**: Manually trigger the rule:

```bash
aws events put-events \
  --entries file://test-event.json \
  --region us-east-1 \
  --profile shopverse
```

Verify CloudWatch Logs for `ShopVerseNightlyMaintenance` for execution details.

---

## Lambda Configuration

After initial setup, focus on understanding and tuning these Lambda configuration options:

### Key Settings

- **Memory size**: Impacts CPU allocation and cost (128 MB to 10 GB)
- **Timeout**: Maximum execution duration (1 second to 15 minutes)
- **Ephemeral storage (`/tmp`)**: Size for temporary files (512 MB to 10 GB)
- **Environment variables**: Configuration without code changes (can be KMS encrypted)
- **Layers**: For shared code and native dependencies
- **Reserved concurrency**: Guaranteed function capacity
- **Provisioned concurrency**: Pre-warmed instances to avoid cold starts
- **Dead-letter queues (DLQ)**: SNS or SQS for async failure handling
- **VPC networking**: Access private resources (impacts cold start time)
- **Logging**: Structure, retention, and structured JSON logs

### Best Practices

1. **Start small**: Use minimal memory and timeout, then tune based on metrics
2. **Monitor costs**: Review AWS Cost Explorer regularly
3. **Use structured logging**: JSON format for better CloudWatch Insights queries
4. **Implement error handling**: Use DLQs for async invocations
5. **Secure environment variables**: Use KMS encryption for sensitive data

---

## Quick Command Reference

### List AWS Resources

```bash
# List DynamoDB tables
aws dynamodb list-tables --region us-east-1 --profile shopverse

# List Lambda functions
aws lambda list-functions --region us-east-1 --profile shopverse

# List S3 buckets
aws s3 ls --region us-east-1 --profile shopverse
```

### View Lambda Logs

```bash
# Tail logs in real-time
aws logs tail /aws/lambda/ShopVerseApiIngest --follow \
  --region us-east-1 \
  --profile shopverse
```

### Update Lambda Configuration

```bash
# Update memory size
aws lambda update-function-configuration \
  --function-name ShopVerseApiIngest \
  --memory-size 512 \
  --region us-east-1 \
  --profile shopverse

# Update timeout
aws lambda update-function-configuration \
  --function-name ShopVerseApiIngest \
  --timeout 30 \
  --region us-east-1 \
  --profile shopverse
```

---

## Notes

- Ensure AWS CLI is installed and configured with the `shopverse` profile
- Replace placeholder values (like `<repo-url>`, `<FunctionName>`, `<suffix>`) with your actual values
- All Lambda functions should have CloudWatch Logs permissions in their IAM roles
- Monitor CloudWatch metrics to optimize Lambda configuration
- Use AWS Cost Explorer to track and optimize costs

---

## Additional Resources

- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [API Gateway HTTP API Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- [EventBridge User Guide](https://docs.aws.amazon.com/eventbridge/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)

For the main project overview, see the [main README](../README.md).
