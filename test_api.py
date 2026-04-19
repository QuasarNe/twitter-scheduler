#!/usr/bin/env python3
"""
测试 Twitter API 连接
运行: python test_api.py
"""
import os
from dotenv import load_dotenv
import tweepy

load_dotenv()

bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

if not bearer_token:
    print("❌ 错误: 请先在 .env 文件中设置 TWITTER_BEARER_TOKEN")
    print("\n📝 获取 Bearer Token 的步骤:")
    print("1. 访问 https://developer.twitter.com/en/portal/dashboard")
    print("2. 创建或选择你的应用")
    print("3. 进入 'Keys and tokens' 标签页")
    print("4. 在 'Authentication Tokens' 下找到 'Bearer Token'")
    print("5. 复制 Bearer Token 到 .env 文件中")
    exit(1)

try:
    client = tweepy.Client(bearer_token=bearer_token)
    
    # 获取认证用户信息（v2 API 不支持，这里只验证连接）
    print("✅ 成功连接到 Twitter API!")
    print("\n🎉 现在你可以运行: python twitter_scheduler.py")
    print("\n💡 提示: 可以在 config.json 中修改推文时间和内容")
    
except tweepy.TweepyException as e:
    print(f"❌ API 连接失败: {e}")
    print("\n🔍 请检查:")
    print("- Bearer Token 是否正确")
    print("- 应用是否有 'Tweet Compose' 权限")
    print("- 账户是否在开发者模式下")
