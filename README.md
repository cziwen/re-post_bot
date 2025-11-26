# Bluesky Repost Bot 🤖

English | [简体中文](README_CN.md)

A powerful Bluesky automation bot that searches, reposts posts with specific tags or keywords, and automatically replies to comments.

## ✨ Features

- 🔍 **Smart Search**: Search for recent posts based on custom tags and keywords
- 🔄 **Auto Repost**: Automatically repost matching posts to the bot account
- 💬 **Preset Comments**: Add custom comments when reposting
- 🤖 **Smart Reply**: Automatically reply to comments based on keyword detection
- 📊 **Data Tracking**: SQLite database tracks all operations to avoid duplicates
- ⏰ **Scheduled Execution**: Configurable scheduled tasks for automation
- 📝 **Logging**: Complete operation logs for debugging and monitoring

## 📁 Project Structure

```
Re-Post_Bot/
├── .env                # Account credentials (DO NOT commit to Git)
├── .gitignore          # Git ignore file
├── config.json         # Bot configuration file
├── requirements.txt    # Python dependencies
├── bot.py              # Command-line main program
├── bot.ipynb           # Jupyter Notebook interactive version
├── auth.py             # Bluesky authentication module
├── database.py         # SQLite database management
├── repost.py           # Repost functionality module
├── reply.py            # Auto-reply module
├── README.md           # English documentation (this file)
└── README_CN.md        # Chinese documentation
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Account

Edit the `.env` file with your Bluesky account information:

```env
BLUESKY_HANDLE=your_handle.bsky.social
BLUESKY_PASSWORD=your_password
```

### 3. Configure Bot

Edit `config.json` to customize bot behavior:

```json
{
  "search": {
    "tags": ["#AI", "#tech"],              // Tags to search for
    "keywords": ["artificial intelligence", "technology"],  // Keywords to search for
    "check_interval_minutes": 10           // Check interval in minutes
  },
  "repost": {
    "preset_comment": "Sharing an interesting post!",  // Comment when reposting
    "max_reposts_per_run": 5                          // Max reposts per run
  },
  "auto_reply": {
    "keyword_responses": {                 // Keyword -> Response mapping
      "thanks": "You're welcome!",
      "how": "Feel free to ask if you have questions!",
      "price": "Please check our website for pricing information."
    },
    "default_response": "Thanks for your comment!"  // Default response
  }
}
```

### 4. Run the Bot

#### Option 1: Command Line (Recommended for Deployment)

```bash
python bot.py
```

The bot will:
1. Execute a search and repost cycle immediately
2. Process comments and replies
3. Automatically repeat at configured intervals

Press `Ctrl+C` to stop.

#### Option 2: Jupyter Notebook (Recommended for Testing)

```bash
jupyter notebook bot.ipynb
```

The Notebook version provides:
- 📊 Interactive interface
- 🧪 Step-by-step testing
- 📈 Real-time statistics viewing
- 🎛️ Dynamic configuration modification

## 📖 Detailed Documentation

### Workflow

1. **Search Phase**
   - Search Bluesky posts based on configured tags and keywords
   - **Search Logic**: Posts matching **ANY** tag OR **ANY** keyword will be selected (OR relationship, not AND)
   - Check if already reposted (deduplication)
   - Filter qualifying posts

2. **Repost Phase**
   - Repost qualifying posts
   - Add preset comment to original post
   - Record in database

3. **Reply Phase**
   - Monitor comments under bot's reposted posts
   - Detect keywords in comments
   - **Reply Logic**: If the comment contains **ANY** configured keyword, the corresponding response is sent; otherwise, the default response is used
   - Automatically send corresponding replies
   - Record processed comments

### Configuration Details

#### Search Configuration (`search`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `tags` | Array | List of tags to search for, e.g. `["#AI", "#tech"]`. Posts with ANY of these tags will be selected. |
| `keywords` | Array | List of keywords to search for. Posts containing ANY of these keywords will be selected. |
| `check_interval_minutes` | Number | Scheduled task interval in minutes |

**Note**: A post will be reposted if it matches **ANY tag OR ANY keyword** (not both required).

#### Repost Configuration (`repost`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `preset_comment` | String | Comment automatically added when reposting |
| `max_reposts_per_run` | Number | Maximum number of posts to repost per run |

#### Auto-Reply Configuration (`auto_reply`)

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword_responses` | Object | Keyword to response mapping. If a comment contains ANY of these keywords, the corresponding response is sent. |
| `default_response` | String | Default response when no keyword matches |

**Note**: Keywords are matched case-insensitively. The first matching keyword's response will be used.

### Database Structure

The bot uses SQLite database (`posts.db`) to store data:

#### `reposted_posts` Table
- `id`: Primary key
- `original_uri`: Original post URI
- `original_author`: Original author
- `repost_uri`: Repost URI
- `reposted_at`: Repost timestamp

#### `processed_replies` Table
- `id`: Primary key
- `reply_uri`: Reply URI
- `parent_post_uri`: Parent post URI
- `author`: Reply author
- `content`: Reply content
- `replied_at`: Reply timestamp

## 🔧 Advanced Usage

### Custom Keyword Responses

Add more keyword mappings in `config.json`:

```json
"keyword_responses": {
  "thanks": "You're welcome, glad to help!",
  "how to": "Please check our user guide...",
  "price": "Visit our website for pricing...",
  "help": "We're here to help anytime!"
}
```

### Modify Search Scope

Adjust search tags and keywords:

```json
"search": {
  "tags": ["#Python", "#AI", "#MachineLearning"],
  "keywords": ["artificial intelligence", "deep learning", "neural networks"]
}
```

### Adjust Run Frequency

Modify check interval (in minutes):

```json
"search": {
  "check_interval_minutes": 15  // Run every 15 minutes
}
```

### View History

Query the database using Python or Jupyter Notebook:

```python
from database import Database

db = Database()

# Get recent 10 repost records
recent_reposts = db.get_recent_reposts(limit=10)

for repost in recent_reposts:
    print(f"Reposted from @{repost['original_author']}")
    print(f"Time: {repost['reposted_at']}")
```

## 📊 Logging

The bot generates a log file `bot.log` recording all operations:

```
2025-11-24 10:30:00 - __main__ - INFO - Starting repost cycle...
2025-11-24 10:30:05 - repost - INFO - Searching for: #AI
2025-11-24 10:30:10 - repost - INFO - Found post to repost from @user: This is...
2025-11-24 10:30:15 - repost - INFO - Reposted: at://...
2025-11-24 10:30:20 - reply - INFO - Checking for new replies...
```

## ⚠️ Important Notes

1. **Account Security**
   - Do NOT commit `.env` file to Git
   - Use strong passwords
   - Change passwords regularly

2. **Usage Limitations**
   - Follow Bluesky's terms of service
   - Avoid excessive frequency
   - Recommended minimum interval: 5 minutes

3. **Content Moderation**
   - Regularly review reposted content
   - Ensure keyword filtering is accurate
   - Avoid reposting inappropriate content

4. **Resource Usage**
   - Long-running operations consume system resources
   - Database will grow over time
   - Periodically clean up old data

## 🛠️ Troubleshooting

### Login Failed

```
Error: Failed to login
```

**Solutions**:
- Check credentials in `.env` file
- Verify Bluesky account status
- Check network connection

### No Search Results

```
Found 0 posts to repost
```

**Solutions**:
- Check tags and keywords in `config.json`
- Try more general search terms
- Verify relevant posts exist on Bluesky

### Database Error

```
Error: database is locked
```

**Solutions**:
- Ensure no multiple bot instances running simultaneously
- Restart the bot
- If necessary, delete `posts.db` and reinitialize

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

---

**Disclaimer**: This project is for educational and research purposes only. When using this bot, please comply with Bluesky's terms of service and community guidelines. The author is not responsible for any consequences of using this software.
