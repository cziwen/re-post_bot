# Bluesky Repost Bot

A simple, self-contained Jupyter notebook bot for Bluesky that automatically reposts content and replies to comments.

## Features

- Search posts by hashtags and keywords
- Auto-repost with custom comments
- Auto-reply to comments with keyword detection
- SQLite database to prevent duplicates
- Easy configuration

## Quick Start

### 1. Install Dependencies

```bash
pip install atproto>=0.0.55 schedule>=1.2.0
```

### 2. Run the Notebook

Open `bot.ipynb` in Jupyter and run cells sequentially:

1. **Cells 1-3**: Install and import dependencies
2. **Cells 4-6**: Define classes (Database, RepostManager, ReplyManager)
3. **Cell 7**: Configure bot settings
4. **Cell 8**: Enter your Bluesky credentials
5. **Cell 9**: Initialize bot components
6. **Cell 10**: Run a single bot cycle (manual)
7. **Cell 11**: View statistics
8. **Cell 12**: (Optional) Run continuously

### 3. Configure

Edit the configuration in Cell 7:

```python
config = {
    "search": {
        "tags": ["#AI", "#Tech"],           # Hashtags to search
        "keywords": ["Gemini", "ChatGPT"],  # Keywords to search
        "check_interval_minutes": 10        # For continuous mode
    },
    "repost": {
        "preset_comment": "Your comment here",
        "max_reposts_per_run": 1
    },
    "auto_reply": {
        "keyword_responses": {
            "thank": "You're welcome!",
            "help": "Happy to help!"
        },
        "default_response": "Thank you for your comment!"
    }
}
```

## How It Works

1. **Search**: Finds posts matching your tags/keywords
2. **Repost**: Reposts posts to your profile with a comment
3. **Auto-reply**: Monitors comments and replies based on keywords
4. **Database**: Tracks reposts and replies to avoid duplicates

## File Structure

```
Re-Post_Bot/
├── bot.ipynb           # Main notebook (all-in-one)
├── config.json         # Configuration (optional reference)
├── posts.db           # SQLite database (auto-created)
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## Usage Modes

### Manual Mode (Recommended for Testing)
Run Cell 10 whenever you want to check for new posts and replies.

### Continuous Mode (Recommended for Deployment)
Run Cell 12 to automatically run the bot every N minutes.

## Notes

- Database file `posts.db` is created automatically
- Reposts appear on your Bluesky profile
- Comments appear as replies to the original posts
- Cell 15 can reset the database if needed
- No separate Python files needed - everything is in `bot.ipynb`

## Troubleshooting

### Can't see new posts?
- Reposts appear on your profile, not as new posts
- Check https://bsky.app/profile/YOUR_HANDLE

### Auto-reply not working?
- Wait for someone to comment on your reposts
- Run Cell 10 again to check for new comments

### Want to start fresh?
- Run Cell 15 (uncomment code) to reset database

## License

MIT
