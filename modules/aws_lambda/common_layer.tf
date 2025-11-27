# Lambda Layerのソースディレクトリとビルド出力先
locals {
  layer_source_dir    = "${path.root}/../../lambda/layers/common"
  layer_build_dir     = "${path.root}/.build/common_layer"
  static_resource_dir = "${path.root}/../../static"
}

# ビルドスクリプトを実行してLayerをビルド
resource "null_resource" "build_common_layer" {
  triggers = {
    requirements = filemd5("${local.layer_source_dir}/python/requirements.txt")
    build_script = filemd5("${local.layer_source_dir}/build.sh")
    # カスタムコードの変更を検出
    custom_code = sha256(join("", [
      for f in fileset("${local.layer_source_dir}/python", "**/*.py") :
      filesha256("${local.layer_source_dir}/python/${f}")
    ]))
    static_files = sha256(join("", [
      for f in fileset("${local.static_resource_dir}", "**/*") :
      filesha256("${local.static_resource_dir}/${f}")
    ]))
  }

  provisioner "local-exec" {
    command     = "chmod +x ${local.layer_source_dir}/build.sh && BUILD_OUTPUT_DIR=${path.root}/.build ${local.layer_source_dir}/build.sh"
    working_dir = path.root
  }
}

data "archive_file" "common_layer" {
  type        = "zip"
  source_dir  = local.layer_build_dir
  output_path = "${path.root}/.build/common_layer.zip"

  depends_on = [null_resource.build_common_layer]
}

resource "aws_lambda_layer_version" "common" {
  layer_name = "Delibird-${var.environment}-CommonLayer"

  filename                 = data.archive_file.common_layer.output_path
  source_code_hash         = data.archive_file.common_layer.output_base64sha256
  compatible_runtimes      = [var.runtime]
  compatible_architectures = var.architectures
}
