from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs, 
    aws_ssm as ssm,
    aws_secretsmanager as sm,
    aws_logs as logs,
    aws_ecs_patterns as ecs_patterns,
    Duration,
    Stack,
)
from constructs import Construct

class BdswissChallengeEcsStack(Stack):


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # get string from SSM
        interval = ssm.StringParameter.value_for_string_parameter(self, "INTERVAL")

        # get usename/password from Secret Manager
        secret = sm.Secret.from_secret_name_v2(self, "ChallengeECS", "ChallengeECS")
        
        # build container image 
        container_image = ecs.ContainerImage.from_asset("./code/")

        # Create a VPC
        vpc = ec2.Vpc(
            self, "ChallengeEcsVpc",
            max_azs=2,
            vpc_name="ChallengeEcsVpc"
        )
        
        # create ECS Cluster 
        cluster = ecs.Cluster(
            self, 'ChallengeEcsCluster',
            vpc=vpc
        )
        
        # create worker task
        worker_task = ecs.FargateTaskDefinition(
            self, "Worker", 
            memory_limit_mib=512, 
            cpu=256
        )
        
        # create server task
        server_task = ecs.FargateTaskDefinition(
            self, "Server", 
            memory_limit_mib=512, 
            cpu=256
        )
        
        # add container for worker
        worker_task.add_container("Worker",
            image=container_image, 
            container_name="Worker",
            environment={"INTERVAL": interval},
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="WorkerLogs",
                log_retention=logs.RetentionDays.ONE_WEEK,
            )
        )
        
        # add container for server
        server_container = server_task.add_container("Server",
            image=container_image, 
            container_name="Server",
            environment={"PORT": "80"},
            secrets={
                "USERNAME": ecs.Secret.from_secrets_manager(secret, "USERNAME"),
                "PASSWORD": ecs.Secret.from_secrets_manager(secret, "PASSWORD")
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="ServerLogs",
                log_retention=logs.RetentionDays.ONE_WEEK,
            )
        )
        
        # add port mapping for server
        server_container.add_port_mappings(
            ecs.PortMapping(container_port=80)
        )


        # create Worker Service
        worker_service = ecs.FargateService(
            self, "ChallengeWorker", 
            service_name="ChallengeWorker",
            cluster=cluster, 
            task_definition=worker_task,
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True)
            #deployment_controller
        )

        # create Server Service
        server_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ChallengeServer",
            service_name="ChallengeServer",
            load_balancer_name="ChallengeServer",
            cluster=cluster,
            task_definition=server_task,
            listener_port=80,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True)
            #deployment_controller
        )

        # add healthcheck
        server_service.target_group.configure_health_check(
            path="/health"
        )

        # Add security rule
        server_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
        
        # add auto scale  for server   
        scalable_target_server = server_service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=50
        )

        scalable_target_server.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=60,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        
        scalable_target_server.scale_on_memory_utilization(
            "MemoryScaling",
            target_utilization_percent=60,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )