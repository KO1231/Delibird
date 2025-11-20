data "archive_file" "common_layer" {
  type        = "zip"
  source_dir  = "../../lambda/layers/common"
  output_path = "${path.root}/.build/common_layer.zip"
}

resource "aws_lambda_layer_version" "common" {
  layer_name = "Delibird-${var.environment}-CommonLayer"

  filename                 = data.archive_file.common_layer.output_path
  source_code_hash         = data.archive_file.common_layer.output_base64sha256
  compatible_runtimes      = [var.runtime]
  compatible_architectures = var.architectures
}
