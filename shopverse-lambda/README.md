
# Shopverse Lambda Project

This repository contains AWS Lambda functions for Shopverse, designed to handle product ingestion, image thumbnail generation, and nightly maintenance tasks. The project is organized for modular development and deployment on AWS Lambda.

---

## EC2 Instance Requirement

An AWS EC2 instance is required for development, deployment, or as a jump/bastion host to access AWS resources securely. Ensure your EC2 instance is set up with the necessary IAM role or credentials to interact with AWS services (Lambda, S3, DynamoDB, etc.).


## Key AWS CLI and Local Commands

- **DynamoDB Table Creation:**
	```sh
	aws dynamodb create-table \
		--table-name ShopVerseProducts \
		--attribute-definitions AttributeName=product_id,AttributeType=S \
		--key-schema AttributeName=product_id,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--region us-east-1 \
		--profile shopverse
	```
- **S3 Bucket Creation:**
	```sh
	aws s3 mb s3://shopverse-product-images-<suffix> --region us-east-1 --profile shopverse
	```
- **IAM Role Creation:**
	```sh
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
- **Lambda Function Creation:**
	```sh
	aws lambda create-function \
		--function-name ShopVerseApiIngest \
		--runtime python3.11 \
		--role arn:aws:iam::<account-id>:role/ShopVerseApiRole \
		--handler app.handler \
		--zip-file fileb://function.zip \
		--region us-east-1 \
		--profile shopverse
	```
- **Update Lambda Code:**
	```sh
	aws lambda update-function-code --function-name <FunctionName> --zip-file fileb://function.zip --region us-east-1 --profile shopverse
	```
- **Add Lambda Permissions for Triggers:**
	- API Gateway:
		```sh
		aws lambda add-permission \
			--function-name ShopVerseApiIngest \
			--action lambda:InvokeFunction \
			--principal apigateway.amazonaws.com \
			--statement-id apigateway-invoke \
			--region us-east-1 \
			--profile shopverse
		```
	- S3:
		```sh
		aws lambda add-permission \
			--function-name ShopVerseImageThumb \
			--action lambda:InvokeFunction \
			--principal s3.amazonaws.com \
			--statement-id s3-invoke \
			--source-arn arn:aws:s3:::shopverse-product-images-<suffix> \
			--region us-east-1 \
			--profile shopverse
		```
	- EventBridge:
		```sh
		aws lambda add-permission \
			--function-name ShopVerseNightlyMaintenance \
			--action lambda:InvokeFunction \
			--principal events.amazonaws.com \
			--statement-id eventbridge-invoke \
			--source-arn arn:aws:events:us-east-1:<account-id>:rule/<rule-name> \
			--region us-east-1 \
			--profile shopverse
		```
- **List Resources:**
	```sh
	aws dynamodb list-tables --region us-east-1 --profile shopverse
	aws lambda list-functions --region us-east-1 --profile shopverse
	aws s3 ls --region us-east-1 --profile shopverse
	```
- **Local Packaging and Dependency Installation:**
	```sh
	pip install -r lambda_api_ingest/requirements.txt -t lambda_api_ingest/
	pip install -r lambda_image_thumb/requirements.txt -t lambda_image_thumb/
	pip install -r lambda_nightly_maintenance/requirements.txt -t lambda_nightly_maintenance/
	```
- **Packaging and Deployment Script:**
	```sh
	cd scripts
	sh package_and_deploy.sh
	```
- **Test API Endpoint (curl):**
	```sh
	curl -X POST <api-gateway-url>/products \
		-H "Content-Type: application/json" \
		-d '{"product_name": "Sample Product"}'
	```
- **Upload Image to S3:**
	```sh
	aws s3 cp ./sample.jpg s3://shopverse-product-images-<suffix>/sample.jpg --region us-east-1 --profile shopverse
	```


# Shopverse Lambda Project

This repository contains AWS Lambda functions for Shopverse, designed to handle product ingestion, image thumbnail generation, and nightly maintenance tasks. The project is organized for modular development and deployment on AWS Lambda.

---

## Approach to Solve

We will build the solution incrementally and use AWS Lambda configuration options deliberately so you understand what each setting does.

**Step 1:** Create an S3 bucket for product images and a DynamoDB table for product metadata. (DynamoDB is minimal and serverless; we use it to persist API writes.)

**Step 2:** Prepare a dedicated IAM execution role per Lambda with least-privilege policies:
	- CloudWatch Logs for all functions
	- S3 read/write for the image function
	- DynamoDB write for the API function

**Step 3:** Scaffold a Python project with one folder per Lambda. Use a shared “layer” later for common utilities.

**Step 4:** Package and deploy with zip uploads via AWS CLI and Console (to see exactly how code and configs relate).

**Step 5:** Wire up triggers:
	- API Gateway → lambda_api_ingest
	- S3 put-object → lambda_image_thumb
	- EventBridge schedule → lambda_nightly_maintenance

**Step 6:** Observe and tune configurations:
	- Memory (MB)
	- Timeout (seconds)
	- Ephemeral storage (/tmp)
	- Environment variables
	- Reserved concurrency
	- DLQ/SNS
	- Logging format

**Step 7:** Test each path end-to-end, read logs in CloudWatch, and iterate.

---

## Project Structure

```
shopverse-lambda/
	common/
		utils.py                  # Shared utility functions
	lambda_api_ingest/
		app.py                    # Lambda for API ingestion
		requirements.txt          # Dependencies for API ingest
	lambda_image_thumb/
		app.py                    # Lambda for image thumbnailing
		requirements.txt          # Dependencies for image thumbnail
	lambda_nightly_maintenance/
		app.py                    # Lambda for nightly maintenance
		requirements.txt          # Dependencies for maintenance
	scripts/
		package_and_deploy.sh     # Script to package and deploy all Lambdas
	README.md                   # Project documentation
```

---

## AWS Setup

### 1. DynamoDB Table for Metadata

Create a DynamoDB table to store product metadata:

```sh
aws dynamodb create-table \
	--table-name ShopVerseProducts \
	--attribute-definitions AttributeName=product_id,AttributeType=S \
	--key-schema AttributeName=product_id,KeyType=HASH \
	--billing-mode PAY_PER_REQUEST \
	--region us-east-1 \
	--profile shopverse
```

### 2. IAM Roles and Permissions

- Create IAM roles for each Lambda function with least-privilege permissions.
- Attach policies for DynamoDB, S3, and CloudWatch as needed.

### 3. S3 Buckets

- Create S3 buckets for storing product images and thumbnails.

---

## Local Development

1. Clone the repository:
	 ```sh
	 git clone <repo-url>
	 cd shopverse-lambda
	 ```
2. Install dependencies for each Lambda:
	 ```sh
	 pip install -r lambda_api_ingest/requirements.txt -t lambda_api_ingest/
	 pip install -r lambda_image_thumb/requirements.txt -t lambda_image_thumb/
	 pip install -r lambda_nightly_maintenance/requirements.txt -t lambda_nightly_maintenance/
	 ```

---

## Packaging and Deployment

Use the provided script to package and deploy all Lambda functions:

```sh
cd scripts
sh package_and_deploy.sh
```

The script should handle zipping the code and dependencies, then use AWS CLI to update the Lambda functions.

---

## Example Lambda Handler

Each Lambda's `app.py` should define a handler function:

```python
def handler(event, context):
		# Your logic here
		return {"statusCode": 200, "body": "Success"}
```

---

## Configuring Triggers

### API Gateway (HTTP API) for ShopVerseApiIngest

**Console Steps:**

1. Open the AWS Console and go to API Gateway.
2. Create a new HTTP API.
3. Add an integration:
	 - Choose Lambda
	 - Select the ShopVerseApiIngest Lambda function
4. Add a route:
	 - Method: POST
	 - Resource path: /products
	 - Attach this route to the Lambda integration
5. Deploy the API and note the invoke URL for use in clients or tests.
6. Set Lambda permission to allow API Gateway invoke:
	 - The Console usually configures this automatically.
	 - If needed, use the AWS CLI:

```sh
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

1. Open the S3 bucket (e.g., shopverse-product-images-...)
2. Go to Properties → Event notifications → Create event notification.
3. Set event types to: PUT (All object create events)
4. Set destination to: Lambda → ShopVerseImageThumb

**CLI Permission Example:**

```sh
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

1. Open EventBridge in the AWS Console.
2. Go to Rules → Create rule.
3. Set schedule pattern to: `cron(0 2 * * ? *)` (runs at 2:00 UTC daily)
4. Set target to: Lambda → ShopVerseNightlyMaintenance

**CLI Permission Example:**

```sh
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

## Basic Testing

**API Function:**
- Invoke the API function locally or via the API Gateway URL with a product name in the request body.
- Expect HTTP 201 and a `product_id` in the response body.

**Image Lambda:**
- Upload any image to the S3 bucket.
- Check CloudWatch Logs for ShopVerseImageThumb for processing results.

**Nightly Maintenance Lambda:**
- Wait for the scheduled EventBridge time or manually trigger the rule.
- Verify CloudWatch Logs for ShopVerseNightlyMaintenance for execution details.

---

## Lambda Configuration Focus Areas

After initial setup, focus on tuning and understanding these Lambda configuration options:

- **Memory size:** Impacts CPU allocation and cost.
- **Timeout:** Behavior and retries for different event sources.
- **Ephemeral storage (/tmp):** Size for temporary files.
- **Environment variables:** Use and encryption (KMS).
- **Layers:** For shared code and native dependencies.
- **Reserved/provisioned concurrency:** Manage scaling and cold starts.
- **Dead-letter queues (SNS/SQS):** For async failure handling.
- **VPC networking (optional):** Impacts cold start and egress.
- **Logging:** Structure, retention, and use of structured JSON logs.

---

## Downloadable Files (Templates)

Copy-paste or create these files in your project as needed:

- `trust-policy.json`
- `policy-api-dynamo.json`
- `policy-s3-thumb.json`
- The three `app.py` files and `requirements.txt` (see above for structure)
- `scripts/package_and_deploy.sh` (simple script to run packaging commands)

---



## Notes

- Ensure AWS CLI is installed and configured with the `shopverse` profile.
- Replace placeholder values (like `<repo-url>`, `<FunctionName>`) with your actual values.
- For more details, see individual Lambda folders and scripts.
