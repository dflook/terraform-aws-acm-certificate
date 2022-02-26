output "arn" {
  description = "The ARN of the certificate. By default this is available once the certificate is issued and ready to use. If `wait_for_validation` is false, it is available immediately after resource creation but possibly before being issued."
  value       = var.wait_for_validation ? aws_acm_certificate_validation.validation[0].certificate_arn : aws_acm_certificate.certificate.arn
}

output "common_name" {
  description = "The CN of the certificate."
  value       = aws_acm_certificate.certificate.domain_name
}

output "certificate" {
  description = "The underlying aws_acm_certificate resource."
  value       = aws_acm_certificate.certificate
}
