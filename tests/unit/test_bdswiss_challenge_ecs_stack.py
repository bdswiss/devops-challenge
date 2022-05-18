import aws_cdk as core
import aws_cdk.assertions as assertions

from bdswiss_challenge_ecs.bdswiss_challenge_ecs_stack import BdswissChallengeEcsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in bdswiss_challenge_ecs/bdswiss_challenge_ecs_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BdswissChallengeEcsStack(app, "bdswiss-challenge-ecs")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
