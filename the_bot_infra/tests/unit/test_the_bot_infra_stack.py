import aws_cdk as core
import aws_cdk.assertions as assertions

from the_bot_infra.the_bot_infra_stack import TheBotInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in the_bot_infra/the_bot_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TheBotInfraStack(app, "the-bot-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
