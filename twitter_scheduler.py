import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import tweepy

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化 Twitter API 客户端
def init_twitter_client():
    """初始化 Twitter API 客户端"""
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        raise ValueError("❌ 错误：请在 .env 文件中设置 TWITTER_BEARER_TOKEN")
    
    client = tweepy.Client(bearer_token=bearer_token)
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
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def send_tweet(message):
    """发送推文"""
    if not twitter_client:
        logger.error("❌ Twitter 客户端未初始化，无法发送推文")
        return False
    
    try:
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


def schedule_tweets():
    """根据配置文件安排定时推文"""
    config = load_config()
    scheduler = BackgroundScheduler()
    
    timezone = config.get('timezone', 'UTC')
    
    for item in config['schedule']:
        time_str = item['time']  # 格式: "09:00"
        message = item['message']
        hour, minute = map(int, time_str.split(':'))
        
        # 安排每天固定时间执行
        scheduler.add_job(
            send_tweet,
            'cron',
            hour=hour,
            minute=minute,
            timezone=timezone,
            args=[message],
            id=f"tweet_{time_str.replace(':', '_')}",
            name=f"每日 {time_str} 发送推文"
        )
        logger.info(f"📅 已安排: 每日 {time_str} 发送 - {message}")
    
    return scheduler


def main():
    """主函数"""
    logger.info("🚀 启动定时发推服务...")
    
    # 如果是测试模式，先发送一条测试推文
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    if test_mode and twitter_client:
        logger.info("🧪 测试模式：发送测试推文...")
        send_tweet("🤖 测试推文 - 如果你看到这条，说明 API 正常运行！")
    
    # 启动定时调度器
    scheduler = schedule_tweets()
    scheduler.start()
    
    logger.info("✅ 定时发推服务已启动，按 Ctrl+C 停止")
    
    try:
        # 保持服务运行
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 收到停止信号，正在关闭...")
        scheduler.shutdown()
        logger.info("👋 服务已关闭")


if __name__ == '__main__':
    main()
