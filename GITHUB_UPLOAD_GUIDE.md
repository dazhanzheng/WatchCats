# 📚 GitHub 上传和自动构建完整指南

## 第一步：在GitHub创建仓库

### 1. 登录GitHub
访问 [https://github.com](https://github.com) 并登录你的账号

### 2. 创建新仓库
- 点击右上角的 **+** 号，选择 **New repository**
- 填写仓库信息：
  - **Repository name**: `baal-standalone` （或你喜欢的名字）
  - **Description**: `Baal Desktop Pet Assistant - AI桌面宠物助手`
  - **Visibility**: 选择 `Public`（公开）或 `Private`（私有）
  - ⚠️ **重要**：不要勾选任何初始化选项：
    - ❌ 不要勾选 "Add a README file"
    - ❌ 不要选择 "Add .gitignore"
    - ❌ 不要选择 "Choose a license"
- 点击 **Create repository**

### 3. 复制仓库地址
创建后会看到快速设置页面，复制你的仓库地址：
- HTTPS: `https://github.com/你的用户名/baal-standalone.git`
- SSH: `git@github.com:你的用户名/baal-standalone.git`

## 第二步：连接并上传本地仓库

在本地项目目录（`/Users/dnf/Documents/baalproject/baal-standalone`）执行：

### 方法A：使用HTTPS（推荐新手）

```bash
# 1. 添加远程仓库
git remote add origin https://github.com/你的用户名/baal-standalone.git

# 2. 推送代码到GitHub
git push -u origin main
```

首次推送时会要求输入GitHub用户名和密码（或Personal Access Token）。

#### 如果需要Personal Access Token：
1. 访问 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token"
3. 设置名称和过期时间
4. 勾选 `repo` 权限
5. 生成并复制token
6. 使用token代替密码

### 方法B：使用SSH（推荐高级用户）

#### 先配置SSH密钥（如果没有）：
```bash
# 1. 生成SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 启动ssh-agent
eval "$(ssh-agent -s)"

# 3. 添加密钥到ssh-agent
ssh-add ~/.ssh/id_ed25519

# 4. 复制公钥
cat ~/.ssh/id_ed25519.pub
```

然后在GitHub添加SSH密钥：
1. GitHub → Settings → SSH and GPG keys
2. 点击 "New SSH key"
3. 粘贴公钥并保存

#### 上传代码：
```bash
# 1. 添加远程仓库
git remote add origin git@github.com:你的用户名/baal-standalone.git

# 2. 推送代码
git push -u origin main
```

## 第三步：启用GitHub Actions

### 1. 确认Actions已启用
- 访问你的仓库页面
- 点击 **Settings** 标签
- 左侧菜单找到 **Actions** → **General**
- 确保 **Actions permissions** 设置为：
  - ✅ "Allow all actions and reusable workflows"
  - 或 "Allow select actions and reusable workflows"

### 2. 首次触发构建
代码推送后，Actions会自动触发。你可以：

#### 方法1：手动触发（推荐首次测试）
1. 点击仓库的 **Actions** 标签
2. 左侧选择 **Build Windows Installer**
3. 右侧点击 **Run workflow**
4. 选择分支 `main`
5. 点击绿色的 **Run workflow** 按钮

#### 方法2：通过代码修改触发
```bash
# 做一个小修改
echo "# Build Status" >> README.md
git add README.md
git commit -m "Trigger CI build"
git push
```

### 3. 查看构建进度
1. 点击 **Actions** 标签
2. 你会看到正在运行的工作流
3. 点击进入查看详细日志
4. 等待构建完成（通常需要5-10分钟）

## 第四步：下载构建产物

### 日常构建版本
1. 在 **Actions** 页面找到成功的构建
2. 点击进入构建详情
3. 滚动到页面底部的 **Artifacts** 部分
4. 下载需要的文件：
   - `BaalPetAssistant-portable-windows`: 便携版exe
   - `BaalPetAssistant-installer-windows`: 安装程序

### 正式发布版本
创建版本标签来触发正式发布：

```bash
# 1. 创建版本标签
git tag -a v1.0.0 -m "First release"

# 2. 推送标签
git push origin v1.0.0
```

然后在 **Releases** 页面下载。

## 第五步：后续开发流程

### 日常开发
```bash
# 1. 修改代码
# ... 编辑文件 ...

# 2. 提交更改
git add .
git commit -m "描述你的更改"

# 3. 推送到GitHub（自动触发构建）
git push
```

### 创建新版本
```bash
# 1. 更新版本号（可选）
# 编辑相关配置文件

# 2. 提交版本更改
git add .
git commit -m "Bump version to 1.1.0"

# 3. 创建标签
git tag -a v1.1.0 -m "Release version 1.1.0"

# 4. 推送代码和标签
git push
git push origin v1.1.0
```

## 🎯 快速检查清单

- [ ] GitHub账号已登录
- [ ] 新仓库已创建（不含初始文件）
- [ ] 本地仓库已连接远程（`git remote -v` 查看）
- [ ] 代码已推送（`git push -u origin main`）
- [ ] Actions已启用（Settings → Actions）
- [ ] 首次构建已触发（Actions页面）
- [ ] 构建成功（绿色勾号）
- [ ] 安装包已下载测试

## 🔧 常见问题解决

### 问题1：推送失败 - "failed to push some refs"
```bash
# 如果远程有更新，先拉取
git pull origin main --allow-unrelated-histories
git push origin main
```

### 问题2：权限错误 - "Permission denied"
- 使用HTTPS：需要Personal Access Token
- 使用SSH：需要配置SSH密钥

### 问题3：Actions构建失败
1. 查看Actions日志找到错误
2. 常见原因：
   - Python版本不匹配
   - 依赖安装失败
   - 文件路径问题

### 问题4：找不到Artifacts
- 确保构建成功完成
- Artifacts在构建成功后才会出现
- 默认保留30天

## 📝 完整命令示例

```bash
# 完整的上传流程（使用HTTPS）
cd /Users/dnf/Documents/baalproject/baal-standalone

# 查看当前状态
git status

# 添加远程仓库（替换为你的用户名）
git remote add origin https://github.com/你的用户名/baal-standalone.git

# 推送代码
git push -u origin main

# 输入GitHub用户名和密码/Token

# 创建首个发布版本
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

## 🎉 恭喜！

完成以上步骤后，你就拥有了：
- ✅ 完整的GitHub仓库
- ✅ 自动化CI/CD流程
- ✅ Windows安装包自动构建
- ✅ 版本发布管理

每次推送代码都会自动构建新版本，用户可以直接下载使用！

## 📚 相关资源

- [GitHub官方文档](https://docs.github.com)
- [Git基础教程](https://git-scm.com/book/zh/v2)
- [GitHub Actions入门](https://docs.github.com/cn/actions/quickstart)
- [Personal Access Token创建](https://docs.github.com/cn/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

---

*如有问题，请参考项目的 `GITHUB_CICD.md` 文件了解更多CI/CD配置细节*