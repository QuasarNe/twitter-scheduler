import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import tweepy
from openai import OpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化 AI 客户端
ai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
)

# 初始化 Twitter API 客户端
def init_twitter_client():
    """初始化 Twitter API 客户端"""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError("❌ 错误：请在 .env 文件中设置 TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
    
    # 使用 Tweepy v2 Client 以支持 OAuth 1.0a 访问 v2 接口
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    return client


# 全局客户端
try:
    twitter_client = init_twitter_client()
    logger.info("✅ Twitter API 客户端已连接")
except Exception as e:
    logger.error(f"❌ 初始化 Twitter 客户端失败: {e}")
    twitter_client = None


def load_config():
    """加载配置文件"""
    with open('CONTENT_config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def send_tweet(message, in_reply_to_tweet_id=None):
    """发送推文"""
    if not twitter_client:
        logger.error("❌ Twitter 客户端未初始化，无法发送推文")
        return False
    
    try:
        # 使用 v2 API 创建推文
        if in_reply_to_tweet_id:
            response = twitter_client.create_tweet(text=message, in_reply_to_tweet_id=in_reply_to_tweet_id)
        else:
            response = twitter_client.create_tweet(text=message)
            
        tweet_id = response.data['id']
        logger.info(f"✅ 推文已发送 (ID: {tweet_id}): {message}")
        
        # 记录到历史文件
        with open('tweet_history.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - ID: {tweet_id} - {message}\n")
        
        return True
    except tweepy.TweepyException as e:
        logger.error(f"❌ 发送失败: {e}")
        return False


def generate_ai_content(prompt, context=""):
    """使用 AI 生成推文内容"""
    try:
        config = load_config()
        ai_cfg = config.get('ai_settings', {})
        system_prompt = ai_cfg.get('system_prompt', os.getenv('AI_SYSTEM_PROMPT', '你是一个推特博主。'))
        model = ai_cfg.get('model', os.getenv('AI_MODEL', 'gpt-4o'))
        
        response = ai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prompt}\n\n参考内容/上下文: {context}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"❌ AI 生成失败: {e}")
        return None


def check_mentions_and_reply():
    """检查提及并自动回复（限制1层）"""
    if not twitter_client:
        return

    try:
        config = load_config()
        # 获取机器人自身的 ID
        me = twitter_client.get_me(user_auth=True).data
        bot_id = me.id
        
        # 获取最近的提及
        # 注意：需要权限支持收听 Mentions
        mentions = twitter_client.get_users_mentions(
            id=bot_id, 
            tweet_fields=['created_at', 'conversation_id', 'referenced_tweets'],
            max_results=10,
            user_auth=True
        )
        
        if not mentions.data:
            return

        # 读取已回复的 ID 列表（简单去重）
        replied_ids = []
        if os.path.exists('replied_tweets.log'):
            with open('replied_tweets.log', 'r') as f:
                replied_ids = [line.strip() for line in f.readlines()]

        for tweet in mentions.data:
            tweet_id = str(tweet.id)
            logger.info(f"检测到提及: {tweet.text[:50]}... (ID: {tweet_id})")
            if tweet_id in replied_ids:
                logger.info(f"跳过: 已回复 (ID: {tweet_id})")
                continue
            
            # --- 检查是否仅提及本账号 ---
            import re
            mentioned_users = re.findall(r'@(\w+)', tweet.text)
            if len(mentioned_users) > 1 or (len(mentioned_users) == 1 and mentioned_users[0].lower() != me.username.lower()):
                logger.info(f"跳过: 提及了其他账号或多个账号 (ID: {tweet_id})")
                continue

            logger.info(f"处理提及: {tweet.text[:50]}... (ID: {tweet_id})")

            logger.info(f"🔍 发现新的提及: {tweet.text}")
            
            # 从 config 获取回复指令
            reply_instruction = config.get('ai_settings', {}).get('prompts', {}).get('reply', {}).get('instruction', os.getenv('AI_REPLY_PROMPT', '请根据上下文简短地回复这条推文。'))
            reply_content = generate_ai_content(reply_instruction, context=tweet.text)
            
            if reply_content:
                if send_tweet(reply_content, in_reply_to_tweet_id=tweet.id):
                    # 标记为已回复
                    with open('replied_tweets.log', 'a') as f:
                        f.write(f"{tweet_id}\n")
                
    except Exception as e:
        logger.error(f"❌ 自动回复循环出错: {e}")


def send_scheduled_ai_tweet(prompt_type):
    """定时任务调用的 AI 发推函数"""
    if not twitter_client:
        return

    config = load_config()
    prompts = config.get('ai_settings', {}).get('prompts', {})
    
    if prompt_type in prompts:
        prompt = prompts[prompt_type].get('instruction')
        
        if not prompt:
            logger.error(f"❌ 配置文件中 {prompt_type} 缺少 instruction")
            return

        message = generate_ai_content(prompt)
        if message:
            send_tweet(message)
    else:
        logger.error(f"❌ 配置文件中找不到任务类型: {prompt_type}")


def schedule_tweets():
    """根据配置文件安排定时推文"""
    config = load_config()
    scheduler = BackgroundScheduler()
    
    timezone = config.get('timezone', 'Asia/Shanghai')
    prompts = config.get('ai_settings', {}).get('prompts', {})
    
    # 根据 config 中的 prompts 配置定时任务
    for p_type, p_info in prompts.items():
        if 'time' in p_info:
            time_str = p_info['time']
            hour, minute = map(int, time_str.split(':'))
            
            scheduler.add_job(
                send_scheduled_ai_tweet,
                'cron',
                hour=hour,
                minute=minute,
                timezone=timezone,
                args=[p_type],
                id=f"ai_tweet_{p_type}",
                name=f"猫少年 {p_type} AI 发推"
            )
            logger.info(f"📅 已安排: {p_type} 任务，时间 {time_str}")

    # 获取自动回复检查间隔
    interval = config.get('runtime', {}).get('check_mentions_interval_minutes', 5)
    scheduler.add_job(
        check_mentions_and_reply,
        'interval',
        minutes=interval,
        id='check_mentions',
        name='自动检查提及并回复'
    )
    
    return scheduler


def main():
    """主函数"""
    import time
    
    # 重新加载 config 获取运行时长
    config = load_config()
    runtime_cfg = config.get('runtime', {})
    
    logger.info("🚀 启动定时发推服务...")
    
    # 如果是测试模式，先发送一条测试推文
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    if test_mode and twitter_client:
        logger.info("🧪 测试模式：发送测试推文...")
        send_tweet("🤖 测试推文 - 如果你看到这条，说明 API 正常运行！")
    
    # 启动定时调度器
    scheduler = schedule_tweets()
    scheduler.start()
    
    # 获取运行时长
    run_hours = runtime_cfg.get('run_hours', int(os.getenv('RUN_HOURS', '24')))
    
    try:
        if run_hours == -1:
            logger.info("✅ 定时发推服务已启动，将永不停止运行")
            while True:
                time.sleep(10)
        else:
            run_seconds = run_hours * 3600
            start_time = time.time()
            logger.info(f"✅ 定时发推服务已启动，将在 {run_hours} 小时后自动停止")
            
            while True:
                elapsed = time.time() - start_time
                if elapsed >= run_seconds:
                    logger.info(f"⏰ {run_hours} 小时已到，正在关闭服务...")
                    break
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号，正在关闭...")
    finally:
        scheduler.shutdown()
        logger.info("👋 服务已关闭")


if __name__ == '__main__':
    main()
