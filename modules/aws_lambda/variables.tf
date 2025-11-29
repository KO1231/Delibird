variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "environment_var" {
  type = string
}

variable "runtime" {
  description = "Lambda runtime version"
  type        = string
}

variable "architectures" {
  description = "Lambda architectures"
  type        = list(string)
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
}

variable "memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
}

variable "ddb_link_table" {
  type = object({
    name = string
    arn  = string
  })
}

variable "role_redirect_request" {
  type = object({
    name = string
    arn  = string
  })
}

variable "role_admin_portal" {
  type = object({
    name = string
    arn  = string
  })
}

variable "allowed_domain" {
  description = "Allowed domain for the Lambda function"
  type        = list(string)
}

variable "reserved_concurrent_executions" {
  description = "Reserved concurrent executions for Lambda function (for cost and DDoS protection)"
  type        = number
}
