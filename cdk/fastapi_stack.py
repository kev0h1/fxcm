from aws_cdk import core, aws_secretsmanager as secretsmanager
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_docdb as docdb,
)
from aws_cdk.aws_iam import PolicyStatement, Effect
import json


class FastAPIStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # (i) Create VPC
        self.vpc = ec2.Vpc(self, "MyVPC", max_azs=3)

        # (ii) Create Fargate Cluster
        self.ecs_cluster = ecs.Cluster(self, "MyECSCluster", vpc=self.vpc)

        # (iii) Define Docker image for the Service
        image = ecs.ContainerImage.from_asset(directory="..")

        # (iv) Create DocumentDB Cluster
        # Create a secret
        docdb_secret = secretsmanager.Secret(
            self,
            "DocDBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "myuser"}),
                generate_string_key="password",
            ),
        )

        self.docdb_cluster = docdb.CfnDBCluster(
            self,
            "MyDocDBCluster",
            master_username=docdb_secret.secret_value_from_json(
                "username"
            ).to_string(),
            master_user_password=docdb_secret.secret_value_from_json(
                "password"
            ).to_string(),
            db_cluster_identifier="mydbcluster",
            vpc_security_group_ids=["sg-1234567890abcdef0"],
            db_subnet_group_name="mydbsubnetgroup",
            port=27017,
        )

        # (v) Create Fargate Service and ALB
        self.ecs_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FastAPIService",
            cluster=self.ecs_cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image
            ),
            public_load_balancer=True,
        )

        # (vi) Add environment variables to Fargate service task definition
        self.ecs_service.task_definition.add_container(
            "FastAPIContainer",
            image=image,
            environment={
                "DB_HOST": self.docdb_cluster.attr_endpoint,
                "DB_PORT": str(self.docdb_cluster.port),
                "DB_NAME": "my_db",
                "DB_USER": docdb_secret.secret_value_from_json(
                    "username"
                ).to_string(),
                "DB_PASSWORD": docdb_secret.secret_value_from_json(
                    "password"
                ).to_string(),
            },
        )
