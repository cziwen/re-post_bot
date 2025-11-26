import logging
from typing import List, Optional
from atproto import Client, models
from database import Database

logger = logging.getLogger(__name__)


class ReplyManager:
    def __init__(self, client: Client, db: Database, config: dict):
        self.client = client
        self.db = db
        self.config = config

    def get_notifications(self) -> List[dict]:
        """Get recent notifications (mentions and replies)"""
        try:
            response = self.client.app.bsky.notification.list_notifications(
                params={'limit': 50}
            )

            notifications = []
            if hasattr(response, 'notifications'):
                for notif in response.notifications:
                    # Filter for replies only
                    if notif.reason == 'reply':
                        notifications.append({
                            'uri': notif.uri,
                            'cid': notif.cid,
                            'author': notif.author.handle,
                            'record': notif.record,
                            'reason': notif.reason
                        })

            return notifications
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []

    def get_post_replies(self, post_uri: str) -> List[dict]:
        """Get replies to a specific post"""
        try:
            # Extract the post thread
            response = self.client.app.bsky.feed.get_post_thread(
                params={'uri': post_uri}
            )

            replies = []
            if hasattr(response, 'thread') and hasattr(response.thread, 'replies'):
                for reply in response.thread.replies:
                    if hasattr(reply, 'post'):
                        post = reply.post
                        replies.append({
                            'uri': post.uri,
                            'cid': post.cid,
                            'author': post.author.handle,
                            'text': post.record.text if hasattr(post.record, 'text') else '',
                            'created_at': post.record.created_at if hasattr(post.record, 'created_at') else None
                        })

            return replies
        except Exception as e:
            logger.error(f"Error getting post replies: {e}")
            return []

    def detect_keywords(self, text: str) -> Optional[str]:
        """Detect keywords in text and return appropriate response"""
        text_lower = text.lower()

        keyword_responses = self.config.get('auto_reply', {}).get('keyword_responses', {})

        for keyword, response in keyword_responses.items():
            if keyword.lower() in text_lower:
                return response

        return None

    def send_reply(self, parent_post: dict, reply_text: str) -> bool:
        """Send a reply to a post"""
        try:
            # Create reply reference
            reply_ref = models.AppBskyFeedPost.ReplyRef(
                parent=models.create_strong_ref(
                    models.ComAtprotoRepoStrongRef.Main(
                        uri=parent_post['uri'],
                        cid=parent_post['cid']
                    )
                ),
                root=models.create_strong_ref(
                    models.ComAtprotoRepoStrongRef.Main(
                        uri=parent_post['uri'],
                        cid=parent_post['cid']
                    )
                )
            )

            # Send reply
            self.client.send_post(
                text=reply_text,
                reply_to=reply_ref
            )

            logger.info(f"Sent reply to @{parent_post['author']}: {reply_text}")
            return True

        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False

    def process_new_replies(self):
        """Process new replies and send auto-responses"""
        logger.info("Checking for new replies...")

        # Get recent reposts from database
        recent_reposts = self.db.get_recent_reposts(limit=20)

        reply_count = 0

        for repost in recent_reposts:
            if not repost['repost_uri']:
                continue

            # Get replies to this repost
            replies = self.get_post_replies(repost['repost_uri'])

            for reply in replies:
                # Skip if already processed
                if self.db.is_reply_processed(reply['uri']):
                    continue

                # Skip own replies
                if reply['author'] == self.client.me.handle:
                    continue

                # Detect keywords and get response
                response_text = self.detect_keywords(reply['text'])

                if response_text:
                    logger.info(f"Found keyword in reply from @{reply['author']}: {reply['text'][:50]}...")
                    if self.send_reply(reply, response_text):
                        reply_count += 1
                        # Mark as processed
                        self.db.add_processed_reply(
                            reply['uri'],
                            repost['repost_uri'],
                            reply['author'],
                            reply['text']
                        )
                else:
                    # Use default response if configured
                    default_response = self.config.get('auto_reply', {}).get('default_response')
                    if default_response:
                        if self.send_reply(reply, default_response):
                            reply_count += 1
                            self.db.add_processed_reply(
                                reply['uri'],
                                repost['repost_uri'],
                                reply['author'],
                                reply['text']
                            )

        logger.info(f"Processed {reply_count} new replies.")

    def monitor_notifications(self):
        """Monitor notifications for replies and respond"""
        logger.info("Monitoring notifications...")

        notifications = self.get_notifications()
        reply_count = 0

        for notif in notifications:
            # Skip if already processed
            if self.db.is_reply_processed(notif['uri']):
                continue

            # Skip own posts
            if notif['author'] == self.client.me.handle:
                continue

            # Extract text from record
            text = ''
            if hasattr(notif['record'], 'text'):
                text = notif['record'].text

            # Detect keywords and respond
            response_text = self.detect_keywords(text)

            if not response_text:
                response_text = self.config.get('auto_reply', {}).get('default_response')

            if response_text:
                logger.info(f"Responding to notification from @{notif['author']}")
                if self.send_reply(notif, response_text):
                    reply_count += 1
                    self.db.add_processed_reply(
                        notif['uri'],
                        notif['uri'],  # Parent is the notification itself
                        notif['author'],
                        text
                    )

        logger.info(f"Responded to {reply_count} notifications.")
