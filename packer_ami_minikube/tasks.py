from invoke import task
import terraform_vpc_packer
import os


@task(pre=[terraform_vpc_packer.initialize])
def build(context):
    """
    Build the AMI Minikube.
    """

    config = context.config.packer_ami_minikube
    working_dir = os.path.normpath(config.working_dir)
    bin_packer = os.path.normpath(os.path.join(config.bin_dir, 'packer.exe'))

    with terraform_vpc_packer.vpc_packer(context=context) as vpc_packer_output:
        with context.cd(working_dir):
            print('Building AMI Minikube')

            # Build twice, for each of amd64 and arm64
            # TODO: "arm64" not supported pending Minikube docker driver
            #       https://minikube.sigs.k8s.io/docs/drivers/docker/
            variables = [
                {
                    'ami_architecture': 'amd64',
                    'aws_instance_type': 't3.medium',
                },
                # {
                #     'ami_architecture': 'arm64',
                #     'aws_instance_type': 't4g.medium',
                # }
            ]

            for variables_current in variables:
                context.run(
                    command=' '.join([
                        bin_packer,
                        'build',
                        '-color=false',
                        '-var "ami_architecture={}"'.format(variables_current['ami_architecture']),
                        '-var "aws_instance_type={}"'.format(variables_current['aws_instance_type']),
                        '-var "vpc_packer_vpc_id={}"'.format(vpc_packer_output.vpc_id),
                        '-var "vpc_packer_subnet_id={}"'.format(vpc_packer_output.subnet_id),
                        '.'
                    ])
                )