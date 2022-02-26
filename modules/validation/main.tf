resource "aws_route53_record" "validation" {
  for_each = {
    for record in var.certificate.domain_validation_options : record.domain_name => {
      name    = record.resource_record_name
      record  = record.resource_record_value
      type    = record.resource_record_type
      zone_id = var.names[record.domain_name]
    } if lookup(var.names, record.domain_name, null) != null
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = each.value.zone_id
}
