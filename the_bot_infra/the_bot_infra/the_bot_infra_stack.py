from aws_cdk import (
    # Duration,
    Stack,
    BundlingOptions,
    # aws_sqs as sqs,
)
from constructs import Construct
from aws_cdk import Stack, aws_lambda as _lambda
from aws_cdk import Duration
import aws_cdk.aws_ssm as ssm

class TheBotInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        discord_webhook = ssm.StringParameter.value_for_string_parameter(
            self, "discord_webhook")
        
        powertools_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            id="lambda-powertools",
            layer_version_arn=f"arn:aws:lambda:us-east-1:017000801446:layer:AWSLambdaPowertoolsPythonV2:71"
        )

        the_bot_layer = _lambda.LayerVersion(
               self, 'the_bot_layer',
                code=_lambda.Code.from_asset(
                    "../",
                    bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -t /asset-output/python .",
                    ]
                )   ),
               compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
               description='the bot layer',
               layer_version_name='the_bot_layer_ver'
           )

        the_bot = _lambda.Function(
            self,
            "the_bot",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(
                "../the_bot/services"),
            handler="execute_operations.run_the_bot",
            timeout=Duration.minutes(10),
            layers=[the_bot_layer, powertools_layer],
            environment={
                "DISCORD_WEBHOOK": discord_webhook
            }
        )

