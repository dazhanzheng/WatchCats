# 数据迁移故障排除指南 / Data Migration Troubleshooting Guide

## 问题诊断 / Problem Diagnosis

### 症状 / Symptoms
用户报告: "迁移内容好像把旧的删了新的也没有成功复制"
User report: "Migration seems to delete old data without successfully copying to new location"

### 根本原因分析 / Root Cause Analysis

1. **权限问题 / Permission Issues**:
   - Windows 文件权限可能阻止复制
   - 某些防病毒软件可能干扰文件操作
   - UAC (用户账户控制) 可能限制访问

2. **路径问题 / Path Issues**:
   - 环境变量可能未正确解析
   - 特殊字符或空格可能导致问题
   - 路径可能不存在或无法访问

3. **文件锁定 / File Locking**:
   - 如果旧版本 BaalPet 正在运行，文件可能被锁定
   - 其他程序可能正在访问这些文件

## 改进措施 / Improvements Implemented

### 1. SafeCopyFile 函数
```pascal
function SafeCopyFile(const SourceFile, DestFile: String): Boolean;
```
- 首先尝试 Pascal 的 `FileCopy`
- 失败时回退到 Windows `copy` 命令
- 验证目标文件是否成功创建

### 2. 详细的错误处理
- 记录每个失败的文件
- 显示具体的错误原因
- 提供明确的解决建议

### 3. 改进的日志记录
```pascal
Log('Migration: Old path = ' + OldConfigPath);
Log('Migration: New path = ' + NewConfigPath);
Log('Migration: Successfully copied config.json');
```

## 手动迁移步骤 / Manual Migration Steps

如果自动迁移失败，请按以下步骤手动迁移:

### Windows 命令行方法 / Command Line Method

1. **打开命令提示符（管理员）/ Open Admin Command Prompt**:
   ```
   Win + X → Windows PowerShell (管理员)
   ```

2. **创建目标目录 / Create target directory**:
   ```batch
   mkdir "%LOCALAPPDATA%\WatchCats"
   ```

3. **复制所有文件 / Copy all files**:
   ```batch
   xcopy "%APPDATA%\BaalPet\*.*" "%LOCALAPPDATA%\WatchCats\" /E /I /Y /H
   ```

   参数说明 / Parameters:
   - `/E` - 复制所有子目录 / Copy all subdirectories
   - `/I` - 目标是目录 / Target is directory
   - `/Y` - 覆盖不提示 / Overwrite without prompt
   - `/H` - 复制隐藏文件 / Copy hidden files

### Windows 资源管理器方法 / File Explorer Method

1. **打开源文件夹 / Open source folder**:
   - 按 `Win + R`
   - 输入 `%APPDATA%\BaalPet`
   - 按回车

2. **打开目标文件夹 / Open target folder**:
   - 按 `Win + R`
   - 输入 `%LOCALAPPDATA%`
   - 创建新文件夹 `WatchCats`

3. **复制文件 / Copy files**:
   - 选择 BaalPet 文件夹中的所有文件 (`Ctrl + A`)
   - 复制 (`Ctrl + C`)
   - 切换到 WatchCats 文件夹
   - 粘贴 (`Ctrl + V`)

## 验证迁移 / Verify Migration

### 检查文件是否存在 / Check if files exist:

```batch
dir "%LOCALAPPDATA%\WatchCats" /B
```

应该看到 / Should see:
- config.json
- chat_history.json
- schedules.json (如果存在 / if exists)
- goals.json (如果存在 / if exists)
- memory (文件夹 / folder)

### 验证文件内容 / Verify file contents:

```batch
type "%LOCALAPPDATA%\WatchCats\config.json"
```

## 预防措施 / Preventive Measures

1. **安装前 / Before Installation**:
   - 关闭所有 BaalPet/WatchCats 实例
   - 暂时禁用防病毒软件
   - 确保有足够的磁盘空间

2. **安装时 / During Installation**:
   - 以管理员身份运行安装程序
   - 如果提示权限，选择"是"

3. **安装后 / After Installation**:
   - 验证新版本正常运行
   - 确认数据已迁移
   - 保留旧数据至少一周

## 常见问题解答 / FAQ

**Q: 为什么不自动删除旧数据？/ Why not auto-delete old data?**
A: 为了数据安全，让用户确认新版本正常后再手动删除。
   For data safety, users should confirm new version works before manual deletion.

**Q: 可以多次运行迁移吗？/ Can migration run multiple times?**
A: 是的，迁移只复制不存在的文件，不会覆盖已有文件。
   Yes, migration only copies non-existing files, won't overwrite existing ones.

**Q: 如果两个位置都有配置怎么办？/ What if both locations have config?**
A: 新位置的配置优先，旧配置不会覆盖新配置。
   New location config takes priority, old config won't overwrite new.

## 技术细节 / Technical Details

### 路径映射 / Path Mapping
```
旧路径 / Old: C:\Users\[用户名]\AppData\Roaming\BaalPet
新路径 / New: C:\Users\[用户名]\AppData\Local\WatchCats
```

### 环境变量 / Environment Variables
- `%APPDATA%` = `C:\Users\[用户名]\AppData\Roaming`
- `%LOCALAPPDATA%` = `C:\Users\[用户名]\AppData\Local`

### Inno Setup 变量 / Inno Setup Variables
- `{userappdata}` = User's AppData\Roaming
- `{localappdata}` = User's AppData\Local

## 获取帮助 / Getting Help

如果问题持续，请提供以下信息 / If problems persist, provide:

1. Windows 版本 / Windows version:
   ```batch
   winver
   ```

2. 目录权限 / Directory permissions:
   ```batch
   icacls "%APPDATA%\BaalPet"
   icacls "%LOCALAPPDATA%\WatchCats"
   ```

3. 安装日志 / Installation log:
   运行安装程序时添加 `/LOG` 参数
   Run installer with `/LOG` parameter:
   ```batch
   WatchCats-Setup.exe /LOG="install.log"
   ```

将以上信息发送到 / Send above info to:
https://github.com/dazhanzheng/WatchCats/issues