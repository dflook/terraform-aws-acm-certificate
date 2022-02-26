provider "aws" {}
provider "google" {}

data "aws_route53_zone" "example_com" {
  name = "example.com."
}

module "my_cert" {
  source = "dflook/acm-certificate/aws"
  version = "1.0.0"

  names = {
    "abc.example.com" : data.aws_route53_zone.example_com.zone_id
    "xyz.example.org" : null
  }
}

resource "google_dns_record_set" "certificate_validate_second_zone" {
  for_each = module.my_cert.certificate.domain_validation_options

  managed_zone = "example-org"

  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  rrdatas = [each.value.record]
}
