resource "aws_iam_role" "lambda_redirect_request" {
  name = "DelibirdLambdaRedirectRequestRole-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Inline Policy
resource "aws_iam_role_policy" "lambda_redirect_request" {
  role = aws_iam_role.lambda_redirect_request.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
        ]
        Resource = [
          var.ddb_link_table.arn,
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:UpdateItem",
        ]
        Resource = [
          var.ddb_link_table.arn,
        ]
        Condition = {
          "ForAllValues:StringEquals" = {
            "dynamodb:Attributes" = [
              "domain",
              "slug",
              "uses",
              "max_uses",
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
        ]
        Resource = [
          var.ddb_link_nonce_table.arn,
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:UpdateItem",
        ]
        Resource = [
          var.ddb_link_nonce_table.arn,
        ]
        Condition = {
          "ForAllValues:StringEquals" = {
            "dynamodb:Attributes" = [
              "nonce",
              "used_at",
            ]
          }
        }
      },
    ]
  })
}

# Managed Policy
resource "aws_iam_role_policy_attachment" "lambda_redirect_request_basic_execution" {
  role       = aws_iam_role.lambda_redirect_request.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
