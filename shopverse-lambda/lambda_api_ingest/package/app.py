import json
import os
import uuid
import boto3

# Get DynamoDB table name from environment variable (default: ShopVerseProducts)
TABLE_NAME = os.getenv("TABLE_NAME", "ShopVerseProducts")

# Initialize DynamoDB resource and table
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    """
    Lambda handler for ingesting product data.
    Expects an API Gateway event with a JSON body containing 'name'.
    """
    try:
        # API Gateway sends the request body as a string
        body = event.get("body") or "{}"
        payload = json.loads(body) if isinstance(body, str) else body

        # Validate required field
        name = payload.get("name")
        if not name:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "name is required"})
            }

        # Generate a unique product ID
        product_id = str(uuid.uuid4())

        # Build item and insert into DynamoDB
        item = {
            "product_id": product_id,
            "name": name
        }
        table.put_item(Item=item)

        # Return success response
        return {
            "statusCode": 201,
            "body": json.dumps({"product_id": product_id})
        }

    except Exception as e:
        # Catch any unexpected errors
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
