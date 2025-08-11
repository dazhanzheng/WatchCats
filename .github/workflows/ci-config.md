# GitHub Actions CI/CD 配置说明

## 当前工作流配置

### 自动触发的工作流（推送main分支）

| 工作流 | 文件 | 触发条件 | 产物 | 运行时间 |
|--------|------|---------|------|----------|
| Build Windows Installer | `build-windows.yml` | push to main | Windows exe + installer | ~5分钟 |
| Build Windows (Fast) | `build-windows-fast.yml` | push to main | Windows exe + zip | ~3分钟 |
| Build macOS DMG | `build-macos.yml` | push to main | macOS app + DMG | ~5分钟 |

### 手动/标签触发的工作流

| 工作流 | 文件 | 触发条件 | 产物 |
|--------|------|---------|------|
| Build All Platforms | `build-all-platforms.yml` | 标签 v* 或手动 | 全平台 |
| Release Build | `release.yml` | 标签 v* 或手动 | 全平台发布 |

## 并行运行说明

当推送代码到main分支时，会**同时触发**3个工作流：
- 它们**并行运行**，互不影响
- 总耗时 = 最慢的工作流时间（约5分钟）
- 而非串行累加（15分钟）

## GitHub Actions 限制

### 免费版限制：
- **并发任务**：20个并发任务
- **每月时间**：2000分钟（私有仓库）/无限（公开仓库）
- **单任务时长**：最长6小时
- **runner数量**：Windows/Linux各20个，macOS各5个

### 对你的影响：
- ✅ 公开仓库：无时间限制
- ✅ 3个并发：远低于20个限制
- ✅ 5分钟构建：远低于6小时限制

## 优化选项

### 选项1：保持现状（推荐）
**优点**：
- 快速并行构建
- 有备用方案（fast版本）
- 独立失败重试

**适用**：开发阶段，需要快速迭代

### 选项2：禁用重复的Windows构建
修改 `build-windows-fast.yml`：
```yaml
on:
  workflow_dispatch:  # 仅手动触发
  # push:            # 注释掉自动触发
  #   branches: [ main, master ]
```

**优点**：减少资源使用
**缺点**：失去fast版本的自动构建

### 选项3：使用条件触发
根据文件修改触发不同构建：
```yaml
on:
  push:
    branches: [ main ]
    paths:
      - 'baal/**'        # 只在代码修改时触发
      - 'requirements.txt'
      - '*.py'
```

### 选项4：串行构建（不推荐）
使用 `needs` 关键字创建依赖：
```yaml
jobs:
  build-windows:
    # ...
  build-macos:
    needs: build-windows  # 等待Windows完成
    # ...
```

**缺点**：总时间变长

## 建议配置

对于你的项目，建议：

1. **开发阶段**：保持当前并行配置
2. **发布阶段**：使用 `build-all-platforms.yml` 或 `release.yml`
3. **可选优化**：禁用 `build-windows-fast.yml` 的自动触发

## 查看构建状态

- 所有构建：https://github.com/dazhanzheng/WatchCats/actions
- Windows构建：https://github.com/dazhanzheng/WatchCats/actions/workflows/build-windows.yml
- macOS构建：https://github.com/dazhanzheng/WatchCats/actions/workflows/build-macos.yml

## 手动控制

如果想手动控制构建顺序，可以：
1. 先推送不触发CI的分支
2. 通过Actions页面手动运行特定工作流
3. 使用 `[skip ci]` 在commit message中跳过CI