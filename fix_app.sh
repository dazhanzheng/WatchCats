#\!/bin/bash

# 彻底清理和重新签名应用
APP_PATH="dist/Watch Cats.app"

echo "清理应用..."
# 删除所有扩展属性
xattr -cr "$APP_PATH"

# 删除所有.DS_Store文件
find "$APP_PATH" -name .DS_Store -delete

# 使用深度签名，强制替换
echo "重新签名..."
codesign --force --deep --sign - "$APP_PATH"

echo "设置权限..."
chmod -R 755 "$APP_PATH"

echo "完成！"
echo ""
echo "现在你可以通过以下方式打开应用："
echo "1. 右键点击应用，选择'打开'（推荐）"
echo "2. 或在系统设置中允许运行未识别开发者的应用"
