# aws-acm-certificate/validation_records Terraform Module

This module creates ACM validation records in Route53 hosted zones.
This should be used when the ACM certificate is in a different account to the Route53 Hosted Zone.

## Input variables

### `names`

- Type: map(string)
- Required

The names to create validation records for and their Route53 hosted zones.

The hosted zone ids to create validation records in. The keys of the map are the FQDNs and the values are the Route53 Hosted Zone ids.

### `certificate`

- Type: aws_acm_certificate
- Required

The certificate resource to validate. Should be the `certificate` output from the aws-acm-certificate module.

## Examples

See the [acm-certificate](../../) module for examples.
