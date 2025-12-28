#!/bin/bash
set -e

# このスクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# LAMBDA_NAMEが指定されていればそれを使用、なければエラー
if [ -n "${LAMBDA_NAME}" ]; then
    LAMBDA_NAME="${LAMBDA_NAME}"
else
    echo "Error: LAMBDA_NAME environment variable is not set." >&2
    exit 1
fi
LAMBDA_DIR="${SCRIPT_DIR}/${LAMBDA_NAME}"

# BUILD_OUTPUT_DIRが指定されていればそれを使用、なければエラー
if [ -n "${BUILD_OUTPUT_DIR}" ]; then
    BUILD_DIR="${BUILD_OUTPUT_DIR}/${LAMBDA_NAME}"
else
    echo "Error: BUILD_OUTPUT_DIR environment variable is not set." >&2
    exit 1
fi

echo "Building Fuction: ${LAMBDA_NAME}..."
echo "Output directory: ${BUILD_DIR}"

# 既存のbuildディレクトリをクリーンアップ
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# requirements.txtから依存関係をインストール
if [ -f "${LAMBDA_DIR}/requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    # Lambdaを/var/taskにマウントして、buildディレクトリを/delibird/outputにマウント
    # /delibird/outputを通して、buildディレクトリにパッケージをインストール
    docker run --rm \
    -v "${LAMBDA_DIR}":/var/task \
    -v "${BUILD_DIR}":/delibird/output \
    public.ecr.aws/sam/build-python3.13:latest-arm64 \
    pip install -r "requirements.txt" -t "/delibird/output" --upgrade
else
    echo "Error: No requirements.txt found" >&2
    exit 1
fi

# カスタムコード（ddb, utilなど）をコピー
echo "Copying custom code..."

# 除外するファイル/ディレクトリのパターン
EXCLUDE_PATTERNS=("__pycache__" "*.pyc" "*.pyo" "*.sh" "*.md" ".git" ".gitignore" "*.txt")

copied_count=0
for item in "${LAMBDA_DIR}"/*; do
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
        cp -r "$item" "${BUILD_DIR}/"
        ((copied_count++))
    else
        echo "Skipping: $item_name"
    fi
done

# コピーされたファイルがあるか確認
if [ "$copied_count" -eq 0 ]; then
    echo "Error: No custom code was copied to ${BUILD_DIR}" >&2
    exit 1
fi

echo "Function ${LAMBDA_NAME} build completed successfully."

# ビルド成果物の内容を表示
echo ""
echo "Build output contents:"
echo "----------------------"
echo "Python packages:"
ls -lh "${BUILD_DIR}" | head -20
echo ""
echo "Total size:"
du -sh "${BUILD_DIR}"

