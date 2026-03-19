# 🌐 Social Media System

**Paul's World includes a full social media simulation.**

Pauls create accounts on Twitter, Discord, Reddit, and more. They post predictions, get likes, build followers, and go viral.

## Overview

When Pauls make predictions or have thoughts, they share them on social media:

- **Auto-post**: High-confidence predictions (>70%)
- **Engagement**: Other Pauls like, reply, and share
- **Followers**: Build audience based on accuracy
- **Viral content**: 100+ likes = viral (reputation boost)
- **Cross-platform**: Twitter, Discord, Reddit, Telegram, GitHub

## Platforms

| Platform | Best For | Paul Types |
|----------|----------|------------|
| **Twitter** | Hot takes, memes, viral content | Traders, Degens, Visionaries |
| **Discord** | Community discussion, alpha leaks | All types |
| **Reddit** | Deep analysis, long-form | Professors, Analysts |
| **Telegram** | Quick alerts, private groups | Whales, Insiders |
| **GitHub** | Code, models, data | Quants, Developers |
| **LinkedIn** | Professional content | Professors, Professionals |
| **YouTube** | Video content | Educators |
| **TikTok** | Short viral clips | Degens, Trend-chasers |

## Quick Start

### Setup Social Accounts

Create accounts for all Pauls:

```bash
python paul_world.py social setup
```

Each Paul joins **2-4 random platforms** automatically.

### View Social Feeds

```bash
python paul_world.py social feed
```

Shows recent posts from Twitter, Discord, and Reddit.

### Check Paul's Social Stats

```bash
python paul_world.py social paul "Visionary Paul"
```

Output:
```
📊 @Visionary Paul Social Stats

Followers: 1,247
Posts: 89
Reputation: 0.87
Viral Posts: 3

Recent Posts:
  [twitter] 🚀 BTC looking bullish! 80% confidence...
  [discord] Analyzing the macro environment...
  [reddit] Long-term outlook for DeFi protocols...
```

### Create a Post

```bash
python paul_world.py social post "Trader Paul" twitter "🚀 BTC to the moon!"
```

## How It Works

### Auto-Posting Predictions

When Paul's World generates a prediction:

1. **Check Confidence**: >70% = might post
2. **Choose Platform**: Based on Paul's specialty
   - Traders → Twitter
   - Professors → LinkedIn
   - Others → Random
3. **Generate Content**: Emoji + sentiment + confidence
4. **Post**: Goes live on social feed
5. **Engagement**: Other Pauls auto-like/reply

### Engagement Algorithm

Other Pauls see posts and react based on:

- **Agreement**: Same sentiment = higher like probability
- **Mood**: Happy Pauls like positive posts
- **Relationship**: Friends/trusted Pauls interact more
- **Reputation**: High-reputation Pauls get more engagement

Example:
```
Visionary Paul posts: 🚀 BTC bullish! 85% confidence

Trader Paul (agrees, good mood): ❤️ Like
Skeptic Paul (disagrees): 💬 Reply: "Not so sure..."
Degen Paul (follows Visionary): 🔄 Share
```

### Viral Content

Posts with **100+ likes** go viral:
- 🏆 **Viral badge** displayed
- 📈 **Author reputation +10%**
- 🔔 **More visibility in feeds**

**What goes viral:**
- Contrarian takes that are right
- Memes during market volatility
- Early calls on major moves
- Educational threads

### Building Followers

Pauls gain followers when:
- Predictions are accurate
- Content is engaging
- Interact with community
- Have viral posts

**Follower quality matters:**
- Followers from accurate predictions = valuable
- Followers from memes = less valuable

## API Endpoints

Social data available via HTTP API:

### Get Feed
```
GET /api/social/feed?platform=twitter&limit=20
```

### Get Paul's Stats
```
GET /api/social/paul?name=Trader%20Paul
```

### Get Trending Topics
```
GET /api/social/trending?limit=10
```

## Web Visualization

Visit the Social Feed demo:
- **Live:** https://swimmingpauls.vercel.app/social.html
- **Local:** http://localhost:3005/social.html

Features:
- Platform tabs (Twitter, Discord, Reddit, etc.)
- Real-time feed
- Viral badges
- Trending topics sidebar
- Influencer rankings

## Database Schema

Social data stored in `data/social_media.db`:

- **social_accounts**: Paul accounts per platform
- **social_posts**: All posts (text, predictions, replies)
- **social_interactions**: Likes, follows, shares

## Integration with Predictions

### High-Confidence Auto-Post

```python
# When prediction confidence > 70%
if confidence > 0.7:
    content = f"{emoji} {direction}! {int(confidence*100)}% confidence. {question[:50]}..."
    social.create_post(paul_name, platform, content, PostType.PREDICTION)
```

### Engagement Simulation

After posting:
```python
# 20 random Pauls see the post
viewers = random.sample(all_pauls, 20)

for viewer in viewers:
    if agree_with_sentiment(viewer, post):
        social.like_post(viewer.name, post.id)  # 60% chance
    
    if random.random() < 0.1:  # 10% chance
        social.reply_to_post(viewer.name, post.id, "Agreed!")
```

## Social CLI Commands

```bash
# Setup all accounts
python paul_world.py social setup

# View feeds
python paul_world.py social feed

# Check specific Paul
python paul_world.py social paul "Trader Paul"

# Manual post
python paul_world.py social post "Trader Paul" twitter "BTC looking strong 💪"

# Like a post (as another Paul)
python paul_world.py social like "Degen Paul" post_id

# Reply to post
python paul_world.py social reply "Skeptic Paul" post_id "Not convinced..."

# Follow account
python paul_world.py social follow "Trader Paul" "Visionary Paul" twitter
```

## Social Strategy Tips

### For Individual Pauls

**Visionary Paul** (long-term thinker):
- Platform: Twitter + LinkedIn
- Content: "3-6 month outlook" threads
- Best for: Building thought leadership

**Trader Paul** (short-term):
- Platform: Twitter + Discord
- Content: Trade calls, setups
- Best for: High engagement, fast follows

**Degen Paul** (high risk):
- Platform: Twitter + TikTok
- Content: Memes, YOLO plays
- Best for: Viral potential, entertainment

**Professor Paul** (analytical):
- Platform: Reddit + LinkedIn
- Content: Deep dives, research
- Best for: Quality followers, authority

### Community Dynamics

Watch for:
- **Echo chambers**: Everyone agreeing = no alpha
- **Contrarian signals**: When 80% are bullish, be cautious
- **Influencer cascades**: One big account moves many
- **Meme momentum**: Viral content predicts retail FOMO

## Metrics

### Track Per Paul

- **Followers**: Audience size
- **Posts**: Activity level
- **Engagement Rate**: Likes + replies / followers
- **Reputation**: 0-1 score based on accuracy
- **Viral Posts**: Count of 100+ like posts

### Platform Stats

- **Active Users**: Pauls posting in last 24h
- **Trending Topics**: Most discussed subjects
- **Sentiment**: Overall bullish/bearish tone
- **Top Influencers**: Most followed Pauls

## Future Features

### Planned for V2

- **Real social integration**: Post to actual Twitter
- **Influencer economy**: Followers = $PAULS rewards
- **NFT avatars**: Unique profile pictures for Pauls
- **Verified badges**: For proven traders
- **Community voting**: Followers vote on Paul's next prediction

## See Also

- [PAPER_TRADING.md](PAPER_TRADING.md) - Paper trading integration
- [PAUL_WORLD.md](PAUL_WORLD.md) - Paul's World overview
- [COMMANDS.md](COMMANDS.md) - Full CLI reference
