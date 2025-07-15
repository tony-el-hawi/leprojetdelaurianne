#!/bin/bash
set -e

# Define paths
LAMBDA_SRC_DIR="lambda"
LAMBDA_SRC_FINE_NAME="lambda_function.py"
BUILD_DIR="lambda_build"
ZIP_FILE="${BUILD_DIR}/lambda.zip"

echo "🔧 Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
sleep 2

echo "📦 Copying Lambda source code..."
cp "${LAMBDA_SRC_DIR}/${LAMBDA_SRC_FINE_NAME}" "$BUILD_DIR/"

echo "🗜️  Creating zip archive..."
cd "$BUILD_DIR"
zip -r lambda.zip . > /dev/null
cd ..

echo "🔍 Generating content hash..."
sha256sum lambda.zip > lambda.zip.sha256

echo "✅ Lambda package created at ${ZIP_FILE}"
