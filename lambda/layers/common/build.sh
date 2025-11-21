#!/bin/bash
set -e

# このスクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAYER_DIR="${SCRIPT_DIR}"

# BUILD_OUTPUT_DIRが指定されていればそれを使用、なければエラー
if [ -n "${BUILD_OUTPUT_DIR}" ]; then
    BUILD_DIR="${BUILD_OUTPUT_DIR}/common_layer"
else
    echo "Error: BUILD_OUTPUT_DIR environment variable is not set." >&2
    exit 1
fi

PYTHON_DIR="${BUILD_DIR}/python"
echo "Building common layer..."
echo "Output directory: ${BUILD_DIR}"

# 既存のbuildディレクトリをクリーンアップ
rm -rf "${BUILD_DIR}"
mkdir -p "${PYTHON_DIR}"

# requirements.txtから依存関係をインストール
if [ -f "${LAYER_DIR}/python/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r "${LAYER_DIR}/python/requirements.txt" -t "${PYTHON_DIR}" --upgrade
else
    echo "Error: No requirements.txt found" >&2
    exit 1
fi

# カスタムコード（ddb, utilなど）をコピー
echo "Copying custom code..."

# 除外するファイル/ディレクトリのパターン
EXCLUDE_PATTERNS=("__pycache__" "*.pyc" "*.pyo" "*.sh" "*.md" ".git" ".gitignore" "*.txt")

copied_count=0
for item in "${LAYER_DIR}/python"/*; do
    if [ ! -e "$item" ]; then
        continue  # ファイルが存在しない場合はスキップ
    fi

    item_name=$(basename "$item")
    should_exclude=false

    # 除外パターンにマッチするかチェック
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        # shellcheck disable=SC2254
        case "$item_name" in
            $pattern)
                should_exclude=true
                break
                ;;
        esac
    done

    if [ "$should_exclude" = false ]; then
        echo "Copying: $item_name"
        cp -r "$item" "${PYTHON_DIR}/"
        ((copied_count++))
    else
        echo "Skipping: $item_name"
    fi
done

# コピーされたファイルがあるか確認
if [ "$copied_count" -eq 0 ]; then
    echo "Error: No custom code was copied to ${PYTHON_DIR}" >&2
    exit 1
fi

echo "Common layer build complete: ${BUILD_DIR}"

# ビルド成果物の内容を表示
echo ""
echo "Build output contents:"
echo "----------------------"
ls -lh "${PYTHON_DIR}" | head -20
echo ""
echo "Total size:"
du -sh "${BUILD_DIR}"

