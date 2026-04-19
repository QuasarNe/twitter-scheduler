# 定时发推工具

一个简单但强大的 Python 工具，用于在固定时间自动发送推文到 Twitter。

## ✨ 功能特性

- ⏰ 支持多个固定时间点的定时发推
- 🌍 支持多时区配置
- 📝 灵活的推文管理（JSON 配置）
- 📊 推文历史记录
- 🔄 失败重试机制
- 🛡️ 安全的 API 凭证管理（使用 .env）
- 📋 详细的日志记录

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 Twitter API 凭证

访问 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)：

1. 登录你的 Twitter 开发者账户
2. 创建或选择一个应用
3. 进入 "Keys and tokens" 页面
4. 生成或复制 **Bearer Token**
5. （可选）如果使用 v1.1 API，也复制 API Key、Secret 和 Access Token

### 3. 配置凭证

```bash
# 复制环境变量模板
cp .env.example .env

# 在 .env 文件中填入你的 Bearer Token
# TWITTER_BEARER_TOKEN=your_bearer_token_here
```

### 4. 配置推文时间和内容

编辑 `config.json`：

```json
{
  "schedule": [
    {
      "time": "09:00",
      "message": "你的推文内容"
    },
    {
      "time": "14:00",
      "message": "第二条推文"
    }
  ],
  "timezone": "Asia/Shanghai",
  "retry_failed": true,
  "max_retries": 3
}
```

### 5. 测试 API 连接

```bash
python test_api.py
```

### 6. 启动服务

```bash
python twitter_scheduler.py
```

## 📁 项目结构

```
twitter-scheduler/
├── twitter_scheduler.py    # 主程序
├── test_api.py            # API 测试脚本
├── config.json            # 推文配置文件
├── .env                   # API 凭证（不要提交到 Git）
├── .env.example           # 环境变量模板
├── requirements.txt       # Python 依赖
├── tweet_history.log      # 推文历史记录（自动生成）
└── README.md             # 本文件
```

## ⚙️ 配置说明

### config.json

| 字段 | 说明 | 示例 |
|-----|------|------|
| `schedule` | 推文计划数组 | 见下方 |
| `time` | 推文时间（24小时制） | `"09:00"` |
| `message` | 推文内容 | `"早安！"` |
| `timezone` | 时区 | `"Asia/Shanghai"` |
| `retry_failed` | 是否重试失败的推文 | `true` |
| `max_retries` | 最大重试次数 | `3` |

### 常见时区

- `Asia/Shanghai` - 中国
- `America/New_York` - 纽约
- `Europe/London` - 伦敦
- `UTC` - 协调世界时

更多时区查看：[pytz timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## 🐛 故障排查

### "❌ 错误: 请在 .env 文件中设置 TWITTER_BEARER_TOKEN"

- 确保 `.env` 文件存在
- 检查 Bearer Token 是否正确填入
- 不要在 Bearer Token 中包含多余的空格

### "❌ API 连接失败"

- 验证 Bearer Token 有效性
- 检查网络连接
- 确保应用有 "Tweet Compose" 权限（在 Twitter Developer Portal 配置）

### 推文没有发送

- 检查日志文件中的错误信息
- 验证系统时间是否正确（定时任务依赖系统时间）
- 检查 Twitter API 是否有速率限制

## 📝 推文历史

推文历史自动保存在 `tweet_history.log` 文件中：

```
2026-04-18T15:23:47.123456 - ID: 1234567890 - 早安！今天又是美好的一天 🌅
```

## 🔒 安全提示

- ⚠️ **不要**将 `.env` 文件提交到 Git
- ⚠️ **不要**在代码中硬编码 API 凭证
- ✅ 使用 `.gitignore` 排除 `.env` 文件：

```
.env
tweet_history.log
*.pyc
__pycache__/
```

## 🎯 高级用法

### 在后台运行（Linux/Mac）

```bash
nohup python twitter_scheduler.py > twitter_scheduler.log 2>&1 &
```

### 使用 Systemd 服务（Linux）

创建 `/etc/systemd/system/twitter-scheduler.service`：

```ini
[Unit]
Description=Twitter Scheduler Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/twitter-scheduler
ExecStart=/usr/bin/python3 /path/to/twitter-scheduler/twitter_scheduler.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

然后运行：
```bash
sudo systemctl enable twitter-scheduler
sudo systemctl start twitter-scheduler
sudo systemctl status twitter-scheduler
```

### 使用 Cron 运行脚本（Linux/Mac）

编辑 crontab：
```bash
crontab -e
```

添加行：
```
0 9,14 * * * cd /path/to/twitter-scheduler && python twitter_scheduler.py
```

## 📚 相关资源

- [Twitter API 文档](https://developer.twitter.com/en/docs)
- [Tweepy 文档](https://docs.tweepy.org/)
- [APScheduler 文档](https://apscheduler.readthedocs.io/)

## 📄 许可证

MIT License

## 💬 支持

如有问题，请：
1. 检查 README 中的故障排查部分
2. 查看日志输出
3. 确保所有依赖都正确安装
