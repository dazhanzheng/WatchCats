# 🏃 Self-Hosted Runner 配置指南

## 当前状态
✅ Runner已配置完成
✅ 工作流已创建：`.github/workflows/build-self-hosted.yml`
⏳ 等待首次运行

## 启动Runner

### 方法1：前台运行（测试用）
```bash
cd ~/actions-runner
./run.sh
# 保持终端开启
```

### 方法2：后台运行
```bash
cd ~/actions-runner
nohup ./run.sh &
# 或使用 screen/tmux
```

### 方法3：作为服务运行（推荐）
```bash
cd ~/actions-runner
./svc.sh install  # 安装服务
./svc.sh start    # 启动服务
./svc.sh status   # 检查状态
```

## 工作流使用

### 自动触发
每次推送到main分支会自动在你的本地机器上构建：
- 使用本地环境
- 复用已安装的依赖
- 缓存虚拟环境

### 手动触发
1. 访问 [Actions页面](https://github.com/dazhanzheng/WatchCats/actions)
2. 选择 "Build on Self-Hosted Runner"
3. 点击 "Run workflow"

## 优化特性

### 智能缓存
- ✅ 虚拟环境缓存
- ✅ 依赖哈希检查
- ✅ 图标文件缓存
- ✅ 跳过未变更的安装

### 性能优势
| 项目 | GitHub Runner | Self-Hosted |
|------|--------------|-------------|
| 环境准备 | 1-2分钟 | 0秒（已存在） |
| 依赖安装 | 2-3分钟 | 0-10秒（缓存） |
| 构建速度 | 标准 | 使用全部CPU |
| 总时间 | 5-10分钟 | 1-3分钟 |

## 管理命令

### 查看状态
```bash
cd ~/actions-runner
./svc.sh status
```

### 查看日志
```bash
cd ~/actions-runner
tail -f _diag/Runner_*.log
```

### 停止Runner
```bash
./svc.sh stop
# 或 Ctrl+C（前台运行时）
```

### 卸载服务
```bash
./svc.sh uninstall
```

### 完全移除
```bash
cd ~/actions-runner
./config.sh remove --token YOUR_TOKEN
cd ..
rm -rf actions-runner
```

## 注意事项

### 安全建议
1. ⚠️ 只用于你自己的仓库
2. ⚠️ 不要在生产服务器运行
3. ⚠️ 定期更新runner版本
4. ⚠️ 使用专门的用户账户

### 资源占用
- CPU: 构建时100%（几分钟）
- 内存: 约2-4GB
- 磁盘: 约1GB（含缓存）
- 网络: 下载/上传artifacts

### 故障排除

#### Runner离线
```bash
# 检查进程
ps aux | grep Runner.Listener

# 重启服务
./svc.sh restart
```

#### 构建失败
- 检查磁盘空间
- 清理旧的构建：`rm -rf _work/*/`
- 重置虚拟环境：`rm -rf venv`

#### 权限问题
```bash
# 修复权限
chmod +x run.sh
chmod +x config.sh
chmod +x svc.sh
```

## 监控Dashboard

在GitHub查看runner状态：
1. 访问 [Settings > Actions > Runners](https://github.com/dazhanzheng/WatchCats/settings/actions/runners)
2. 查看你的runner状态（Idle/Active/Offline）

## 并行使用

你可以同时使用：
- **GitHub Runner**: 用于正式发布
- **Self-Hosted**: 用于快速开发测试

在workflow中指定：
```yaml
runs-on: ubuntu-latest  # GitHub的runner
# 或
runs-on: self-hosted    # 你的runner
```

## 最佳实践

1. **开发阶段**：使用self-hosted快速迭代
2. **发布阶段**：使用GitHub runner确保干净环境
3. **混合使用**：
   ```yaml
   strategy:
     matrix:
       runner: [self-hosted, ubuntu-latest]
   runs-on: ${{ matrix.runner }}
   ```

---

*Runner配置完成！推送代码即可触发本地构建。*