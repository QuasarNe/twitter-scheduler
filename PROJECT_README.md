# Twitter Scheduler 项目概述

## 项目简介

Twitter Scheduler 是一个基于 Twitter API v2 和 OpenAI 的自动化推文调度和回复系统。支持多账号管理、AI 生成内容、定时发推和自动回复提及。

## 主要功能

- **多账号支持**: 同时管理多个 Twitter 账号
- **AI 内容生成**: 使用 OpenAI 生成推文和回复
- **定时任务**: 根据配置定时发送 AI 生成的推文
- **自动回复**: 自动回复 @提及，支持过滤和去重
- **日志记录**: 详细的运行日志和推文历史

## 技术栈

- **语言**: Python 3.14+
- **框架**: APScheduler (定时任务), Tweepy (Twitter API), OpenAI (AI 生成)
- **环境管理**: uv (虚拟环境和包管理)
- **配置**: JSON 配置文件 + 环境变量

## 安装和运行

### 环境设置

1. 安装 uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 创建虚拟环境: `uv venv`
3. 激活环境: `source .venv/bin/activate`
4. 安装依赖: `uv pip install -r requirements.txt`

### 配置

1. 编辑 `CONTENT_config.json` 配置账号和设置
2. 创建 `.env` 文件设置环境变量 (见 CONFIG_README.md)

### 运行

```bash
python twitter_scheduler.py
```

测试模式: 设置 `TEST_MODE=true` 发送测试推文

## 文件结构

- `twitter_scheduler.py`: 主程序
- `CONTENT_config.json`: 配置文件
- `requirements.txt`: Python 依赖
- `CONFIG_README.md`: 配置说明
- `scheduler.log`: 运行日志
- `tweet_history_{account}.log`: 推文历史
- `replied_tweets_{account}.log`: 已回复记录

## 注意事项

- 确保 Twitter API 凭据正确
- OpenAI API Key 必需
- 遵守 Twitter 使用条款，避免过度自动化
- 监控日志文件以排查问题