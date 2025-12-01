resource "aws_iam_role" "apigateway" {
  name = "DelibirdAPIGatewayRole-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      },
    ]
  })
}


# Inline Policy
resource "aws_iam_role_policy" "invoke_lambda_redirect_request" {
  role = aws_iam_role.apigateway.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
        ]
        Resource = [
          var.lambda_redirect_request.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "invoke_lambda_admin_portal" {
  role = aws_iam_role.apigateway.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction",
        ]
        Resource = [
          var.lambda_admin_portal.arn
        ]
      }
    ]
  })
}
