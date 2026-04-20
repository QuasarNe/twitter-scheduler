import os
import tweepy
from dotenv import load_dotenv

def get_new_user_tokens():
    load_dotenv()
    
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ 错误: 请确保 .env 中已设置 TWITTER_API_KEY 和 TWITTER_API_SECRET")
        return

    # 初始化 OAuth 1.0a 认证
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, callback='oob')

    try:
        # 获取授权 URL
        auth_url = auth.get_authorization_url()
        print("\n" + "="*50)
        print("🚀 第一步: 请在浏览器中登录你想【发推】的账号")
        print("🔗 第二步: 访问以下链接并点击 'Authorize app':")
        print(f"\n{auth_url}\n")
        print("="*50)
        
        # 获取用户输入的 PIN 码
        verifier = input("请输入授权后显示的 PIN 码: ").strip()
        
        # 获取 Access Token 和 Secret
        access_token, access_token_secret = auth.get_access_token(verifier)
        
        print("\n✅ 授权成功！")
        print("-" * 30)
        print(f"新 Access Token: {access_token}")
        print(f"新 Access Token Secret: {access_token_secret}")
        print("-" * 30)
        print("\n💡 正在自动更新 .env 文件...")
        
        # 更新 .env 文件
        update_env(access_token, access_token_secret)
        
    except Exception as e:
        print(f"❌ 授权失败: {e}")

def update_env(token, secret):
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    # 标注旧配置
    for line in lines:
        if line.startswith('TWITTER_ACCESS_TOKEN='):
            new_lines.append(f"# 旧 Token: {line.strip()}\n")
            new_lines.append(f"TWITTER_ACCESS_TOKEN={token}\n")
        elif line.startswith('TWITTER_ACCESS_TOKEN_SECRET='):
            new_lines.append(f"# 旧 Secret: {line.strip()}\n")
            new_lines.append(f"TWITTER_ACCESS_TOKEN_SECRET={secret}\n")
        else:
            new_lines.append(line)
            
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✨ .env 文件已更新，现在可以使用新账号发推了！")

if __name__ == "__main__":
    get_new_user_tokens()
