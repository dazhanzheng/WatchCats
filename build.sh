#!/bin/bash

# Watch Cats Desktop Pet Assistant Build Script

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Watch Cats Build Script              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# 步骤 1: 安装依赖
echo -e "${GREEN}[1/3] 安装依赖...${NC}"
pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt

# 步骤 2: 安装 PyInstaller
echo -e "${GREEN}[2/3] 安装构建工具...${NC}"
pip install pyinstaller dmgbuild

# 步骤 3: 构建应用
echo -e "${GREEN}[3/3] 构建应用...${NC}"
pyinstaller --clean --noconfirm baal.spec

echo -e "${GREEN}✓ 构建完成！${NC}"
echo -e "${BLUE}Application location: dist/Watch Cats.app${NC}"

# 可选：创建 DMG
read -p "是否创建 DMG 文件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}创建 DMG 文件...${NC}"
    dmgbuild -s scripts/dmgbuild-settings.py -D app=dist/Watch\ Cats.app "Watch Cats" dist/Watch\ Cats.dmg
    echo -e "${GREEN}✓ DMG 创建完成！${NC}"
fi