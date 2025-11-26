import sqlite3
from datetime import datetime
from typing import Optional, List


class Database:
    def __init__(self, db_path: str = "posts.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table for reposted posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reposted_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_uri TEXT UNIQUE NOT NULL,
                original_author TEXT NOT NULL,
                repost_uri TEXT,
                reposted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table for processed replies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reply_uri TEXT UNIQUE NOT NULL,
                parent_post_uri TEXT NOT NULL,
                author TEXT NOT NULL,
                content TEXT,
                replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def is_post_reposted(self, post_uri: str) -> bool:
        """Check if a post has already been reposted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM reposted_posts WHERE original_uri = ?",
            (post_uri,)
        )
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def add_reposted_post(self, original_uri: str, original_author: str, repost_uri: Optional[str] = None):
        """Record a reposted post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO reposted_posts (original_uri, original_author, repost_uri) VALUES (?, ?, ?)",
                (original_uri, original_author, repost_uri)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Already exists
            pass
        finally:
            conn.close()

    def is_reply_processed(self, reply_uri: str) -> bool:
        """Check if a reply has already been processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM processed_replies WHERE reply_uri = ?",
            (reply_uri,)
        )
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def add_processed_reply(self, reply_uri: str, parent_post_uri: str, author: str, content: str):
        """Record a processed reply"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO processed_replies (reply_uri, parent_post_uri, author, content) VALUES (?, ?, ?, ?)",
                (reply_uri, parent_post_uri, author, content)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # Already exists
            pass
        finally:
            conn.close()

    def get_recent_reposts(self, limit: int = 10) -> List[dict]:
        """Get recent reposted posts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT original_uri, original_author, repost_uri, reposted_at FROM reposted_posts ORDER BY reposted_at DESC LIMIT ?",
            (limit,)
        )
        results = cursor.fetchall()
        conn.close()

        return [
            {
                "original_uri": row[0],
                "original_author": row[1],
                "repost_uri": row[2],
                "reposted_at": row[3]
            }
            for row in results
        ]
