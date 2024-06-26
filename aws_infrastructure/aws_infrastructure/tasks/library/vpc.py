from aws_infrastructure.tasks import compose_collection
import aws_infrastructure.tasks.library.terraform
from collections import namedtuple
from invoke import Collection
from pathlib import Path
from typing import List
from typing import Union


def create_tasks(
    *,
    config_key: str,
    terraform_bin: Union[Path, str],
    terraform_dir: Union[Path, str],
):
    """
    Create all of the tasks, re-using and passing parameters appropriately.
    """

    terraform_bin = Path(terraform_bin)
    terraform_dir = Path(terraform_dir)

    ns_vpc = Collection('vpc')

    ns_terraform = aws_infrastructure.tasks.library.terraform.create_tasks(
        config_key=config_key,
        terraform_bin=terraform_bin,
        terraform_dir=terraform_dir,
        auto_approve=False,
        output_tuple_factory=namedtuple(
            'vpc',
            [
                'vpc_id',
                'default_security_group_id',
                'availability_zone_subnet_ids',
                'subnet_ids',
                'subnet_id',
            ]
        ),
    )

    compose_collection(
        ns_vpc,
        ns_terraform,
        sub=False
    )

    return ns_vpc


def create_vpc_read_only(
    ns_vpc: Collection,
):
    """
    Create a read only context manager.
    """

    vpc_read_only = aws_infrastructure.tasks.library.terraform.create_context_manager_read_only(
        init=ns_vpc.tasks['init'],
        output=ns_vpc.tasks['output'],
    )

    return vpc_read_only
