import os
from dotenv import load_dotenv
from openai import OpenAI
import tweepy

# 强制使用 UTF-8 环境
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_connectivity():
    print("--- 1. 测试 AI 接口可访问性 ---")
    ai_key = os.getenv('OPENAI_API_KEY')
    ai_base = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    ai_model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    
    # 检查是否包含占位符
    if "你的" in str(ai_key):
        print("❌ 错误: 请在 .env 中将 '你的_GITHUB_TOKEN' 替换为真实的 Token")
        return

    try:
        ai_client = OpenAI(api_key=ai_key, base_url=ai_base)
        response = ai_client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        print(f"✅ AI 响应成功: {response.choices[0].message.content.strip()}")
    except Exception as e:
        print(f"❌ AI 接口故障: {e}")

    print("\n--- 2. 测试 Twitter API 凭证有效性 ---")
    try:
        client = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        me = client.get_me()
        print(f"✅ Twitter 认证成功! 当前账号: @{me.data.username}")
    except Exception as e:
        print(f"❌ Twitter 认证失败: {e}")

if __name__ == "__main__":
    test_connectivity()
