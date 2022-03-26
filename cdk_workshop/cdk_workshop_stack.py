# from tkinter.tix import INTEGER
import aws_cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_logs as logs,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_secretsmanager as sm,

)

from aws_cdk.aws_ecr_assets import DockerImageAsset
from os import path



class DevOpsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "SampleVPC", max_azs=1)

        cluster = ecs.Cluster(self, "ServiceCluster", vpc=vpc)

        # int_param = ssm.StringParameter(self, "Parameter",
        #     allowed_pattern=".*",
        #     parameter_name="INTERVAL",
        #     string_value="5002",
        #     tier=ssm.ParameterTier.ADVANCED
        # )



        interval_value = ssm.StringParameter.value_from_lookup(self, "INTERVAL")
 

        secret = sm.Secret.from_secret_complete_arn(self, "ImportedSecret",
            secret_complete_arn="arn:aws:secretsmanager:eu-west-3:306119897415:secret:server_secret-zjpEcH",
            # If the secret is encrypted using a KMS-hosted CMK, either import or reference that key:
            # encryption_key="DefaultEncryptionKey"
        )

        worker_task = ecs.FargateTaskDefinition(
            self, "worker", memory_limit_mib=512,
        )

        worker_task.add_container(
            "worker",
            image=ecs.ContainerImage.from_asset('./devops-challenge'),
            essential=True,
            environment={"INSTANCE": "WORKER", "INTERVAL": interval_value},
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="WorkerContainer",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
        ).add_port_mappings(ecs.PortMapping(container_port=6001, host_port=6001))

        worker_service = aws_cdk.aws_ecs_patterns.NetworkLoadBalancedFargateService(
            self, id="fworker-service",
            cluster=cluster,
            service_name="worker",
            desired_count=1, 
            task_definition=worker_task,
        )

        worker_service.service.auto_scale_task_count(min_capacity=1,max_capacity=1)

        server_task = ecs.FargateTaskDefinition(
            self, "server-task", memory_limit_mib=512,
        )

        server_task.add_container(
            "server",
            image=ecs.ContainerImage.from_asset('./devops-challenge'),
            essential=True,
            secrets={"USERNAME": ecs.Secret.from_secrets_manager(secret)},
            environment={"PORT": "6006"},
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="ServerContainer",
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
        ).add_port_mappings(ecs.PortMapping(container_port=6006, host_port=6006))





        server_service = aws_cdk.aws_ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            id="server-service",
            service_name="server",
            cluster=cluster,  
            task_definition=server_task,
            listener_port=80,
            public_load_balancer=True,
        )


        server_service.service.connections.allow_from_any_ipv4(
            ec2.Port.tcp(6006), "health_check"
            )
        server_service.service.auto_scale_task_count(max_capacity=3,min_capacity=2)







        # backend_service.service.connections.allow_from(
        #     front_service.service, ec2.Port.tcp(6006)
        # )

        # Add capacity to it
        # cluster.add_capacity("DefaultAutoScalingGroupCapacity",
        #     instance_type=ec2.InstanceType("t3.micro"),
        #     desired_capacity=1
        # )



###follow_symlinks=cdk.SymlinkFollowMode.ALWAYS,),      #from_registry("asset.image_uri"),
