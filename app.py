#!/usr/bin/env python3
import os
import aws_cdk as cdk

from cdk_workshop.cdk_workshop_stack import DevOpsStack


app = cdk.App()
DevOpsStack(app, "cdk-workshop",
  env={
    'account': os.environ['CDK_DEFAULT_ACCOUNT'], 
    'region': os.environ['CDK_DEFAULT_REGION']
  })

app.synth()
