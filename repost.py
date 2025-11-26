import logging
from typing import List, Optional
from atproto import Client, models
from database import Database
import json

logger = logging.getLogger(__name__)


class RepostManager:
    def __init__(self, client: Client, db: Database, config: dict):
        self.client = client
        self.db = db
        self.config = config

    def search_posts(self, query: str, limit: int = 25) -> List[dict]:
        """Search for posts matching the query"""
        try:
            response = self.client.app.bsky.feed.search_posts(
                params={'q': query, 'limit': limit}
            )

            posts = []
            if hasattr(response, 'posts'):
                for post in response.posts:
                    posts.append({
                        'uri': post.uri,
                        'cid': post.cid,
                        'author': post.author.handle,
                        'text': post.record.text if hasattr(post.record, 'text') else '',
                        'created_at': post.record.created_at if hasattr(post.record, 'created_at') else None
                    })

            return posts
        except Exception as e:
            logger.error(f"Error searching posts: {e}")
            return []

    def should_repost(self, post: dict) -> bool:
        """Determine if a post should be reposted"""
        # Check if already reposted
        if self.db.is_post_reposted(post['uri']):
            return False

        # Check if post contains target keywords or tags
        text = post.get('text', '').lower()

        # Check tags
        tags = self.config.get('search', {}).get('tags', [])
        for tag in tags:
            if tag.lower() in text:
                return True

        # Check keywords
        keywords = self.config.get('search', {}).get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in text:
                return True

        return False

    def repost_with_comment(self, post: dict) -> Optional[str]:
        """Repost a post and add a preset comment"""
        try:
            # Create repost
            repost_ref = models.create_strong_ref(
                models.ComAtprotoRepoStrongRef.Main(
                    uri=post['uri'],
                    cid=post['cid']
                )
            )

            repost_response = self.client.app.bsky.feed.repost.create(
                self.client.me.did,
                models.AppBskyFeedRepost.Record(
                    subject=repost_ref,
                    created_at=self.client.get_current_time_iso()
                )
            )

            logger.info(f"Reposted: {post['uri']}")

            # Add preset comment as a reply to the original post
            preset_comment = self.config.get('repost', {}).get('preset_comment', '')
            if preset_comment:
                self.add_comment(post, preset_comment)

            # Record in database
            repost_uri = f"at://{self.client.me.did}/app.bsky.feed.repost/{repost_response.cid}"
            self.db.add_reposted_post(post['uri'], post['author'], repost_uri)

            return repost_uri

        except Exception as e:
            logger.error(f"Error reposting: {e}")
            return None

    def add_comment(self, post: dict, comment_text: str):
        """Add a comment to a post"""
        try:
            # Create reply reference
            reply_ref = models.AppBskyFeedPost.ReplyRef(
                parent=models.create_strong_ref(
                    models.ComAtprotoRepoStrongRef.Main(
                        uri=post['uri'],
                        cid=post['cid']
                    )
                ),
                root=models.create_strong_ref(
                    models.ComAtprotoRepoStrongRef.Main(
                        uri=post['uri'],
                        cid=post['cid']
                    )
                )
            )

            # Create post record with reply
            self.client.send_post(
                text=comment_text,
                reply_to=reply_ref
            )

            logger.info(f"Added comment to post: {post['uri']}")

        except Exception as e:
            logger.error(f"Error adding comment: {e}")

    def run_repost_cycle(self):
        """Run one cycle of searching and reposting"""
        logger.info("Starting repost cycle...")

        max_reposts = self.config.get('repost', {}).get('max_reposts_per_run', 5)
        repost_count = 0

        # Search for posts with tags
        tags = self.config.get('search', {}).get('tags', [])
        keywords = self.config.get('search', {}).get('keywords', [])

        search_queries = tags + keywords

        for query in search_queries:
            if repost_count >= max_reposts:
                break

            logger.info(f"Searching for: {query}")
            posts = self.search_posts(query)

            for post in posts:
                if repost_count >= max_reposts:
                    break

                if self.should_repost(post):
                    logger.info(f"Found post to repost from @{post['author']}: {post['text'][:50]}...")
                    if self.repost_with_comment(post):
                        repost_count += 1

        logger.info(f"Repost cycle completed. Reposted {repost_count} posts.")
