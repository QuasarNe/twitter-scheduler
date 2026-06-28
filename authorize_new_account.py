import os

import tweepy
from dotenv import load_dotenv


def get_new_user_tokens():
    load_dotenv()

    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')

    if not api_key or not api_secret:
        print('❌ 错误: 请确保 .env 中已设置 TWITTER_API_KEY 和 TWITTER_API_SECRET')
        return

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, callback='oob')

    try:
        auth_url = auth.get_authorization_url()
        print('\n' + '=' * 50)
        print('🚀 第一步: 请在浏览器中登录你想【发推】的账号')
        print("🔗 第二步: 访问以下链接并点击 'Authorize app':")
        print(f'\n{auth_url}\n')
        print('=' * 50)

        verifier = input('请输入授权后显示的 PIN 码: ').strip()
        access_token, access_token_secret = auth.get_access_token(verifier)

        print('\n✅ 授权成功！')
        print('-' * 30)
        print('请将下面信息复制到 CONTENT_config.json 对应账号：')
        print(f'Access Token: {access_token}')
        print(f'Access Token Secret: {access_token_secret}')
        print('-' * 30)
        print('💡 如果是新账号，请手动新增到 CONTENT_config.json 的 accounts 列表中。')

    except Exception as e:
        print(f'❌ 授权失败: {e}')


if __name__ == '__main__':
    get_new_user_tokens()
