import json
import boto3

ssm_client = boto3.client("ssm")


def get_user_credentials(schedule_name):
    username = ssm_client.get_parameter(Name=f"{schedule_name}/username")
    password = ssm_client.get_parameter(Name=f"{schedule_name}/password")
    return {
        "username": username.get("Parameter", {}).get("Value"),
        "password": password.get("Parameter", {}).get("Value"),
    }
