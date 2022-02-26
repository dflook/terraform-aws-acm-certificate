import os
import random
import shutil
import string
import time

import boto3

import pytest
from download import get_executable, terraform_exec

TERRAFORM_VERSIONS=['0.12.20', '1.1.6']
AWS_PROVIDER_VERSIONS=['3.0.0', '4.2.0']

FIRST_ZONE_NAME=os.environ['TEST_FIRST_ZONE_NAME']
FIRST_ZONE_ID=os.environ['TEST_FIRST_ZONE_ID']
SECOND_ZONE_NAME=os.environ['TEST_SECOND_ZONE_NAME']
SECOND_ZONE_ID=os.environ['TEST_SECOND_ZONE_ID']

acm = boto3.client('acm', region_name='eu-west-1')
route53 = boto3.client('route53', region_name='eu-west-1')

def random_prefix() -> str:
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(6))


@pytest.mark.parametrize("aws_provider_version", ['4.2.0'])
@pytest.mark.parametrize("terraform_version", ['1.1.6'])
def test_validation(terraform_version, aws_provider_version):
    terraform_path = get_executable(terraform_version)

    workdir = f'.terraform-module/validation_{terraform_version}_{aws_provider_version}'

    first_zone_prefix = random_prefix()

    module = f'''
terraform {{
  required_version= "{terraform_version}"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "{aws_provider_version}"
    }}
  }}
}}

provider "aws" {{
  region = "eu-west-1"
}}

module certificate {{
  source = "../../../"

  common_name = "{first_zone_prefix}.{FIRST_ZONE_NAME}"

  names = {{
    "{first_zone_prefix}.{FIRST_ZONE_NAME}": "{FIRST_ZONE_ID}"
  }}

  tags = {{
    "my_cert" = "{first_zone_prefix}"
  }}
}}

output certificate_arn {{
  value = module.certificate.arn
}}
    '''

    print(terraform_exec(workdir, terraform_path, ['init'], module))
    print(terraform_exec(workdir, terraform_path, ['apply', '-auto-approve'], module))
    print(terraform_exec(workdir, terraform_path, ['plan', '-detailed-exitcode'], module))

    # Check the certificate resource
    certificate_arn = terraform_exec(workdir, terraform_path, ['output', 'certificate_arn'], module).strip(' "\n')
    assert certificate_arn.startswith('arn:aws:acm:')
    certificate = acm.describe_certificate(CertificateArn=certificate_arn)['Certificate']
    print(certificate)
    assert certificate['DomainName'] == f'{first_zone_prefix}.{FIRST_ZONE_NAME}'
    assert certificate['SubjectAlternativeNames'] == [f'{first_zone_prefix}.{FIRST_ZONE_NAME}']
    assert certificate['Status'] == 'ISSUED'

    tags = {tag['Key']: tag['Value'] for tag in acm.list_tags_for_certificate(CertificateArn=certificate_arn)['Tags']}

    assert tags['my_cert'] == f'{first_zone_prefix}'

    print(terraform_exec(workdir, terraform_path, ['destroy', '-auto-approve'], module))


@pytest.mark.parametrize("aws_provider_version", AWS_PROVIDER_VERSIONS)
@pytest.mark.parametrize("terraform_version", TERRAFORM_VERSIONS)
def test_secondary_validate(terraform_version, aws_provider_version):
    if terraform_version == '0.12.20' and aws_provider_version == '4.2.0':
        pytest.skip('Invalid version combination')

    terraform_path = get_executable(terraform_version)

    workdir = f'.terraform-module/external_validate_{terraform_version}_{aws_provider_version}'

    first_zone_prefix = random_prefix()
    second_zone_prefix = random_prefix()

    module = f'''
terraform {{
  required_version= "{terraform_version}"
  
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "{aws_provider_version}"
    }}
  }}
}}

provider "aws" {{
  region = "eu-west-1"
}}

module certificate {{
  source = "../../../"
  
  common_name = "{first_zone_prefix}.{FIRST_ZONE_NAME}"
  
  names = {{
    "{first_zone_prefix}.{FIRST_ZONE_NAME}": "{FIRST_ZONE_ID}"
    "{second_zone_prefix}.{SECOND_ZONE_NAME}": null
  }}
  
  tags = {{
    "my_cert" = "{first_zone_prefix}{second_zone_prefix}"
  }}
}}

module certificate_validation {{
  source = "../../../modules/validation"

  names = {{
    "{second_zone_prefix}.{SECOND_ZONE_NAME}": "{SECOND_ZONE_ID}"
  }}

  certificate = module.certificate.certificate
}}

output certificate_arn {{
  value = module.certificate.arn
}}
    '''

    print(terraform_exec(workdir, terraform_path, ['init'], module))
    print(terraform_exec(workdir, terraform_path, ['apply', '-auto-approve'], module))
    print(terraform_exec(workdir, terraform_path, ['plan', '-detailed-exitcode'], module))

    # Check the certificate resource
    certificate_arn = terraform_exec(workdir, terraform_path, ['output', 'certificate_arn'], module).strip(' "\n')
    assert certificate_arn.startswith('arn:aws:acm:')
    certificate = acm.describe_certificate(CertificateArn=certificate_arn)['Certificate']
    print(certificate)
    assert certificate['DomainName'] == f'{first_zone_prefix}.{FIRST_ZONE_NAME}'
    assert certificate['SubjectAlternativeNames'] == [f'{first_zone_prefix}.{FIRST_ZONE_NAME}', f'{second_zone_prefix}.{SECOND_ZONE_NAME}']
    assert certificate['Status'] == 'ISSUED'

    tags = {tag['Key']: tag['Value'] for tag in acm.list_tags_for_certificate(CertificateArn=certificate_arn)['Tags']}

    assert tags['my_cert'] == f'{first_zone_prefix}{second_zone_prefix}'

    print(terraform_exec(workdir, terraform_path, ['destroy', '-auto-approve'], module))

@pytest.mark.parametrize("aws_provider_version", ['4.2.0'])
@pytest.mark.parametrize("terraform_version", ['1.1.6'])
def test_no_wait_for_validation(terraform_version, aws_provider_version):
    terraform_path = get_executable(terraform_version)

    workdir = f'.terraform-module/wait_for_validation_{terraform_version}_{aws_provider_version}'

    first_zone_prefix = random_prefix()

    module = f'''
terraform {{
  required_version= "{terraform_version}"

  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "{aws_provider_version}"
    }}
  }}
}}

provider "aws" {{
  region = "eu-west-1"
}}

module certificate {{
  source = "../../../"

  names = {{
    "{first_zone_prefix}.{FIRST_ZONE_NAME}": null
  }}
  
  wait_for_validation = false

  tags = {{
    "my_cert" = "{first_zone_prefix}"
  }}
}}

output certificate_arn {{
  value = module.certificate.arn
}}
    '''

    print(terraform_exec(workdir, terraform_path, ['init'], module))
    print(terraform_exec(workdir, terraform_path, ['apply', '-auto-approve'], module))
    print(terraform_exec(workdir, terraform_path, ['plan', '-detailed-exitcode'], module))

    # Check the certificate resource
    certificate_arn = terraform_exec(workdir, terraform_path, ['output', 'certificate_arn'], module).strip(' "\n')
    assert certificate_arn.startswith('arn:aws:acm:')
    certificate = acm.describe_certificate(CertificateArn=certificate_arn)['Certificate']
    print(certificate)
    assert certificate['DomainName'] == f'{first_zone_prefix}.{FIRST_ZONE_NAME}'
    assert certificate['SubjectAlternativeNames'] == [f'{first_zone_prefix}.{FIRST_ZONE_NAME}']
    assert certificate['Status'] == 'PENDING_VALIDATION'

    tags = {tag['Key']: tag['Value'] for tag in acm.list_tags_for_certificate(CertificateArn=certificate_arn)['Tags']}

    assert tags['my_cert'] == f'{first_zone_prefix}'

    print(terraform_exec(workdir, terraform_path, ['destroy', '-auto-approve'], module))
