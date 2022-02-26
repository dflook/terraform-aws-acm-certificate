provider "aws" {}

data "aws_route53_zone" "example_com" {
  name = "example.com."
}

data "aws_route53_zone" "example_org" {
  name = "example.org."
}

module "certificate" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "hello.example.com" : data.aws_route53_zone.example_com.zone_id
  }
}

module "tags" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "world.example.com" : data.aws_route53_zone.example_com.zone_id
  }

  tags = {
    "Example" : "tags"
  }
}

module "multiple_names" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "abc.example.com" : data.aws_route53_zone.example_com.zone_id
    "xyz.example.com" : data.aws_route53_zone.example_com.zone_id
  }
}

module "explicit_common_name" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  common_name = "yuiop.example.com"

  names = {
    "qwert.example.com" : data.aws_route53_zone.example_com.zone_id
    "yuiop.example.com" : data.aws_route53_zone.example_com.zone_id
  }
}

module "multiple_zones" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "foo.example.com" : data.aws_route53_zone.example_com.zone_id
    "bar.example.org" : data.aws_route53_zone.example_org.zone_id
  }
}

module "wildcard" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "example.com" : data.aws_route53_zone.example_com.zone_id
    "*.example.com" : data.aws_route53_zone.example_com.zone_id
  }
}
