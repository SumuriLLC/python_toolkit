#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the PyInstaller output directory
APP_PATH="$SCRIPT_DIR"
CERT="Developer ID Application: SUMURI LLC (M2UAN8S5M3)"

echo "🧹 Cleaning up unnecessary files..."

find "$APP_PATH" -name "*.o" -delete
find "$APP_PATH" -name "*.a" -delete
find "$APP_PATH" -name "*.pyc" -delete
find "$APP_PATH" -type d -name "__pycache__" -exec rm -rf {} +

echo "📝 Signing native binaries inside $APP_PATH"

# Find all .dylib and .so files and sign them
find "$APP_PATH" -type f \( -name "*.so" -o -name "*.dylib" \) | while read file; do
  echo "🔏 Signing $file"
  codesign --force --options runtime --sign "$CERT" "$file"
done

# Sign the main binary
MAIN_BINARY="$APP_PATH/dist/dict_extractor"
if [ -f "$MAIN_BINARY" ]; then
  echo "🔏 Signing $MAIN_BINARY"
  codesign --force --options runtime --sign "$CERT" "$MAIN_BINARY"
fi

echo "✅ Verifying signature..."
codesign --verify --deep --strict --verbose=2 "$MAIN_BINARY"

echo "🎉 Done" 
