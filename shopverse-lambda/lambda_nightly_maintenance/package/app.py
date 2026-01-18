import json
import datetime


def lambda_handler(event, context):
    """
    AWS Lambda handler that returns the current UTC timestamp.
    Useful for maintenance checks or heartbeat monitoring.
    """
    # Get current UTC time in ISO 8601 format
    now = datetime.datetime.utcnow().isoformat()

    # Return response with timestamp
    return {
        "statusCode": 200,
        "body": json.dumps({"maintenance_run_utc": now})
    }
