# Bluesky 转发机器人 🤖

[English](README.md) | 简体中文

一个功能强大的 Bluesky 自动化机器人，可以搜索、转发包含特定标签或关键词的帖子，并自动回复评论。

## ✨ 功能特性

- 🔍 **智能搜索**：根据自定义标签和关键词搜索最新帖子
- 🔄 **自动转发**：将匹配的帖子转发到机器人账户
- 💬 **预设评论**：转发时自动添加自定义评论
- 🤖 **智能回复**：根据关键词自动回复帖子下的评论
- 📊 **数据跟踪**：SQLite 数据库记录所有操作，避免重复
- ⏰ **定时运行**：可配置的定时任务，自动化执行
- 📝 **日志记录**：完整的操作日志，便于调试和监控

## 📁 项目结构

```
Re-Post_Bot/
├── .env                # 账号凭证配置（不要上传到 Git）
├── .gitignore          # Git 忽略文件
├── config.json         # 机器人配置文件
├── requirements.txt    # Python 依赖列表
├── bot.py              # 命令行版本主程序
├── bot.ipynb           # Jupyter Notebook 交互式版本
├── auth.py             # Bluesky 认证模块
├── database.py         # SQLite 数据库管理
├── repost.py           # 转发功能模块
├── reply.py            # 自动回复模块
├── README.md           # 英文文档
└── README_CN.md        # 中文文档（本文件）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

编辑 `.env` 文件，填入你的 Bluesky 账号信息：

```env
BLUESKY_HANDLE=your_handle.bsky.social
BLUESKY_PASSWORD=your_password
```

### 3. 配置机器人

编辑 `config.json` 文件，自定义机器人行为：

```json
{
  "search": {
    "tags": ["#AI", "#tech"],           // 要搜索的标签
    "keywords": ["人工智能", "技术"],    // 要搜索的关键词
    "check_interval_minutes": 10        // 检查间隔（分钟）
  },
  "repost": {
    "preset_comment": "分享一个有趣的内容！",  // 转发时的评论
    "max_reposts_per_run": 5                  // 每次最多转发数量
  },
  "auto_reply": {
    "keyword_responses": {              // 关键词 -> 回复映射
      "谢谢": "不客气！",
      "怎么": "如果有问题欢迎询问！",
      "价格": "请查看官网获取价格信息。"
    },
    "default_response": "感谢你的评论！"  // 默认回复
  }
}
```

### 4. 运行机器人

#### 方式一：命令行运行（推荐用于部署）

```bash
python bot.py
```

机器人将：
1. 立即执行一次搜索和转发
2. 处理评论和回复
3. 按配置的时间间隔自动重复执行

按 `Ctrl+C` 停止运行。

#### 方式二：Jupyter Notebook 运行（推荐用于测试）

```bash
jupyter notebook bot.ipynb
```

Notebook 版本提供：
- 📊 交互式界面
- 🧪 单步测试功能
- 📈 实时查看统计
- 🎛️ 动态配置修改

## 📖 详细说明

### 工作流程

1. **搜索阶段**
   - 根据配置的标签和关键词搜索 Bluesky 帖子
   - **搜索逻辑**：匹配**任一**标签或**任一**关键词的帖子都会被选中（OR 关系，非 AND）
   - 检查是否已转发过（去重）
   - 筛选符合条件的帖子

2. **转发阶段**
   - 转发（repost）符合条件的帖子
   - 添加预设评论到原帖
   - 记录到数据库

3. **回复阶段**
   - 监控机器人转发的帖子下的评论
   - 检测评论中的关键词
   - **回复逻辑**：若评论包含**任一**配置的关键词，则发送对应回复；否则使用默认回复
   - 自动发送对应的回复
   - 记录已处理的评论

### 配置说明

#### 搜索配置 (`search`)

| 参数 | 类型 | 说明 |
|------|------|------|
| `tags` | 数组 | 要搜索的标签列表，如 `["#AI", "#tech"]`。包含任一标签的帖子都会被选中。 |
| `keywords` | 数组 | 要搜索的关键词列表。包含任一关键词的帖子都会被选中。 |
| `check_interval_minutes` | 数字 | 定时任务间隔（分钟） |

**注意**：帖子只需满足**任一标签或任一关键词**即会被转发（非同时满足）。

#### 转发配置 (`repost`)

| 参数 | 类型 | 说明 |
|------|------|------|
| `preset_comment` | 字符串 | 转发时自动添加的评论 |
| `max_reposts_per_run` | 数字 | 每次运行最多转发的帖子数量 |

#### 自动回复配置 (`auto_reply`)

| 参数 | 类型 | 说明 |
|------|------|------|
| `keyword_responses` | 对象 | 关键词到回复的映射。若评论包含任一关键词，则发送对应回复。 |
| `default_response` | 字符串 | 未匹配到关键词时的默认回复 |

**注意**：关键词匹配不区分大小写。优先使用第一个匹配到的关键词对应的回复。

### 数据库结构

机器人使用 SQLite 数据库 (`posts.db`) 存储数据：

#### `reposted_posts` 表
- `id`: 主键
- `original_uri`: 原帖 URI
- `original_author`: 原作者
- `repost_uri`: 转发后的 URI
- `reposted_at`: 转发时间

#### `processed_replies` 表
- `id`: 主键
- `reply_uri`: 回复 URI
- `parent_post_uri`: 父帖子 URI
- `author`: 回复作者
- `content`: 回复内容
- `replied_at`: 回复时间

## 🔧 高级用法

### 自定义关键词响应

在 `config.json` 中添加更多关键词映射：

```json
"keyword_responses": {
  "谢谢": "不客气，很高兴能帮到你！",
  "怎么用": "请查看我们的使用指南...",
  "价格": "价格信息请访问官网...",
  "帮助": "我们随时为你提供帮助！"
}
```

### 修改搜索范围

调整搜索的标签和关键词：

```json
"search": {
  "tags": ["#Python", "#AI", "#MachineLearning"],
  "keywords": ["人工智能", "深度学习", "神经网络"]
}
```

### 调整运行频率

修改检查间隔（单位：分钟）：

```json
"search": {
  "check_interval_minutes": 15  // 每 15 分钟运行一次
}
```

### 查看历史记录

使用 Python 或 Jupyter Notebook 查询数据库：

```python
from database import Database

db = Database()

# 获取最近 10 条转发记录
recent_reposts = db.get_recent_reposts(limit=10)

for repost in recent_reposts:
    print(f"转发自 @{repost['original_author']}")
    print(f"时间: {repost['reposted_at']}")
```

## 📊 日志

机器人会生成日志文件 `bot.log`，记录所有操作：

```
2025-11-24 10:30:00 - __main__ - INFO - Starting repost cycle...
2025-11-24 10:30:05 - repost - INFO - Searching for: #AI
2025-11-24 10:30:10 - repost - INFO - Found post to repost from @user: This is...
2025-11-24 10:30:15 - repost - INFO - Reposted: at://...
2025-11-24 10:30:20 - reply - INFO - Checking for new replies...
```

## ⚠️ 注意事项

1. **账号安全**
   - 不要将 `.env` 文件上传到 Git
   - 使用强密码
   - 定期更换密码

2. **使用限制**
   - 遵守 Bluesky 的使用条款
   - 避免过度频繁的操作
   - 建议间隔时间不少于 5 分钟

3. **内容审核**
   - 定期检查机器人转发的内容
   - 确保关键词过滤准确
   - 避免转发不当内容

4. **资源消耗**
   - 长时间运行会占用系统资源
   - 数据库会逐渐增大
   - 建议定期清理旧数据

## 🛠️ 故障排除

### 登录失败

```
Error: Failed to login
```

**解决方法**：
- 检查 `.env` 文件中的账号密码是否正确
- 确认 Bluesky 账号状态正常
- 检查网络连接

### 搜索无结果

```
Found 0 posts to repost
```

**解决方法**：
- 检查 `config.json` 中的标签和关键词
- 尝试更通用的搜索词
- 确认 Bluesky 上确实有相关帖子

### 数据库错误

```
Error: database is locked
```

**解决方法**：
- 确保没有多个机器人实例同时运行
- 重启机器人
- 必要时删除 `posts.db` 重新初始化

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

---

**免责声明**: 本项目仅供学习和研究使用。使用本机器人时，请遵守 Bluesky 的使用条款和社区准则。作者不对使用本软件造成的任何后果负责。
