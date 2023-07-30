from aws_cdk import App, aws_ec2
from fastapi_stack import FastAPIStack
from aws_cdk import Environment

app = App()
FastAPIStack(
    app,
    "FastAPIStack",
    env=Environment(
        account="547423740268",  # Replace with your AWS account ID
        region="us-east-1",  # Replace with your desired AWS region
    ),
)

app.synth()

# aws ecr get-login-password --region "us-east-1" | docker login --username AWS --password-stdin "522117021059.dkr.ecr.us-east-1.amazonaws.com"
# cdk bootstrap aws://547423740268/us-east-1

# aws configure --profile 547423740268
# cdk bootstrap --profile 547423740268 aws://547423740268/region
