resource "aws_iam_role" "lambda_admin_portal" {
  name = "DelibirdLambdaAdminPortalRole-${var.environment}"

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
resource "aws_iam_role_policy" "lambda_admin_portal" {
  role = aws_iam_role.lambda_admin_portal.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
        ]
        Resource = [
          var.ddb_link_table.arn,
        ]
      },
    ]
  })
}

# Managed Policy
resource "aws_iam_role_policy_attachment" "lambda_admin_portal_basic_execution" {
  role       = aws_iam_role.lambda_admin_portal.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
