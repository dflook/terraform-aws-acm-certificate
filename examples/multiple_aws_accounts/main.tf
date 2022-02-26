provider "aws" {
  profile = "account-1"
  region  = "eu-west-1"
}

provider "aws" {
  alias   = "account-2"
  profile = "account-2"
  region  = "eu-west-1"
}

data "aws_route53_zone" "example_com" {
  name = "example.com."
}

data "aws_route53_zone" "example_org" {
  provider = aws.account-2
  name     = "example.org."
}

module "certificate" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"

  names = {
    "abc.example.com" : data.aws_route53_zone.example_com.zone_id
    "xyz.example.org" : null
  }
}

module "certificate_validate_second_zone" {
  source = "github.com/dflook/terraform-aws-acm-certificate//modules/validation?ref=1.0.0"

  providers = {
    aws = aws.account-2
  }

  certificate = module.certificate.certificate

  names = {
    "xyz.example.org" : data.aws_route53_zone.example_org.zone_id
  }
}
