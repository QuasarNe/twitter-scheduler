# Twitter Scheduler 配置说明

## 配置文件 (CONTENT_config.json)

```json
{
    "accounts": [
        {
            "name": "账号名称",
            "api_key": "Twitter API Key",
            "api_secret": "Twitter API Secret",
            "access_token": "Twitter Access Token",
            "access_token_secret": "Twitter Access Token Secret",
            "bearer_token": "Twitter Bearer Token (可选)",
            "timezone": "时区 (如 'Asia/Shanghai')",
            "ai_settings": {
                "system_prompt": "AI 系统提示",
                "model": "AI 模型",
                "prompts": {
                    "类型": {
                        "time": "HH:MM",
                        "instruction": "AI 生成指令"
                    }
                }
            },
            "runtime": {//默认值
                "check_mentions_interval_minutes": 5,
                "enable_auto_reply": true,
                "enable_auto_like_mentions": false//在上一选项启用后才生效
            }
        }
    ]
}
```

## 环境变量 (.env)

- `OPENAI_API_KEY`: OpenAI API Key (必需)
- `OPENAI_BASE_URL`: OpenAI API 基础 URL (默认: https://api.openai.com/v1)
- `AI_SYSTEM_PROMPT`: 全局 AI 系统提示 (默认: "你是一个推特博主。")
- `AI_MODEL`: 全局 AI 模型 (默认: "gpt-4o")
- `AI_REPLY_PROMPT`: 全局回复提示 (默认: "请根据上下文简短地回复这条推文。")
- `BEARER_TOKEN`: Twitter Bearer Token (覆盖配置文件)
- `TEST_MODE`: 测试模式 ("true"/"false", 默认: "false")
- `RUN_HOURS`: 运行小时数 (默认: 24, -1 为永不停止)

## 配置优先级

环境变量 > 配置文件账号设置 > 全局默认值

## 注意

- Twitter 凭据从 Developer Portal 获取
- 时区影响定时任务
- 日志: scheduler.log, tweet_history_{account}.log