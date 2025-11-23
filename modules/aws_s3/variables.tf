variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
}

variable "bucket_name" {
  type = string
}

variable "remote_base_path" {
  type = string
}

locals {
  local_base_path = "${path.root}/../../s3"
}
