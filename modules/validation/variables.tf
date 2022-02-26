variable "names" {
  type        = map(string)
  description = "A map of names to create validation records for. Keys are domain names, values are hosted zone ids to create validation records in."
}

variable "certificate" {
  type        = any
  description = "The certificate resource to validate. Should be the `certificate` output from an aws-acm-certificate module."
}
