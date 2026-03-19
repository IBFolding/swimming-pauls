"""
Social Media System for Paul's World
Pauls can create accounts, post, interact, and build influence on social platforms.

Part of Paul's World - Extended Digital Life

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import sqlite3
from pathlib import Path


class Platform(Enum):
    """Social media platforms available in Paul's World."""
    TWITTER = "twitter"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    REDDIT = "reddit"
    GITHUB = "github"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class PostType(Enum):
    """Types of social media posts."""
    TEXT = "text"
    PREDICTION = "prediction"
    ANALYSIS = "analysis"
    MEME = "meme"
    REPLY = "reply"
    SHARE = "share"


@dataclass
class SocialPost:
    """A post on social media."""
    id: str
    author: str  # Paul name
    platform: Platform
    content: str
    post_type: PostType
    timestamp: datetime
    
    # Engagement metrics
    likes: int = 0
    replies: int = 0
    shares: int = 0
    views: int = 0
    
    # Context
    topic: Optional[str] = None
    sentiment: float = 0.0  # -1 to 1
    is_viral: bool = False
    
    # Reply threading
    parent_id: Optional[str] = None
    reply_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'author': self.author,
            'platform': self.platform.value,
            'content': self.content[:200],  # Truncate for storage
            'post_type': self.post_type.value,
            'timestamp': self.timestamp.isoformat(),
            'likes': self.likes,
            'replies': self.replies,
            'shares': self.shares,
            'views': self.views,
            'topic': self.topic,
            'sentiment': self.sentiment,
            'is_viral': self.is_viral,
            'parent_id': self.parent_id,
        }


@dataclass
class SocialAccount:
    """A Paul's social media account."""
    paul_name: str
    platform: Platform
    handle: str
    
    # Account stats
    followers: int = 0
    following: int = 0
    posts_count: int = 0
    reputation: float = 0.5  # Platform-specific reputation
    
    # Activity
    last_post: Optional[datetime] = None
    joined_at: datetime = field(default_factory=datetime.now)
    
    # Preferences
    post_frequency: float = 0.3  # 0-1, how often they post
    engagement_style: str = "balanced"  # aggressive, balanced, passive
    
    def to_dict(self) -> dict:
        return {
            'paul_name': self.paul_name,
            'platform': self.platform.value,
            'handle': self.handle,
            'followers': self.followers,
            'following': self.following,
            'posts_count': self.posts_count,
            'reputation': self.reputation,
            'last_post': self.last_post.isoformat() if self.last_post else None,
            'joined_at': self.joined_at.isoformat(),
            'post_frequency': self.post_frequency,
            'engagement_style': self.engagement_style,
        }


class SocialMediaManager:
    """
    Manages all social media activity in Paul's World.
    
    Features:
    - Pauls create accounts on platforms
    - Post predictions, analysis, memes
    - Like, reply, share posts
    - Build followers and reputation
    - Viral content detection
    - Cross-platform influence
    """
    
    def __init__(self, db_path: str = "data/social_media.db"):
        self.db_path = Path(db_path)
        self.posts: Dict[str, SocialPost] = {}
        self.accounts: Dict[tuple, SocialAccount] = {}  # (paul_name, platform)
        self.platform_feeds: Dict[Platform, List[str]] = {p: [] for p in Platform}
        self.trending_topics: Dict[str, int] = {}
        
        self._init_db()
        self._load_data()
    
    def _init_db(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_accounts (
                paul_name TEXT,
                platform TEXT,
                handle TEXT,
                followers INTEGER DEFAULT 0,
                following INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0,
                reputation REAL DEFAULT 0.5,
                last_post TEXT,
                joined_at TEXT,
                post_frequency REAL DEFAULT 0.3,
                engagement_style TEXT DEFAULT 'balanced',
                PRIMARY KEY (paul_name, platform)
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_posts (
                id TEXT PRIMARY KEY,
                author TEXT,
                platform TEXT,
                content TEXT,
                post_type TEXT,
                timestamp TEXT,
                likes INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                topic TEXT,
                sentiment REAL DEFAULT 0,
                is_viral INTEGER DEFAULT 0,
                parent_id TEXT
            )
        ''')
        
        # Interactions table (likes, follows)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT,
                target TEXT,
                action TEXT,  -- like, follow, share
                platform TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_data(self):
        """Load existing data from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load accounts
        cursor.execute('SELECT * FROM social_accounts')
        for row in cursor.fetchall():
            account = SocialAccount(
                paul_name=row[0],
                platform=Platform(row[1]),
                handle=row[2],
                followers=row[3],
                following=row[4],
                posts_count=row[5],
                reputation=row[6],
                last_post=datetime.fromisoformat(row[7]) if row[7] else None,
                joined_at=datetime.fromisoformat(row[8]),
                post_frequency=row[9],
                engagement_style=row[10],
            )
            self.accounts[(row[0], Platform(row[1]))] = account
        
        # Load posts
        cursor.execute('SELECT * FROM social_posts ORDER BY timestamp DESC LIMIT 1000')
        for row in cursor.fetchall():
            post = SocialPost(
                id=row[0],
                author=row[1],
                platform=Platform(row[2]),
                content=row[3],
                post_type=PostType(row[4]),
                timestamp=datetime.fromisoformat(row[5]),
                likes=row[6],
                replies=row[7],
                shares=row[8],
                views=row[9],
                topic=row[10],
                sentiment=row[11],
                is_viral=bool(row[12]),
                parent_id=row[13],
            )
            self.posts[post.id] = post
            self.platform_feeds[post.platform].append(post.id)
        
        conn.close()
    
    def create_account(self, paul_name: str, platform: Platform, 
                       handle: Optional[str] = None) -> SocialAccount:
        """Create a social media account for a Paul."""
        if handle is None:
            handle = f"@{paul_name.replace(' ', '').lower()}"
        
        account = SocialAccount(
            paul_name=paul_name,
            platform=platform,
            handle=handle,
        )
        
        self.accounts[(paul_name, platform)] = account
        self._save_account(account)
        
        return account
    
    def _save_account(self, account: SocialAccount):
        """Save account to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO social_accounts 
            (paul_name, platform, handle, followers, following, posts_count, reputation,
             last_post, joined_at, post_frequency, engagement_style)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            account.paul_name,
            account.platform.value,
            account.handle,
            account.followers,
            account.following,
            account.posts_count,
            account.reputation,
            account.last_post.isoformat() if account.last_post else None,
            account.joined_at.isoformat(),
            account.post_frequency,
            account.engagement_style,
        ))
        
        conn.commit()
        conn.close()
    
    def create_post(self, paul_name: str, platform: Platform, 
                    content: str, post_type: PostType = PostType.TEXT,
                    topic: Optional[str] = None, parent_id: Optional[str] = None) -> SocialPost:
        """Create a post on social media."""
        # Ensure account exists
        if (paul_name, platform) not in self.accounts:
            self.create_account(paul_name, platform)
        
        post_id = f"{platform.value}_{paul_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        post = SocialPost(
            id=post_id,
            author=paul_name,
            platform=platform,
            content=content,
            post_type=post_type,
            timestamp=datetime.now(),
            topic=topic,
            parent_id=parent_id,
        )
        
        # Calculate sentiment (simple heuristic)
        positive_words = ['bullish', 'up', 'gain', 'moon', 'rocket', 'win', 'good', 'great']
        negative_words = ['bearish', 'down', 'loss', 'dump', 'crash', 'bad', 'terrible']
        
        content_lower = content.lower()
        pos_count = sum(1 for w in positive_words if w in content_lower)
        neg_count = sum(1 for w in negative_words if w in content_lower)
        
        if pos_count + neg_count > 0:
            post.sentiment = (pos_count - neg_count) / (pos_count + neg_count)
        
        self.posts[post_id] = post
        self.platform_feeds[platform].insert(0, post_id)
        
        # Update account
        account = self.accounts[(paul_name, platform)]
        account.posts_count += 1
        account.last_post = datetime.now()
        self._save_account(account)
        
        # Save post
        self._save_post(post)
        
        # Update trending topics
        if topic:
            self.trending_topics[topic] = self.trending_topics.get(topic, 0) + 1
        
        return post
    
    def _save_post(self, post: SocialPost):
        """Save post to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO social_posts
            (id, author, platform, content, post_type, timestamp, likes, replies, shares,
             views, topic, sentiment, is_viral, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.id,
            post.author,
            post.platform.value,
            post.content,
            post.post_type.value,
            post.timestamp.isoformat(),
            post.likes,
            post.replies,
            post.shares,
            post.views,
            post.topic,
            post.sentiment,
            int(post.is_viral),
            post.parent_id,
        ))
        
        conn.commit()
        conn.close()
    
    def like_post(self, paul_name: str, post_id: str):
        """Like a post."""
        if post_id not in self.posts:
            return
        
        post = self.posts[post_id]
        post.likes += 1
        
        # Check for viral
        if post.likes > 100 and not post.is_viral:
            post.is_viral = True
            # Boost author reputation
            if (post.author, post.platform) in self.accounts:
                self.accounts[(post.author, post.platform)].reputation = min(1.0, 
                    self.accounts[(post.author, post.platform)].reputation + 0.1)
        
        self._save_post(post)
        self._record_interaction(paul_name, post.author, 'like', post.platform)
    
    def reply_to_post(self, paul_name: str, post_id: str, content: str) -> SocialPost:
        """Reply to a post."""
        if post_id not in self.posts:
            return None
        
        parent = self.posts[post_id]
        
        reply = self.create_post(
            paul_name=paul_name,
            platform=parent.platform,
            content=content,
            post_type=PostType.REPLY,
            topic=parent.topic,
            parent_id=post_id
        )
        
        parent.replies += 1
        parent.reply_ids.append(reply.id)
        self._save_post(parent)
        
        return reply
    
    def share_post(self, paul_name: str, post_id: str):
        """Share/retweet a post."""
        if post_id not in self.posts:
            return
        
        post = self.posts[post_id]
        post.shares += 1
        self._save_post(post)
        
        # Create share post
        self.create_post(
            paul_name=paul_name,
            platform=post.platform,
            content=f"RT {post.author}: {post.content[:50]}...",
            post_type=PostType.SHARE,
            topic=post.topic
        )
        
        self._record_interaction(paul_name, post.author, 'share', post.platform)
    
    def follow_account(self, follower: str, target: str, platform: Platform):
        """Follow an account."""
        if (target, platform) in self.accounts:
            self.accounts[(target, platform)].followers += 1
            self._save_account(self.accounts[(target, platform)])
        
        if (follower, platform) in self.accounts:
            self.accounts[(follower, platform)].following += 1
            self._save_account(self.accounts[(follower, platform)])
        
        self._record_interaction(follower, target, 'follow', platform)
    
    def _record_interaction(self, actor: str, target: str, action: str, platform: Platform):
        """Record an interaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO social_interactions (actor, target, action, platform, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (actor, target, action, platform.value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_feed(self, platform: Platform, limit: int = 20) -> List[SocialPost]:
        """Get feed for a platform."""
        post_ids = self.platform_feeds[platform][:limit]
        return [self.posts[pid] for pid in post_ids if pid in self.posts]
    
    def get_paul_posts(self, paul_name: str, limit: int = 20) -> List[SocialPost]:
        """Get all posts by a Paul across platforms."""
        posts = [p for p in self.posts.values() if p.author == paul_name]
        posts.sort(key=lambda p: p.timestamp, reverse=True)
        return posts[:limit]
    
    def get_trending(self, limit: int = 10) -> List[tuple]:
        """Get trending topics."""
        sorted_topics = sorted(self.trending_topics.items(), 
                              key=lambda x: x[1], reverse=True)
        return sorted_topics[:limit]
    
    def get_paul_social_stats(self, paul_name: str) -> dict:
        """Get comprehensive social stats for a Paul."""
        total_followers = 0
        total_posts = 0
        reputation = 0
        platform_count = 0
        
        for platform in Platform:
            if (paul_name, platform) in self.accounts:
                account = self.accounts[(paul_name, platform)]
                total_followers += account.followers
                total_posts += account.posts_count
                reputation += account.reputation
                platform_count += 1
        
        viral_posts = len([p for p in self.posts.values() 
                          if p.author == paul_name and p.is_viral])
        
        return {
            'total_followers': total_followers,
            'total_posts': total_posts,
            'avg_reputation': reputation / platform_count if platform_count > 0 else 0,
            'platforms': platform_count,
            'viral_posts': viral_posts,
        }


# Integration with Paul's World
class SocialMediaIntegration:
    """Integrates social media with Paul's World simulation."""
    
    def __init__(self, paul_world, social_manager: SocialMediaManager):
        self.world = paul_world
        self.social = social_manager
    
    def auto_create_accounts(self):
        """Auto-create social accounts for all Pauls."""
        for paul_name in self.world.pauls.keys():
            # Each Paul joins 2-4 random platforms
            platforms = random.sample(list(Platform), random.randint(2, 4))
            for platform in platforms:
                handle = f"@{paul_name.replace(' ', '').lower()}"
                self.social.create_account(paul_name, platform, handle)
    
    def generate_prediction_post(self, paul_name: str, prediction: dict):
        """Generate a social post from a prediction."""
        consensus = prediction.get('consensus', {})
        direction = consensus.get('direction', 'NEUTRAL')
        confidence = consensus.get('confidence', 0.5)
        
        # Pick platform based on Paul's specialty
        paul = self.world.pauls.get(paul_name)
        if not paul:
            return
        
        platform_weights = {
            Platform.TWITTER: 0.4,
            Platform.DISCORD: 0.2,
            Platform.TELEGRAM: 0.2,
            Platform.REDDIT: 0.1,
            Platform.LINKEDIN: 0.1,
        }
        
        if 'Trader' in paul_name or 'Degen' in paul_name:
            platform_weights[Platform.TWITTER] = 0.6
        elif 'Professor' in paul_name:
            platform_weights[Platform.LINKEDIN] = 0.4
        
        platform = random.choices(
            list(platform_weights.keys()),
            weights=list(platform_weights.values())
        )[0]
        
        # Generate content based on sentiment
        templates = {
            'BULLISH': [
                "🚀 I'm bullish! {confidence}% confidence. Let the Pauls cook!",
                "Green candles incoming 📈 {confidence}% sure about this.",
                "My gut says UP and my models agree. {confidence}% confidence.",
            ],
            'BEARISH': [
                "🔻 Expecting a dip. {confidence}% confidence.",
                "Red flags everywhere 📉 {confidence}% sure we're heading down.",
                "Taking profits here. {confidence}% confidence bearish.",
            ],
            'NEUTRAL': [
                "🤔 Sideways action. {confidence}% confidence on neutral.",
                "Waiting for clearer signals. {confidence}% confidence.",
                "Rangebound for now. {confidence}% confidence.",
            ]
        }
        
        content = random.choice(templates.get(direction, templates['NEUTRAL']))
        content = content.format(confidence=int(confidence * 100))
        
        post = self.social.create_post(
            paul_name=paul_name,
            platform=platform,
            content=content,
            post_type=PostType.PREDICTION,
            topic=prediction.get('question', 'general')[:30]
        )
        
        return post
    
    def simulate_engagement(self, post: SocialPost):
        """Simulate likes/replies from other Pauls."""
        # Other Pauls see the post
        viewers = random.sample(
            list(self.world.pauls.keys()),
            min(20, len(self.world.pauls))
        )
        
        for viewer_name in viewers:
            if viewer_name == post.author:
                continue
            
            viewer = self.world.pauls.get(viewer_name)
            if not viewer:
                continue
            
            # Like probability based on agreement
            like_prob = 0.3
            if viewer.mood > 0.2 and post.sentiment > 0:
                like_prob = 0.6
            elif viewer.mood < -0.2 and post.sentiment < 0:
                like_prob = 0.6
            
            if random.random() < like_prob:
                self.social.like_post(viewer_name, post.id)
            
            # Reply probability
            if random.random() < 0.1:
                replies = [
                    "Agreed!",
                    "Interesting take.",
                    "Not sure about that...",
                    "My models show different 👀",
                    "Following your lead on this one!",
                ]
                self.social.reply_to_post(viewer_name, post.id, random.choice(replies))


# CLI Interface
def social_cli():
    """Command-line interface for social media."""
    import sys
    
    social = SocialMediaManager()
    
    if len(sys.argv) < 2:
        print("Social Media CLI")
        print("Commands:")
        print("  feed <platform>              - Show platform feed")
        print("  paul <name>                  - Show Paul's social stats")
        print("  trending                     - Show trending topics")
        print("  post <paul> <platform> <msg> - Create post")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "feed" and len(sys.argv) > 2:
        platform = Platform(sys.argv[2].lower())
        posts = social.get_feed(platform, limit=10)
        print(f"\n📱 {platform.value.upper()} Feed\n")
        for post in posts:
            print(f"@{post.author}: {post.content}")
            print(f"   ❤️ {post.likes}  💬 {post.replies}  🔄 {post.shares}")
            print()
    
    elif command == "paul" and len(sys.argv) > 2:
        paul_name = sys.argv[2]
        stats = social.get_paul_social_stats(paul_name)
        posts = social.get_paul_posts(paul_name, limit=5)
        
        print(f"\n📊 @{paul_name} Social Stats\n")
        print(f"Followers: {stats['total_followers']}")
        print(f"Posts: {stats['total_posts']}")
        print(f"Reputation: {stats['avg_reputation']:.2f}")
        print(f"Viral Posts: {stats['viral_posts']}")
        
        print(f"\nRecent Posts:")
        for post in posts:
            print(f"  [{post.platform.value}] {post.content[:60]}...")
    
    elif command == "trending":
        trends = social.get_trending(10)
        print("\n🔥 Trending Topics\n")
        for topic, count in trends:
            print(f"  #{topic}: {count} posts")
    
    elif command == "post" and len(sys.argv) > 4:
        paul_name = sys.argv[2]
        platform = Platform(sys.argv[3].lower())
        content = " ".join(sys.argv[4:])
        
        post = social.create_post(paul_name, platform, content)
        print(f"✅ Posted: {post.id}")


if __name__ == "__main__":
    social_cli()
