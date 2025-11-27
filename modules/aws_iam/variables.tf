variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "ddb_link_table" {
  type = object({
    name = string
    arn  = string
  })
}

variable "lambda_redirect_request" {
  type = object({
    name = string
    arn  = string
  })
}
