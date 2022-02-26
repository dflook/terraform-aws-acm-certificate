This example creates a certificate where one of the names can't have the validation record created as part of the terraform plan.
Perhaps the DNS zone is controlled by a third party.

The `wait_for_issuance` input variable is set to `false` so the certificate resource is created and the ARN made available through the `arn` output before the certificate is issued.
The `domain_validation_options` output contains the validation records that still need to be created for the certificate to be issued.

```hcl
provider "aws" {}

data "aws_route53_zone" "example_com" {
  name = "example.com."
}

module "my_cert" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "abc.example.com" : data.aws_route53_zone.example_com.zone_id
    "xyz.example.com" : null
  }

  wait_for_validation = false
}

output "domain_validation_options" {
  value = module.my_cert.certificate.domain_validation_options
}
```
