import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import tweepy
from openai import OpenAI

# 配置日志（将在main中重新配置）
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化内存中的 last_mention_ids
last_mention_ids = {}

# 初始化 AI 客户端
ai_client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
)

# 初始化 Twitter API 客户端
def init_twitter_clients(config):
    """初始化多个 Twitter API 客户端"""
    clients = {}
    accounts = config.get('accounts', [])
    for account in accounts:
        name = account['name']
        api_key = account['api_key']
        api_secret = account['api_secret']
        access_token = account['access_token']
        access_token_secret = account['access_token_secret']
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN', account.get('bearer_token'))
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            logger.error(f"❌ 账号 {name} 缺少必要凭据")
            continue
        
        try:
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            clients[name] = client
            logger.info(f"✅ 账号 {name} Twitter API 客户端已连接")
        except Exception as e:
            logger.error(f"❌ 初始化账号 {name} 客户端失败: {e}")
    return clients


# 全局客户端字典（在main中初始化）
twitter_clients = {}


def load_config():
    """加载配置文件"""
    with open('CONTENT_config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def send_tweet(client, account_name, message, in_reply_to_tweet_id=None):
    """发送推文"""
    if not client:
        logger.error(f"❌ 账号 {account_name} Twitter 客户端未初始化，无法发送推文")
        return False
    
    try:
        # 使用 v2 API 创建推文
        if in_reply_to_tweet_id:
            response = client.create_tweet(text=message, in_reply_to_tweet_id=in_reply_to_tweet_id)
        else:
            response = client.create_tweet(text=message)
            
        tweet_id = response.data['id']
        logger.info(f"✅ 账号 {account_name} 推文已发送 (ID: {tweet_id}): {message}")
        
        # 记录到历史文件
        with open(f'tweet_history_{account_name}.log', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - ID: {tweet_id} - {message}\n")

        # 非回复推文：记录 ID 并立即触发本地 ID 驱动的自动转发
        if not in_reply_to_tweet_id:
            with open(f'local_tweet_ids_{account_name}.log', 'a', encoding='utf-8') as f:
                f.write(f"{tweet_id}\n")
            process_local_tweet_id_retweets(account_name)
        
        return True
    except tweepy.TweepyException as e:
        logger.error(f"❌ 账号 {account_name} 发送失败: {e}")
        return False


def process_local_tweet_id_retweets(source_account_name):
    """基于本地记录的推文 ID 进行自动转发（不扫描时间线）"""
    source_ids_file = f'local_tweet_ids_{source_account_name}.log'
    if not os.path.exists(source_ids_file):
        return

    try:
        with open(source_ids_file, 'r', encoding='utf-8') as f:
            source_tweet_ids = [line.strip() for line in f if line.strip()]

        if not source_tweet_ids:
            return

        config = load_config()
        accounts = config.get('accounts', [])

        for account in accounts:
            target_account_name = account.get('name')
            runtime = account.get('runtime', {})

            if not runtime.get('enable_auto_retweet_from_account', False):
                continue
            if runtime.get('auto_retweet_source_account') != source_account_name:
                continue

            target_client = twitter_clients.get(target_account_name)
            if not target_client:
                logger.warning(f"⚠️ 自动转发跳过：账号 {target_account_name} 客户端未初始化")
                continue

            retweeted_file = f'retweeted_{target_account_name}_from_{source_account_name}.log'
            retweeted_ids = set()
            if os.path.exists(retweeted_file):
                with open(retweeted_file, 'r', encoding='utf-8') as f:
                    retweeted_ids = {line.strip() for line in f if line.strip()}

            for tweet_id in source_tweet_ids:
                if tweet_id in retweeted_ids:
                    continue

                try:
                    target_client.retweet(tweet_id, user_auth=True)
                    logger.info(
                        f"🔁 账号 {target_account_name} 已转发 {source_account_name} 的推文 (ID: {tweet_id})"
                    )
                    with open(retweeted_file, 'a', encoding='utf-8') as f:
                        f.write(f"{tweet_id}\n")
                    retweeted_ids.add(tweet_id)
                except Exception as e:
                    logger.error(
                        f"❌ 账号 {target_account_name} 转发 {source_account_name} 推文失败 (ID: {tweet_id}): {e}"
                    )
    except Exception as e:
        logger.error(f"❌ 处理本地推文 ID 自动转发失败 ({source_account_name}): {e}")


def generate_ai_content(prompt, context="", account_config=None):
    """使用 AI 生成推文内容"""
    try:
        if account_config is None:
            config = load_config()
            ai_cfg = config.get('ai_settings', {})
        else:
            ai_cfg = account_config.get('ai_settings', {})
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


def check_mentions_and_reply(client, account_name, account_config):
    """检查提及并自动回复（限制1层）"""
    if not client:
        return

    try:
        # 获取机器人自身的 ID
        me = client.get_me(user_auth=True).data
        bot_id = me.id
        
        # 获取上次处理的最后一个 tweet ID（从内存中）
        last_id = last_mention_ids.get(account_name, None)
        
        # 获取最近的提及，只获取新的（如果有last_id）
        mentions = client.get_users_mentions(
            id=bot_id, 
            tweet_fields=['created_at', 'conversation_id', 'referenced_tweets'],
            #max_results=100,  # 设置为最大值以处理更多新提及
            since_id=last_id,
            user_auth=True
        )
        
        if not mentions.data:
            return

        # 读取已回复的 ID 列表（简单去重）
        replied_ids = []
        replied_file = f'replied_tweets_{account_name}.log'
        if os.path.exists(replied_file):
            with open(replied_file, 'r') as f:
                replied_ids = [line.strip() for line in f.readlines()]

        max_tweet_id = last_id or 0
        for tweet in mentions.data:
            tweet_id = str(tweet.id)
            logger.info(f"账号 {account_name} 检测到提及: {tweet.text[:50]}... (ID: {tweet_id})")
            if tweet_id in replied_ids:
                logger.info(f"账号 {account_name} 跳过: 已回复 (ID: {tweet_id})")
                continue
            
            # --- 检查是否仅提及本账号 ---
            import re
            mentioned_users = re.findall(r'@(\w+)', tweet.text)
            if len(mentioned_users) > 1 or (len(mentioned_users) == 1 and mentioned_users[0].lower() != me.username.lower()):
                logger.info(f"账号 {account_name} 跳过: 提及了其他账号或多个账号 (ID: {tweet_id})")
                continue

            logger.info(f"账号 {account_name} 处理提及: {tweet.text[:50]}... (ID: {tweet_id})")

            logger.info(f"🔍 账号 {account_name} 发现新的提及: {tweet.text}")
            
            # 从 config 获取回复指令
            reply_instruction = account_config.get('ai_settings', {}).get('prompts', {}).get('reply', {}).get('instruction', os.getenv('AI_REPLY_PROMPT', '请根据上下文简短地回复这条推文。'))
            reply_content = generate_ai_content(reply_instruction, context=tweet.text, account_config=account_config)
            
            if reply_content:
                if send_tweet(client, account_name, reply_content, in_reply_to_tweet_id=tweet.id):
                    # 标记为已回复
                    with open(replied_file, 'a') as f:
                        f.write(f"{tweet_id}\n")
                    
                    # 自动点赞提及的推文（如果启用）
                    if account_config.get('runtime', {}).get('enable_auto_like_mentions', False):
                        try:
                            client.like(tweet.id, user_auth=True)
                            logger.info(f"❤️ 账号 {account_name} 自动点赞了提及推文 (ID: {tweet.id})")
                        except Exception as e:
                            logger.error(f"❌ 账号 {account_name} 点赞失败 (ID: {tweet.id}): {e}")
            
            # 更新最大tweet_id
            max_tweet_id = max(max_tweet_id, tweet.id)
        
        # 更新last_mention_id（在内存中）
        if max_tweet_id > (last_id or 0):
            last_mention_ids[account_name] = max_tweet_id
                
    except Exception as e:
        logger.error(f"❌ 账号 {account_name} 自动回复循环出错: {e}")


def send_scheduled_ai_tweet(client, account_name, prompt_type, account_config):
    """定时任务调用的 AI 发推函数"""
    if not client:
        return

    prompts = account_config.get('ai_settings', {}).get('prompts', {})
    
    if prompt_type in prompts:
        prompt = prompts[prompt_type].get('instruction')
        
        if not prompt:
            logger.error(f"❌ 账号 {account_name} 配置文件中 {prompt_type} 缺少 instruction")
            return

        message = generate_ai_content(prompt, account_config=account_config)
        if message:
            send_tweet(client, account_name, message)
    else:
        logger.error(f"❌ 账号 {account_name} 配置文件中找不到任务类型: {prompt_type}")


def schedule_tweets(clients, config):
    """根据配置文件安排定时推文"""
    scheduler = BackgroundScheduler()
    
    accounts = config.get('accounts', [])
    
    for account in accounts:
        account_name = account['name']
        client = clients.get(account_name)
        if not client:
            logger.warning(f"⚠️ 跳过账号 {account_name}，客户端未初始化")
            continue
        
        timezone = account.get('timezone', 'Asia/Shanghai')
        prompts = account.get('ai_settings', {}).get('prompts', {})
        runtime = account.get('runtime', {})
        enable_auto_reply = runtime.get('enable_auto_reply', True)
        
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
                    args=[client, account_name, p_type, account],
                    id=f"ai_tweet_{account_name}_{p_type}",
                    name=f"{account_name} {p_type} AI 发推"
                )
                logger.info(f"📅 已安排账号 {account_name}: {p_type} 任务，时间 {time_str}")

        # 如果启用自动回复，添加检查任务
        if enable_auto_reply:
            interval = runtime.get('check_mentions_interval_minutes', 30)
            scheduler.add_job(
                check_mentions_and_reply,
                'interval',
                minutes=interval,
                args=[client, account_name, account],
                id=f'check_mentions_{account_name}',
                name=f'{account_name} 自动检查提及并回复'
            )
            logger.info(f"📅 已启用账号 {account_name} 自动回复，每 {interval} 分钟检查")
        else:
            logger.info(f"📅 账号 {account_name} 自动回复已关闭")

        # 自动转发由 send_tweet 成功后基于本地 ID 直接触发，无需扫描任务
        if runtime.get('enable_auto_retweet_from_account', False):
            source_account_name = runtime.get('auto_retweet_source_account')
            if source_account_name:
                logger.info(
                    f"📅 账号 {account_name} 已启用本地 ID 驱动自动转发，来源账号: {source_account_name}"
                )
            else:
                logger.warning(
                    f"⚠️ 账号 {account_name} 已开启自动转发，但未配置 auto_retweet_source_account"
                )
    
    return scheduler


def main():
    """主函数"""
    import time
    
    # 处理日志文件：保留上一run的log，新建当前run的log
    old_log = 'scheduler_old.log'
    current_log = 'scheduler.log'
    
    # 删除旧的old log
    if os.path.exists(old_log):
        os.remove(old_log)
    
    # 将当前的log重命名为old
    if os.path.exists(current_log):
        os.rename(current_log, old_log)
    
    # 配置日志写入新文件
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=current_log,
        filemode='w'
    )
    
    # 加载配置并初始化客户端
    config = load_config()
    global twitter_clients
    twitter_clients = init_twitter_clients(config)
    
    # 重新加载 config 获取运行时长（使用第一个账号的设置作为全局默认）
    accounts = config.get('accounts', [])
    if accounts:
        default_runtime = accounts[0].get('runtime', {})
    else:
        default_runtime = {}
    
    logger.info("🚀 启动定时发推服务...")
    
    # 如果是测试模式，先发送测试推文
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    if test_mode:
        for account_name, client in twitter_clients.items():
            if client:
                logger.info(f"🧪 测试模式：账号 {account_name} 发送测试推文...")
                send_tweet(client, account_name, "🤖 测试推文 - 如果你看到这条，说明 API 正常运行！")
    
    # 启动定时调度器
    scheduler = schedule_tweets(twitter_clients, config)
    scheduler.start()
    
    # 获取运行时长（使用第一个账号的设置）
    run_hours = default_runtime.get('run_hours', int(os.getenv('RUN_HOURS', '24')))
    
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
