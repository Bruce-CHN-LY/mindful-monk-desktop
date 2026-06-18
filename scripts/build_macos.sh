#!/bin/zsh
set -e

ROOT="${0:A:h:h}"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
  for candidate in python3.13 python3.12 python3.11; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PYTHON="$candidate"
      break
    fi
  done
  if [[ -z "$PYTHON" ]]; then
    echo "需要 Python 3.11、3.12 或 3.13。"
    exit 1
  fi
  "$PYTHON" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
rm -rf build dist

ICON_ARGS=()
if [[ -f app/assets/app.icns ]]; then
  ICON_ARGS=(--icon app/assets/app.icns)
fi

.venv/bin/pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "一念小沙弥" \
  --osx-bundle-identifier "com.mindfulmonk.desktop" \
  --add-data "app/assets:assets" \
  "${ICON_ARGS[@]}" \
  mindful_monk.py

PLIST="dist/一念小沙弥.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString 1.0.0" "$PLIST"
/usr/libexec/PlistBuddy -c "Add :CFBundleVersion string 1.0.0" "$PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :CFBundleVersion 1.0.0" "$PLIST"
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST" 2>/dev/null || \
  /usr/libexec/PlistBuddy -c "Set :LSUIElement true" "$PLIST"
codesign --force --deep --sign - "dist/一念小沙弥.app"

echo "已生成：$ROOT/dist/一念小沙弥.app"
