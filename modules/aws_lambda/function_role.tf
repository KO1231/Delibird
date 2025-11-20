resource "aws_iam_role" "lambda_redirect_request" {
  name = "DelibirdLambdaRedirectRequestRole"

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

resource "aws_iam_role_policy_attachment" "lambda_redirect_request_basic_execution" {
  role       = aws_iam_role.lambda_redirect_request.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

/*
resource "aws_iam_role_policy" "lambda_access_policy" {
  name = "DelibirdLambdaRedirectRequestPolicy"
  role = aws_iam_role.delibird_lambda_redirect_request
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Action" : [
          "logs:CreateLogStream",
          "logs:CreateLogGroup",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*"
      },
    ]
  })
}
*/
