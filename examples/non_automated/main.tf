provider "aws" {}

data "aws_route53_zone" "example_com" {
  name = "example.com."
}

module "my_cert" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"

  names = {
    "abc.example.com" : data.aws_route53_zone.example_com.zone_id
    "xyz.example.com" : null
  }

  wait_for_validation = false
}

output "domain_validation_options" {
  value = module.my_cert.certificate.domain_validation_options
}
