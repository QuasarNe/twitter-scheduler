# Twitter Scheduler

一个基于 X API 和 OpenAI API 的自动化推文调度和回复系统。支持多账号管理、AI 生成内容、定时发推和自动回复提及。

## ✨ 主要功能

- **多账号支持**: 同时管理多个 Twitter 账号，只需一个实例。
- **AI 内容生成**: 结合 OpenAI 生成高质量推文并根据上下文智能回复。
- **定时任务**: 根据自定义配置定时发送 AI 生成的推文。
- **自动回复**: 自动回复 @提及，支持智能过滤和去重防刷。
- **日志记录**: 详细的运行日志和推文历史追踪。

## 使用方法

需要一个 X 开发者账号和 OpenAI API Key。请确保您已在 [X Developer Console](https://developer.x.com/) 创建应用并获取必要的 API 凭据。

## 🚀 安装和运行

### 1. 环境设置

推荐使用 `uv` 进行环境管理:

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活环境 (macOS/Linux)
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt
```

### 2. 配置

1. **账号设置**: 编辑 `CONTENT_config.json` 来配置您的账号、发布时间和 AI Prompt。
2. **环境变量**: 基于 `.env.example` 创建 `.env` 文件并设置各种 API Keys (详见 `CONFIG_README.md`)。

### 3. 运行

启动程序:

```bash
python twitter_scheduler.py
```

**测试模式**: 若要进行测试发推 (生成日志但不会真实发送 API 请求到 Twitter)，请设置 `TEST_MODE` 环境变量：
```bash
TEST_MODE=true python twitter_scheduler.py
```

## 📁 文件结构

- `twitter_scheduler.py`: 主程序入口
- `CONTENT_config.json`: 账号和调度配置文件
- `requirements.txt`: Python 依赖
- `CONFIG_README.md`: 详细配置说明
- `scheduler.log`: 运行日志
- `tweet_history_{account}.log`: 推文发布历史
- `replied_tweets_{account}.log`: 已回复记录

## 注意事项

- 如果管理多个账号，**与 X Developer Console 登录账号不同的账号需要用 authorize_new_app.py 进行授权来获取 access token。**
- 确保您的 Twitter API 凭据具有正确的读写 (Read and Write) 权限。
- 必须提供 OpenAI API Key 才能进行内容生成。
- 合规性: 遵守 [Twitter 开发者协议和政策](https://developer.twitter.com/en/developer-terms/agreement-and-policy)，避免过度自动化或垃圾信息行为。
- 定期监控日志文件以排查潜在问题。
