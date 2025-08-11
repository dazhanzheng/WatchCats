# GitHub CI/CD 使用指南

本项目已配置完整的 GitHub Actions CI/CD 流程，可自动构建 Windows 和 macOS 安装包。

## 📋 前置要求

1. 将代码推送到 GitHub 仓库
2. 确保仓库有正确的权限设置（Actions 已启用）
3. 代码包含所有必要的文件

## 🚀 自动构建触发方式

### 1. 推送到主分支
每次推送到 `main` 或 `master` 分支时，自动触发构建：
```bash
git add .
git commit -m "Update features"
git push origin main
```

### 2. 创建版本标签（推荐用于发布）
创建以 `v` 开头的标签会触发完整的发布流程：
```bash
# 创建标签
git tag v1.0.0
git push origin v1.0.0

# 或者一次性推送所有标签
git push origin --tags
```

### 3. 手动触发
在 GitHub 仓库页面：
1. 点击 `Actions` 标签
2. 选择 `Build Windows Installer` 或 `Release Build`
3. 点击 `Run workflow`
4. 选择分支并点击 `Run workflow` 按钮

## 📦 工作流说明

### build-windows.yml
**用途**: 日常构建和测试
- 触发: 推送、PR、手动
- 产出: 
  - Windows 便携版 exe
  - Windows 安装程序（Inno Setup）
- 下载: Actions 页面的 Artifacts 部分

### release.yml
**用途**: 正式版本发布
- 触发: 版本标签、手动
- 产出:
  - Windows 便携版 exe
  - Windows Inno Setup 安装程序
  - Windows NSIS 安装程序
  - macOS DMG 安装包
  - macOS APP 压缩包
- 下载: Releases 页面

## 🎯 使用步骤

### 快速开始（日常构建）

1. **修改代码并推送**
```bash
git add .
git commit -m "Fix bug #123"
git push
```

2. **查看构建状态**
- 访问: `https://github.com/你的用户名/仓库名/actions`
- 查看正在运行的工作流

3. **下载构建产物**
- 构建完成后，在 Actions 运行详情页
- 滚动到底部 `Artifacts` 部分
- 下载需要的文件

### 正式发布流程

1. **更新版本号**（可选）
编辑相关配置文件中的版本号

2. **创建发布标签**
```bash
# 查看当前标签
git tag

# 创建新标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

3. **等待自动发布**
- 工作流会自动：
  - 构建所有平台的安装包
  - 创建 GitHub Release
  - 上传所有安装文件
  - 生成下载链接

4. **编辑发布说明**
- 访问 Releases 页面
- 编辑自动生成的 Release
- 添加更详细的更新说明

## 🛠️ 配置说明

### 修改构建配置

#### 更改 Python 版本
编辑 `.github/workflows/*.yml`:
```yaml
env:
  PYTHON_VERSION: '3.10'  # 改为需要的版本
```

#### 更改应用名称
编辑 `.github/workflows/*.yml`:
```yaml
env:
  APP_NAME: '新名称'
  APP_NAME_EN: 'NewName'
```

### 添加代码签名（可选）

#### Windows 代码签名
1. 获取代码签名证书
2. 将证书转换为 Base64：
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.pfx"))
```
3. 添加 GitHub Secrets：
   - `WINDOWS_CERTIFICATE`: Base64 编码的证书
   - `WINDOWS_CERTIFICATE_PASSWORD`: 证书密码

4. 更新工作流：
```yaml
- name: Sign executable
  run: |
    $cert = [Convert]::FromBase64String("${{ secrets.WINDOWS_CERTIFICATE }}")
    [IO.File]::WriteAllBytes("cert.pfx", $cert)
    signtool sign /f cert.pfx /p "${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}" /t http://timestamp.digicert.com dist\*.exe
    Remove-Item cert.pfx
```

#### macOS 代码签名
1. 导出开发者证书
2. 添加 GitHub Secrets：
   - `MACOS_CERTIFICATE`: Base64 编码的 p12 证书
   - `MACOS_CERTIFICATE_PWD`: 证书密码
   - `APPLE_ID`: Apple ID
   - `APPLE_PASSWORD`: App专用密码

3. 工作流会自动处理签名和公证

## 📊 构建状态徽章

在 README.md 中添加构建状态徽章：

```markdown
![Build Status](https://github.com/你的用户名/仓库名/workflows/Build%20Windows%20Installer/badge.svg)
![Release](https://github.com/你的用户名/仓库名/workflows/Release%20Build/badge.svg)
```

## 🔍 故障排除

### 构建失败
1. 检查 Actions 日志中的错误信息
2. 确保所有依赖都在 `requirements.txt` 中
3. 验证 Python 版本兼容性

### 找不到构建产物
- 确保构建成功完成
- Artifacts 默认保留 30 天
- 检查工作流的 `upload-artifact` 步骤

### Release 未创建
- 确保标签格式正确（`v*.*.*`）
- 检查是否有必要的仓库权限
- 查看 Actions 日志中的错误

### 安装程序无法运行
- Windows: 可能需要允许运行未签名的程序
- macOS: 可能需要在"安全性与隐私"中允许运行

## 💡 最佳实践

1. **版本管理**
   - 使用语义化版本号（如 1.0.0）
   - 为每个发布创建标签
   - 在 CHANGELOG.md 中记录更改

2. **测试**
   - 先在分支上测试构建
   - 使用 PR 触发测试构建
   - 在发布前充分测试

3. **安全**
   - 不要在代码中硬编码敏感信息
   - 使用 GitHub Secrets 存储密钥
   - 定期更新依赖

4. **优化**
   - 使用缓存加速构建
   - 并行构建不同平台
   - 清理不必要的文件减小体积

## 📚 相关链接

- [GitHub Actions 文档](https://docs.github.com/actions)
- [PyInstaller 文档](https://pyinstaller.org)
- [Inno Setup 文档](https://jrsoftware.org/isinfo.php)
- [NSIS 文档](https://nsis.sourceforge.io/Docs)

## 🤝 需要帮助？

如遇问题，请：
1. 查看 Actions 运行日志
2. 检查本文档的故障排除部分
3. 在项目 Issues 中搜索类似问题
4. 创建新 Issue 描述你的问题

---

*最后更新: 2025-08-11*