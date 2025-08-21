# Windows 故障排除指南

## 常见问题：应用闪退

如果 Watch Cats 在您的 Windows 系统上闪退，请按以下步骤排查：

### 快速修复步骤

1. **运行依赖检查工具**
   - 双击运行 `check_windows_deps.bat`
   - 根据提示安装缺失的组件

2. **安装必要的运行库**
   - **Visual C++ Redistributable 2015-2022**
     - 下载地址：https://aka.ms/vs/17/release/vc_redist.x64.exe
     - 这是最常见的缺失依赖
   
   - **DirectX End-User Runtime**（如果提示缺少 d3dcompiler_47.dll）
     - 下载地址：https://www.microsoft.com/en-us/download/details.aspx?id=35

3. **以管理员身份运行**
   - 右键点击 `WatchCats.exe`
   - 选择"以管理员身份运行"

### 详细诊断步骤

#### 方法一：使用 PowerShell 诊断脚本
```powershell
# 在 PowerShell 中运行
.\check_windows_deps.ps1
```
这将生成详细的诊断报告。

#### 方法二：手动检查

1. **检查系统版本**
   - 按 `Win + R`，输入 `winver`
   - 确认是 Windows 10 或更高版本

2. **检查 Visual C++ 运行库**
   - 打开"控制面板" → "程序和功能"
   - 查找 "Microsoft Visual C++ 2015-2022 Redistributable (x64)"
   - 如果没有，请安装

3. **检查系统文件**
   打开命令提示符，运行：
   ```cmd
   where vcruntime140.dll
   where msvcp140.dll
   ```
   如果找不到这些文件，需要安装 VC++ 运行库

### 其他可能的解决方案

1. **更新 Windows**
   - 设置 → 更新和安全 → Windows 更新
   - 安装所有待定更新

2. **更新显卡驱动**
   - 访问显卡制造商网站（NVIDIA/AMD/Intel）
   - 下载并安装最新驱动

3. **禁用杀毒软件**
   - 临时禁用 Windows Defender 或第三方杀毒软件
   - 测试应用是否能正常运行
   - 如果可以运行，将应用添加到杀毒软件白名单

4. **兼容性模式**
   - 右键点击 `WatchCats.exe`
   - 属性 → 兼容性
   - 勾选"以兼容模式运行这个程序"
   - 选择 Windows 8

### 收集错误信息

如果以上方法都无效，请收集以下信息：

1. **事件查看器日志**
   - 按 `Win + X`，选择"事件查看器"
   - 导航到 Windows 日志 → 应用程序
   - 查找与 WatchCats 相关的错误

2. **生成诊断报告**
   运行 PowerShell 脚本并选择生成报告：
   ```powershell
   .\check_windows_deps.ps1
   # 选择 Y 生成诊断报告
   ```

3. **命令行启动**
   在命令提示符中运行，查看错误输出：
   ```cmd
   cd dist
   WatchCats.exe
   ```

### 已知兼容性问题

| Windows 版本 | 兼容性 | 注意事项 |
|------------|-------|---------|
| Windows 11 | ✅ 完全兼容 | - |
| Windows 10 (1909+) | ✅ 完全兼容 | 需要最新更新 |
| Windows 10 (早期版本) | ⚠️ 可能需要额外配置 | 安装所有更新和运行库 |
| Windows 8.1 | ⚠️ 部分兼容 | 需要所有运行库 |
| Windows 7 | ❌ 不支持 | PyQt6 不支持 Win7 |

### 联系支持

如果问题仍未解决：
1. 运行诊断工具生成报告
2. 收集错误截图和日志
3. 在项目 Issues 页面提交问题

## 预防措施

为避免将来出现问题：
1. 定期更新 Windows
2. 保持显卡驱动最新
3. 安装常用运行库（VC++、.NET Framework）
4. 使用稳定的杀毒软件并正确配置白名单

---
最后更新：2025-08-21