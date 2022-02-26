resource "aws_acm_certificate" "certificate" {
  domain_name = local.common_name

  subject_alternative_names = [for name in local.names : name if name != local.common_name]

  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = var.tags
}

locals {
  names       = keys(var.names)
  common_name = var.common_name != "" ? var.common_name : local.names[0]
}

resource "aws_route53_record" "validation" {
  for_each = {
    for record in aws_acm_certificate.certificate.domain_validation_options : record.domain_name => {
      name    = record.resource_record_name
      record  = record.resource_record_value
      type    = record.resource_record_type
      zone_id = var.names[record.domain_name]
    } if var.names[record.domain_name] != null
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = each.value.zone_id
}

resource "aws_acm_certificate_validation" "validation" {
  count = var.wait_for_validation ? 1 : 0

  certificate_arn         = aws_acm_certificate.certificate.arn
  validation_record_fqdns = length(var.names) == length([for hosted_zone in var.names : hosted_zone if hosted_zone != null]) ? [for record in aws_route53_record.validation : record.fqdn] : null
}
