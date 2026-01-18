Prerequisites
Accounts and tools

• An AWS account with access to create IAM roles, Lambda, S3, API Gateway, EventBridge, CloudWatch Logs.

• AWS CLI v2 installed and configured with a profile.

• Python 3.11 installed locally.

• zip utility (macOS/Linux built-in; on Windows, use PowerShell Compress-Archive or 7zip).

• Optional: AWS SAM CLI for local testing, but we will not use Terraform.

Knowledge

• Basic Python.

• Basic AWS concepts: IAM, S3, regions, policies.

• Comfort using the terminal.




Approach to Solve
We will build the solution incrementally and use Lambda configuration options deliberately so you understand what each knob does.

Step 1: Create an S3 bucket for product images and a DynamoDB table for product metadata (DynamoDB is minimal and serverless; we use it to persist API writes).

Step 2: Prepare a dedicated IAM execution role per Lambda with least-privilege policies (CloudWatch Logs, S3 read/write for the image function, DynamoDB write for the API function).

Step 3: Scaffold a Python project with one folder per Lambda. Use a shared “layer” later for common utilities.

Step 4: Package and deploy with zip uploads via AWS CLI and Console (to see exactly how code and configs relate).

Step 5: Wire up triggers: API Gateway → lambda_api_ingest, S3 put-object → lambda_image_thumb, EventBridge schedule → lambda_nightly_maintenance.

Step 6: Observe and tune configurations: memory (MB), timeout (seconds), ephemeral storage (/tmp), environment variables, reserved concurrency, DLQ/SNS, and logging format.

Step 7: Test each path end-to-end, read logs in CloudWatch, and iterate.




Complete Setup Guide
Choose a working AWS region (for example, us-east-1). Replace region/profile names as needed.

A) Local project scaffolding

Create a workspace on your machine:



B) Initialize AWS CLI

C) Create core AWS resources

D) Create IAM execution roles (least privilege)


E) Write initial Lambda code

F) Package and create Lambda functions

G) Configure triggers

API Gateway (HTTP API) for ShopVerseApiIngest:

Console steps (to reinforce config awareness):

Open API Gateway, create HTTP API.
Add integration → Lambda → ShopVerseApiIngest.
Add route POST /products to the integration.
Deploy and note the invoke URL.
Set Lambda permission to allow API Gateway invoke (Console usually does this; CLI if needed):

S3 trigger for ShopVerseImageThumb:

Open S3 bucket shopverse-product-images-.
Properties → Event notifications → Create.
Event types: PUT (All object create events).
Destination: Lambda → ShopVerseImageThumb.
CLI permission example:



EventBridge schedule for ShopVerseNightlyMaintenance:

EventBridge → Rules → Create rule.
Schedule pattern: cron(0 2 * * ? *) for 2:00 UTC daily.
Target: Lambda → ShopVerseNightlyMaintenance.
CLI permission example:



H) Basic testing

Invoke API function locally via API Gateway URL with a product name. Expect 201 and a product_id in the body.

Upload any image to the S3 bucket and check CloudWatch Logs for ShopVerseImageThumb.

Wait for the scheduled time or manually trigger the EventBridge rule and verify CloudWatch Logs for ShopVerseNightlyMaintenance.

I) Where we will focus on Lambda configurations (what you’ll tweak next)

• Memory size and its impact on CPU and cost.

• Timeout behavior and retries across different event sources.

• Ephemeral storage (/tmp) size for temporary files.

• Environment variables and encryption (KMS).

• Layers for shared code and native dependencies.

• Reserved concurrency and provisioned concurrency.

• Dead-letter queues (SNS/SQS) for async failures.

• VPC networking (optional) and implications on cold start and egress.

• Logging structure, log retention, and structured JSON logs.

Downloadable files (copy-paste into your project)

• trust-policy.json

• policy-api-dynamo.json

• policy-s3-thumb.json

• The three app.py files and requirements.txt shown above

• scripts/package_and_deploy.sh (you can create a simple script that runs the packaging commands shown)

