variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
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
