import os
import json


def lambda_handler(event, context):
    """
    AWS Lambda handler to process S3 event notifications.
    Extracts bucket name and object key from each record.
    """
    records = event.get("Records", [])

    info = [
        {
            "bucket": record["s3"]["bucket"]["name"],
            "key": record["s3"]["object"]["key"]
        }
        for record in records
    ]

    return {
        "statusCode": 200,
        "body": json.dumps({"received": info})
    }
