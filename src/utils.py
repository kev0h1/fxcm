import json
import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name="MyDocDBSecret3E0BB6C4-lhNB3WLqtIVK"):
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]

    secret_data = json.loads(secret)

    return secret_data


def count_decimal_places(n):
    """count the number of decimal places"""
    str_n = str(n)
    if "." not in str_n:
        return 0
    return len(str_n) - str_n.index(".") - 1
