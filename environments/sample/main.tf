module "aws_dynamodb" {
  source = "../../modules/aws_dynamodb"

  environment = local.environment
}

module "aws_iam" {
  source = "../../modules/aws_iam"

  environment = local.environment

  ddb_link_table = {
    name = module.aws_dynamodb.link_table.name
    arn  = module.aws_dynamodb.link_table.arn
  }

  ddb_link_nonce_table = {
    name = module.aws_dynamodb.link_nonce_table.name
    arn  = module.aws_dynamodb.link_nonce_table.arn
  }

  lambda_redirect_request = {
    name = module.aws_lambda.lambda_redirect_request.function_name
    arn  = module.aws_lambda.lambda_redirect_request.arn
  }

  lambda_admin_portal = {
    name = module.aws_lambda.lambda_admin_portal.function_name
    arn  = module.aws_lambda.lambda_admin_portal.arn
  }
}

module "aws_lambda" {
  source = "../../modules/aws_lambda"

  environment     = local.environment
  environment_var = "{}" # TODO: Change values as needed
  runtime         = "python3.13"
  architectures   = ["arm64"]
  memory_size     = 512
  timeout         = 10

  ddb_link_table = {
    name = module.aws_dynamodb.link_table.name
    arn  = module.aws_dynamodb.link_table.arn
  }

  ddb_link_nonce_table = {
    name = module.aws_dynamodb.link_nonce_table.name
    arn  = module.aws_dynamodb.link_nonce_table.arn
  }

  role_redirect_request = {
    name = module.aws_iam.role_lambda_redirect_request.name
    arn  = module.aws_iam.role_lambda_redirect_request.arn
  }

  role_admin_portal = {
    name = module.aws_iam.role_lambda_admin_portal.name
    arn  = module.aws_iam.role_lambda_admin_portal.arn
  }

  link_prefix                    = "" # TODO: Change value as needed (e.g. https://example.com/dev/.... -> "dev")
  allowed_domain                 = local.config["allowed_domain"]
  reserved_concurrent_executions = local.config["aws"]["lambda"]["reserved_concurrent_executions"]
}

module "aws_s3" {
  source = "../../modules/aws_s3"

  environment = local.environment

  bucket_name      = local.config["aws"]["s3"]["bucket_name"]
  remote_base_path = local.config["aws"]["s3"]["remote_base_path"]
}
