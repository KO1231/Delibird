data "archive_file" "redirect_request" {
  type        = "zip"
  source_dir  = "../../lambda/redirect_request"
  output_path = "${path.root}/.build/redirect_request.zip"
}

resource "aws_lambda_function" "redirect_request" {
  function_name = "Delibird-${var.environment}-RedirectRequestFunction"
  role          = aws_iam_role.lambda_redirect_request.arn
  handler       = "app.lambda_handler"
  runtime       = var.runtime
  timeout       = var.timeout
  memory_size   = var.memory_size
  architectures = var.architectures
  layers        = [aws_lambda_layer_version.common.arn]

  filename         = data.archive_file.redirect_request.output_path
  source_code_hash = data.archive_file.redirect_request.output_base64sha256

  environment {
    variables = {
      DELIBIRD_ENV = var.environment
    }
  }

  tracing_config {
    mode = "Active"
  }

  logging_config {
    log_format = "JSON"
  }
}
