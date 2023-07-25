from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_docdb as docdb,
    aws_secretsmanager as secretsmanager,
)

from constructs import Construct
from aws_cdk import Stack
import json


class FastAPIStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(self, "MyVPC", max_azs=2)

        self.ecs_cluster = ecs.Cluster(self, "MyECSCluster", vpc=self.vpc)

        image = ecs.ContainerImage.from_asset(directory="..")

        # Create a security group

        self.sg = ec2.SecurityGroup(
            self,
            "MySecurityGroup",
            vpc=self.vpc,
            description="My security group",
            allow_all_outbound=True,  # Allow outbound traffic by default
        )

        # Allow inbound traffic on specific port (27017 here for DocumentDB)
        self.sg.add_ingress_rule(
            peer=self.sg,  # Only allow traffic from instances within the same security group
            connection=ec2.Port.tcp(27017),
            description="Allow inbound traffic on port 27017",
        )

        docdb_secret = secretsmanager.Secret(
            self,
            "DocDBSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"username": "myuser"}),
                generate_string_key="password",
            ),
        )

        # Create a DocumentDB subnet group
        docdb_subnet_group = docdb.CfnDBSubnetGroup(
            self,
            "MyDBSubnetGroup",
            db_subnet_group_description="Subnet group for DocumentDB cluster",
            subnet_ids=self.vpc.select_subnets(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
            ).subnet_ids,
        )

        # Add the dependency
        docdb_subnet_group.node.add_dependency(self.vpc)

        # self.docdb_cluster = docdb.CfnDBCluster(
        #     self,
        #     "MyDocDBCluster",
        #     master_username=docdb_secret.secret_value_from_json(
        #         "username"
        #     ).to_string(),
        #     master_user_password=docdb_secret.secret_value_from_json(
        #         "password"
        #     ).to_string(),
        #     db_cluster_identifier="mydbcluster",
        #     vpc_security_group_ids=[self.sg.security_group_id],
        #     db_subnet_group_name=docdb_subnet_group.db_subnet_group_name,
        #     port=27017,
        # )

        # self.docdb_cluster.node.add_dependency(docdb_subnet_group)

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

        # self.ecs_service.node.add_dependency(self.docdb_cluster)

        self.ecs_service.task_definition.add_container(
            "FastAPIContainer",
            image=image,
            environment={
                # "DB_HOST": self.docdb_cluster.attr_endpoint,
                # "DB_PORT": str(self.docdb_cluster.port),
                "DB_NAME": "my_db",
                "DB_USER": docdb_secret.secret_value_from_json(
                    "username"
                ).to_string(),
                "DB_PASSWORD": docdb_secret.secret_value_from_json(
                    "password"
                ).to_string(),
            },
        )

        # self.ecs_service.service.connections.security_groups.append(self.sg)
