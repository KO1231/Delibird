data "archive_file" "redirect_request" {
  type        = "zip"
  source_dir  = "${path.root}/../../lambda/redirect_request"
  output_path = "${path.root}/.build/redirect_request.zip"
}

data "archive_file" "admin_portal" {
  type        = "zip"
  source_dir  = "${path.root}/../../lambda/admin_portal"
  output_path = "${path.root}/.build/admin_portal.zip"
}

resource "aws_lambda_function" "redirect_request" {
  function_name                  = "Delibird-${var.environment}-RedirectRequestFunction"
  role                           = var.role_redirect_request.arn
  handler                        = "app.lambda_handler"
  runtime                        = var.runtime
  timeout                        = var.timeout
  memory_size                    = var.memory_size
  architectures                  = var.architectures
  reserved_concurrent_executions = var.reserved_concurrent_executions
  layers                         = [aws_lambda_layer_version.common.arn]

  filename         = data.archive_file.redirect_request.output_path
  source_code_hash = data.archive_file.redirect_request.output_base64sha256

  environment {
    variables = {
      DELIBIRD_ENV           = var.environment
      ENV_VAR                = var.environment_var
      LINK_TABLE_NAME        = var.ddb_link_table.name
      STATIC_RESOURCE_DIR    = "/opt/delibird/static"
      ALLOWED_DOMAIN         = join(",", var.allowed_domain)
      MAX_QUERY_KEY_LENGTH   = "100"
      MAX_QUERY_VALUE_LENGTH = "2000"
      MAX_TOTAL_QUERY_PARAMS = "50"
    }
  }

  tracing_config {
    mode = "Active"
  }

  logging_config {
    log_format = "JSON"
  }
}

resource "aws_lambda_function" "admin_portal" {
  function_name                  = "Delibird-${var.environment}-AdminPortalFunction"
  role                           = var.role_admin_portal.arn
  handler                        = "app.lambda_handler"
  runtime                        = var.runtime
  timeout                        = var.timeout
  memory_size                    = var.memory_size
  architectures                  = var.architectures
  reserved_concurrent_executions = var.reserved_concurrent_executions
  layers                         = [aws_lambda_layer_version.common.arn]

  filename         = data.archive_file.admin_portal.output_path
  source_code_hash = data.archive_file.admin_portal.output_base64sha256

  environment {
    variables = {
      DELIBIRD_ENV        = var.environment
      ENV_VAR             = var.environment_var
      LINK_TABLE_NAME     = var.ddb_link_table.name
      STATIC_RESOURCE_DIR = "/opt/delibird/static"
      ALLOWED_DOMAIN      = join(",", var.allowed_domain)
    }
  }

  tracing_config {
    mode = "Active"
  }

  logging_config {
    log_format = "JSON"
  }
}
