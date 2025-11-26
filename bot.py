#!/usr/bin/env python3
"""
Bluesky Repost Bot
Automatically reposts content with specific tags/keywords and responds to comments
"""

import json
import logging
import schedule
import time
from auth import BlueskyAuth
from database import Database
from repost import RepostManager
from reply import ReplyManager


def setup_logging(config: dict):
    """Setup logging configuration"""
    log_level = config.get('logging', {}).get('level', 'INFO')
    log_file = config.get('logging', {}).get('file', 'bot.log')

    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def load_config(config_path: str = 'config.json') -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        raise


def run_bot_cycle(repost_manager: RepostManager, reply_manager: ReplyManager):
    """Run one complete bot cycle"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Starting bot cycle")

    try:
        # Step 1: Search and repost
        repost_manager.run_repost_cycle()

        # Step 2: Monitor and reply to comments
        reply_manager.process_new_replies()

        # Step 3: Monitor notifications
        reply_manager.monitor_notifications()

    except Exception as e:
        logger.error(f"Error in bot cycle: {e}")

    logger.info("Bot cycle completed")
    logger.info("=" * 50)


def main():
    """Main entry point"""
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    logger.info("Bluesky Repost Bot starting...")

    # Initialize components
    auth = BlueskyAuth()
    client = auth.login()
    db = Database()

    repost_manager = RepostManager(client, db, config)
    reply_manager = ReplyManager(client, db, config)

    # Run initial cycle
    run_bot_cycle(repost_manager, reply_manager)

    # Schedule periodic runs
    interval_minutes = config.get('search', {}).get('check_interval_minutes', 10)
    schedule.every(interval_minutes).minutes.do(
        run_bot_cycle,
        repost_manager=repost_manager,
        reply_manager=reply_manager
    )

    logger.info(f"Bot scheduled to run every {interval_minutes} minutes")
    logger.info("Press Ctrl+C to stop")

    # Run scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")


if __name__ == "__main__":
    main()
