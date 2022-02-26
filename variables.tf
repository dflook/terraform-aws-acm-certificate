variable "common_name" {
  type        = string
  description = "The name to use as the Common Name (CN) of the certificate. If not specified, one of the name in the `names` variable is used as the CN."
  default     = ""
}

variable "names" {
  type        = map(string)
  description = "A map of names to add to the certificate. Keys are Fully Qualified Domain Names, values are Hosted Zone ids to create the validation records in. Use null as the value to skip creating the validation record for that name."
}

variable "wait_for_validation" {
  type        = bool
  description = "If the certificate should be validated and issued before the `arn` output is available."
  default     = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
