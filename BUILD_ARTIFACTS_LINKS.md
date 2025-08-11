# 🔗 构建产物快速访问链接

## GitHub仓库
- 主页: https://github.com/dazhanzheng/WatchCats
- Actions: https://github.com/dazhanzheng/WatchCats/actions
- Releases: https://github.com/dazhanzheng/WatchCats/releases

## 查看最新构建状态
[![Build Status](https://github.com/dazhanzheng/WatchCats/workflows/Build%20Windows%20Installer/badge.svg)](https://github.com/dazhanzheng/WatchCats/actions/workflows/build-windows.yml)

## 日常构建产物（Artifacts）

### 查看方法：
1. 访问 [Actions页面](https://github.com/dazhanzheng/WatchCats/actions)
2. 点击最新的 **Build Windows Installer** 工作流运行
3. 在页面底部找到 **Artifacts** 部分
4. 下载需要的文件：
   - `BaalPetAssistant-portable-windows` - 便携版exe
   - `BaalPetAssistant-installer-windows` - 安装程序

### 直接访问最新工作流：
[查看最新构建](https://github.com/dazhanzheng/WatchCats/actions/workflows/build-windows.yml)

## 正式发布版本（Releases）

### 创建发布版本：
```bash
# 在本地创建标签
git tag -a v0.1.0 -m "First release"
git push origin v0.1.0
```

### 查看发布版本：
[Releases页面](https://github.com/dazhanzheng/WatchCats/releases)

## 手动触发构建

1. 访问 [Build Windows Installer](https://github.com/dazhanzheng/WatchCats/actions/workflows/build-windows.yml)
2. 点击 **Run workflow** 按钮
3. 选择分支（通常是 main）
4. 点击绿色的 **Run workflow** 按钮

## 下载说明

### Artifacts（临时构建）
- ✅ 每次代码推送自动生成
- ⏰ 保留30天
- 🔒 需要GitHub登录
- 📦 包含：exe文件 + 安装程序

### Releases（正式版本）
- ✅ 手动创建标签触发
- ♾️ 永久保存
- 🌍 公开访问
- 📦 包含：多种格式安装包 + 版本说明

## 构建产物文件说明

| 文件名 | 类型 | 说明 | 大小 |
|--------|------|------|------|
| `Baal宠物助手.exe` | 便携版 | 无需安装，直接运行 | ~50-80MB |
| `BaalPetAssistantSetup.exe` | Inno Setup | 推荐，专业安装程序 | ~40-60MB |
| `BaalPetAssistant-nsis-setup.exe` | NSIS | 备选安装程序 | ~40-60MB |

## 常见问题

### Q: 为什么看不到Artifacts？
A: 
- 确保构建成功完成（绿色勾号）
- 需要登录GitHub账号
- Artifacts在页面最底部

### Q: Artifacts和Releases有什么区别？
A:
- **Artifacts**: 开发版本，自动构建，临时保存
- **Releases**: 正式版本，手动发布，永久保存

### Q: 如何知道构建是否成功？
A: 
- ✅ 绿色勾号 = 成功
- ❌ 红色叉号 = 失败
- 🟡 黄色圆圈 = 进行中

---
*最后更新: 2025-01-11*