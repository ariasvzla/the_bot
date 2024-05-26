import json
import boto3


def create_schedule_params(
    lambda_target: str,
    schedule_input: dict,
    schedule_execution_time: str,
    schedule_name: str,
):

    return {
        "FlexibleTimeWindow": {"Mode": "OFF"},
        "Name": schedule_name,
        "ScheduleExpression": schedule_execution_time,
        "ScheduleExpressionTimezone": "UTC",
        "State": "ENABLED",
        "Target": {
            "Arn": lambda_target,
            "Input": json.dumps(schedule_input),
        },
    }


def update_schedule(
    lambda_target: str,
    schedule_name: str,
    schedule_input: str,
    schedule_execution_time,
) -> str | None:

    schedule_client = boto3.client("scheduler", region_name="us-east-1")
    schedule_parameters = create_schedule_params(
        lambda_target, schedule_input, schedule_execution_time, schedule_name
    )
    schedule_client.update_schedule(**schedule_parameters)
