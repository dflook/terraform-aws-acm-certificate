# aws-acm-certificate Terraform Module

This module creates an ACM issued DNS validated certificate.
It supports automatically creating the required validation records where the zone is hosted by Route53.

The [validation submodule](modules/validation) can be used with this resource to create the validation records in a Route53 Hosted Zone in another AWS account.

This module can also be used to create certificates that include names that can't have their validation records automatically created.

## Input variables

### `names`

- Type: map(string)
- Required

The names to include in the issued certificate, and their Route53 hosted zones to create the validation records.

The input is a map where the keys are the names to include in the certificate. The value for each key is the Hosted Zone id to create the validation record.
If the value for a key is `null`, the validation record is not created.

### `common_name`

- Type: string
- Optional

The name to use as the Common Name of the issued certificate. If specified, this must be present in the `names` map. If not specified, one of the names in the `names` map is used.
This makes some cosmetic difference to how the certificate is presented in some clients/browsers. All `names` are included in the certificate as Subject Alternative Names.
Validating certificates based on the common name has been deprecated for a long time.

### `tags`

- Type: map(string)
- Optional

Tags to add to the certificate resource.

### `wait_for_validation`

- Type: bool
- Optional, Default: true

When true, wait until the certificate is validated before the `arn` output is available.
This can be set to false if some of the names in the certificate can't have their validation records automatically added by this module.

## Output

### `arn`

- Type: string

The ARN of the certificate. When `validate` is true, the certificate will have been issued.
When `validate` is false, the certificate may not have been issued yet.

### `common_name`

- Type: string

The Common Name (CN) of the certificate.

### `certificate`

- Type: `aws_acm_certificate`

The underlying [aws_acm_certificate](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate) resource. 
This should be passed to the `validation` submodule if needed to create validation records using a different AWS provider, such as when using a Route53 zone in another account.

The `domain_validation_options` attribute could also be used to create validation records in other DNS providers.

## Examples

See the full [examples](examples/) for more.

### A single name

This example creates a certificate for a single name.
The Hosted Zone id is provided, so the certificate is automatically validated and issued.

The `arn` output is available once the certificate is ready to use.

```hcl
module "certificate" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"

  names = {
    "hello.example.com" : data.aws_route53_zone.example_com.zone_id
  }
}
```

### Certificate with names from multiple Hosted Zones

This creates a certificate that includes the names:
  - `example.com`
  - a wildcard for subdomains of `example.com`
  - `hello.example.org`, which is a separate Hosted Zone in the same account

This also explicitly sets which of the names should be the Common Name of the certificate.

```hcl
module "certificate" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"

  common_name = "hello.example.org"
  
  names = {
    "example.com" : data.aws_route53_zone.example_com.zone_id
    "*.example.com" : data.aws_route53_zone.example_com.zone_id

    "hello.example.org" : data.aws_route53_zone.example_org.zone_id
  }
}
```

### Certificate with names from multiple Hosted Zones in multiple AWS accounts

This creates a certificate that includes a name that belongs to a Hosted Zone in another AWS account.
The additional name must be in the `names` input variable with the zone id set to `null`, which prevents the module from trying to create the validation record itself.

You can use the `validation` submodule to create the validation records in the other account by passing in an aws provider configured for the correct account.

```hcl
module "my_cert" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"

  common_name = "example.org"
  
  names = {
    "example.com" : data.aws_route53_zone.example_com.zone_id
    "example.org" : null
  }
}

module "certificate_validate_second_zone" {
  source = "github.com/dflook/terraform-aws-acm-certificate//modules/validation?ref=1.0.0"

  providers = {
    aws = aws.account-2
  }

  certificate = module.my_cert.certificate

  names = {
    "example.org" : data.aws_route53_zone.example_org.zone_id
  }
}
```

### Certificate that is not validated

This creates a certificate that can't yet be validated and issued. Perhaps the DNS zone is managed manually and not using terraform.

The validation record is created in the provided Hosted Zone but we can't create the validation record for the second zone.
By setting `wait_for_validation` to `false`, terraform finished as soon as the certificate is created (but not yet validated or issued).

The `domain_validation_options` output shows the validation records that need to be created.
Soon after the validation records have been created for the second zone, the certificate will be validated and ready to use.

```hcl
module "my_cert" {
  source = "github.com/dflook/terraform-aws-acm-certificate?ref=1.0.0"
  
  wait_for_validation = false
  
  names = {
    "example.com" : data.aws_route53_zone.example_com.zone_id    
    "example.org" : null
  }
}

output "domain_validation_options" {
  value = module.my_cert.certificate.domain_validation_options
}
```
