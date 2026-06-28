# Twitter Scheduler

一个基于 Twitter API v2 和 OpenAI 的自动化推文调度和回复系统。支持多账号管理、AI 生成内容、定时发推和自动回复提及。

## ✨ 主要功能

- **多账号支持**: 同时管理多个 Twitter 账号，只需一个实例。
- **AI 内容生成**: 结合 OpenAI 生成高质量推文并根据上下文智能回复。
- **定时任务**: 根据自定义配置定时发送 AI 生成的推文。
- **自动回复**: 自动回复 @提及，支持智能过滤和去重防刷。
- **日志记录**: 详细的运行日志和推文历史追踪。

## 🛠 技术栈

- **语言**: Python 3.14+
- **框架**: APScheduler (定时任务), Tweepy (Twitter API 交互), OpenAI (AI 生成)
- **环境管理**: [uv](https://github.com/astral-sh/uv) (极速 Python 包和环境管理器)
- **配置**: JSON 配置文件 + 环境变量

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

## ⚠️ 注意事项

- 确保您的 Twitter API 凭据具有正确的读写 (Read and Write) 权限。
- 必须提供 OpenAI API Key 才能进行内容生成。
- **合规性**: 请严格遵守 [Twitter 开发者协议和政策](https://developer.twitter.com/en/developer-terms/agreement-and-policy)，避免过度自动化或垃圾信息行为。
- 定期监控日志文件以排查潜在问题。
