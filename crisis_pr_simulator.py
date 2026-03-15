"""
Crisis PR Simulation Module for Swimming Pauls
Simulates social media spread and public reaction to PR events
"""
import random
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    OUTRAGED = "outraged"


@dataclass
class SocialMediaPost:
    """A simulated social media post."""
    platform: str  # Twitter, Reddit, TikTok, etc.
    author_type: str  # Influencer, Journalist, Regular User, Bot
    content: str
    sentiment: Sentiment
    engagement: int  # Likes, shares, comments
    reach: int  # How many people see it
    timestamp: int  # Minutes since crisis started


@dataclass
class NarrativeNode:
    """A narrative that spreads through the network."""
    id: str
    headline: str
    sentiment: Sentiment
    credibility: float  # 0-1
    virality: float  # 0-1, how likely to spread
    parent_id: str = None  # If this is a mutation of another narrative


class CrisisPRSimulator:
    """
    Simulates how a PR crisis spreads through social media
    and how different responses might play out.
    """
    
    def __init__(self):
        self.platforms = ["Twitter/X", "Reddit", "TikTok", "Instagram", "LinkedIn", "YouTube"]
        self.author_types = {
            "Influencer": {"reach_multiplier": 10, "credibility": 0.6, "activity": 0.3},
            "Journalist": {"reach_multiplier": 8, "credibility": 0.7, "activity": 0.4},
            "Regular User": {"reach_multiplier": 1, "credibility": 0.4, "activity": 0.7},
            "Bot": {"reach_multiplier": 0.5, "credibility": 0.1, "activity": 0.9},
            "Brand Account": {"reach_multiplier": 3, "credibility": 0.3, "activity": 0.2},
        }
        self.sentiment_evolution = {
            Sentiment.POSITIVE: [0.1, 0.7, 0.15, 0.05],  # Stays positive or goes neutral
            Sentiment.NEUTRAL: [0.2, 0.5, 0.2, 0.1],
            Sentiment.NEGATIVE: [0.05, 0.15, 0.5, 0.3],  # Tends to get worse
            Sentiment.OUTRAGED: [0.0, 0.05, 0.25, 0.7],  # Stays outraged
        }
    
    def simulate_crisis(
        self,
        crisis_headline: str,
        company_response: str,
        simulation_hours: int = 24,
        initial_reach: int = 100000
    ) -> Dict[str, Any]:
        """
        Simulate a PR crisis spreading over time.
        
        Args:
            crisis_headline: The initial news/event
            company_response: How the company responds
            simulation_hours: How long to simulate
            initial_reach: Initial audience size
            
        Returns:
            Simulation results with timeline, sentiment shifts, and recommendations
        """
        # Initialize the narrative
        root_narrative = NarrativeNode(
            id="narrative_0",
            headline=crisis_headline,
            sentiment=Sentiment.NEGATIVE,
            credibility=0.6,
            virality=0.7
        )
        
        narratives = {root_narrative.id: root_narrative}
        posts = []
        timeline = []
        
        # Simulate hour by hour
        for hour in range(simulation_hours):
            hour_posts = []
            
            # Generate posts for this hour
            num_posts = self._calculate_post_volume(hour, initial_reach)
            
            for _ in range(num_posts):
                post = self._generate_post(hour, narratives, company_response if hour > 2 else None)
                hour_posts.append(post)
                posts.append(post)
            
            # Narrative mutations (new angles emerge)
            if hour > 0 and random.random() < 0.3:
                new_narrative = self._mutate_narrative(narratives, hour)
                narratives[new_narrative.id] = new_narrative
            
            # Track sentiment for this hour
            hour_sentiment = self._calculate_hour_sentiment(hour_posts)
            
            timeline.append({
                "hour": hour,
                "posts": len(hour_posts),
                "sentiment": hour_sentiment,
                "total_reach": sum(p.reach for p in hour_posts),
                "top_narrative": self._get_dominant_narrative(hour_posts, narratives)
            })
        
        # Generate recommendations based on simulation
        recommendations = self._generate_pr_recommendations(timeline, company_response)
        
        return {
            "crisis_headline": crisis_headline,
            "company_response": company_response,
            "simulation_hours": simulation_hours,
            "total_posts": len(posts),
            "timeline": timeline,
            "final_sentiment": timeline[-1]["sentiment"],
            "narratives": list(narratives.values()),
            "recommendations": recommendations,
            "key_insights": self._extract_insights(posts, timeline)
        }
    
    def _calculate_post_volume(self, hour: int, initial_reach: int) -> int:
        """Calculate how many posts in this hour."""
        # Viral curve: starts small, peaks at 6-12 hours, then declines
        if hour < 2:
            base = 50
        elif hour < 6:
            base = 200 + (hour * 100)
        elif hour < 12:
            base = 800
        elif hour < 24:
            base = 800 - ((hour - 12) * 50)
        else:
            base = 100
        
        scale = initial_reach / 100000
        return int(base * scale * random.uniform(0.8, 1.2))
    
    def _generate_post(self, hour: int, narratives: Dict, company_response: str = None) -> SocialMediaPost:
        """Generate a single social media post."""
        # Select author type
        author_type = random.choices(
            list(self.author_types.keys()),
            weights=[v["activity"] for v in self.author_types.values()]
        )[0]
        
        author_props = self.author_types[author_type]
        
        # Select platform
        platform = random.choice(self.platforms)
        
        # Select or create sentiment
        if hour < 2:
            # Early: mostly negative
            sentiment = random.choices(
                list(Sentiment),
                weights=[0.05, 0.15, 0.5, 0.3]
            )[0]
        elif company_response and hour > 4:
            # After company response: slight shift based on response quality
            sentiment = random.choices(
                list(Sentiment),
                weights=[0.2, 0.3, 0.35, 0.15]
            )[0]
        else:
            # Mid-crisis: evolving
            sentiment = random.choices(
                list(Sentiment),
                weights=[0.1, 0.25, 0.4, 0.25]
            )[0]
        
        # Generate content based on sentiment
        content = self._generate_post_content(sentiment, author_type, platform, company_response)
        
        # Calculate engagement
        base_engagement = {
            "Influencer": random.randint(1000, 50000),
            "Journalist": random.randint(500, 10000),
            "Regular User": random.randint(1, 100),
            "Bot": random.randint(10, 500),
            "Brand Account": random.randint(50, 2000)
        }[author_type]
        
        # Sentiment affects engagement (outrage gets more engagement)
        engagement_multipliers = {
            Sentiment.POSITIVE: 0.7,
            Sentiment.NEUTRAL: 0.5,
            Sentiment.NEGATIVE: 1.2,
            Sentiment.OUTRAGED: 1.8
        }
        
        engagement = int(base_engagement * engagement_multipliers[sentiment])
        
        # Calculate reach
        reach = int(engagement * author_props["reach_multiplier"] * random.uniform(10, 50))
        
        return SocialMediaPost(
            platform=platform,
            author_type=author_type,
            content=content,
            sentiment=sentiment,
            engagement=engagement,
            reach=reach,
            timestamp=hour * 60
        )
    
    def _generate_post_content(self, sentiment: Sentiment, author_type: str, platform: str, company_response: str = None) -> str:
        """Generate realistic post content."""
        templates = {
            Sentiment.POSITIVE: [
                "Glad to see them handling this well 👏",
                "Everyone makes mistakes, it's how you respond that matters",
                "Appreciate the transparency here",
                "This is how you do crisis management",
                "Standing by this brand"
            ],
            Sentiment.NEUTRAL: [
                "Waiting to see how this develops",
                "Interesting situation, watching closely",
                "Need more facts before judging",
                "Both sides have points here",
                "Let's see what happens next"
            ],
            Sentiment.NEGATIVE: [
                "This is really disappointing",
                "They need to do better than this",
                "Lost trust in this brand",
                "Not good enough",
                "Actions speak louder than words"
            ],
            Sentiment.OUTRAGED: [
                "This is UNACCEPTABLE!!!",
                "Boycott this company immediately",
                "How dare they! Fire everyone involved!",
                "Never buying from them again!!!",
                "This is the worst thing I've ever seen!"
            ]
        }
        
        content = random.choice(templates[sentiment])
        
        # Add platform-specific formatting
        if platform == "Twitter/X":
            if random.random() < 0.3:
                content += " #Crisis #PRFail"
        elif platform == "TikTok":
            content = "POV: " + content
        
        return content
    
    def _mutate_narrative(self, narratives: Dict, hour: int) -> NarrativeNode:
        """Create a mutation of an existing narrative."""
        parent = random.choice(list(narratives.values()))
        
        mutations = [
            "But what they didn't tell you...",
            "Meanwhile, sources say...",
            "The real story is...",
            "What if I told you...",
            "Breaking: New details emerge..."
        ]
        
        new_headline = f"{random.choice(mutations)} {parent.headline}"
        
        # Mutated narratives often become more extreme
        sentiment_shift = random.choice([-1, 0, 1])
        sentiments = list(Sentiment)
        parent_idx = sentiments.index(parent.sentiment)
        new_idx = max(0, min(len(sentiments) - 1, parent_idx + sentiment_shift))
        
        return NarrativeNode(
            id=f"narrative_{hour}_{random.randint(0, 1000)}",
            headline=new_headline,
            sentiment=sentiments[new_idx],
            credibility=max(0.1, parent.credibility - 0.1),
            virality=min(1.0, parent.virality + 0.1),
            parent_id=parent.id
        )
    
    def _calculate_hour_sentiment(self, posts: List[SocialMediaPost]) -> Dict[str, float]:
        """Calculate sentiment distribution for an hour."""
        if not posts:
            return {"positive": 0, "neutral": 0, "negative": 0, "outraged": 0}
        
        total_reach = sum(p.reach for p in posts)
        
        sentiment_counts = {s: 0 for s in Sentiment}
        for post in posts:
            sentiment_counts[post.sentiment] += post.reach
        
        return {
            "positive": round(sentiment_counts[Sentiment.POSITIVE] / total_reach * 100, 1),
            "neutral": round(sentiment_counts[Sentiment.NEUTRAL] / total_reach * 100, 1),
            "negative": round(sentiment_counts[Sentiment.NEGATIVE] / total_reach * 100, 1),
            "outraged": round(sentiment_counts[Sentiment.OUTRAGED] / total_reach * 100, 1)
        }
    
    def _get_dominant_narrative(self, posts: List[SocialMediaPost], narratives: Dict) -> str:
        """Get the most common narrative theme."""
        return "Multiple conflicting narratives"
    
    def _generate_pr_recommendations(self, timeline: List[Dict], company_response: str) -> List[str]:
        """Generate PR recommendations based on simulation."""
        recommendations = []
        
        final_sentiment = timeline[-1]["sentiment"]
        
        if final_sentiment["outraged"] > 30:
            recommendations.append("🔥 CRITICAL: Sentiment highly negative. Consider CEO public statement.")
            recommendations.append("📱 Deploy social media listening team 24/7")
            recommendations.append("🤝 Engage directly with top influencers who are neutral/negative")
        elif final_sentiment["negative"] > 40:
            recommendations.append("⚠️  Deploy additional crisis communications resources")
            recommendations.append("📊 Monitor for narrative mutations and address misinformation")
            recommendations.append("💬 Prepare FAQ and talking points for customer service")
        elif final_sentiment["positive"] > 30:
            recommendations.append("✅ Response working well. Amplify positive stories")
            recommendations.append("📈 Consider proactive media outreach")
        else:
            recommendations.append("⏱️  Continue monitoring. Sentiment stabilizing")
        
        # Time-based recommendations
        peak_hour = max(range(len(timeline)), key=lambda i: timeline[i]["posts"])
        recommendations.append(f"📊 Peak discussion at Hour {peak_hour}. Reserve response capacity for this window.")
        
        return recommendations
    
    def _extract_insights(self, posts: List[SocialMediaPost], timeline: List[Dict]) -> List[str]:
        """Extract key insights from the simulation."""
        insights = []
        
        # Platform insights
        platform_reach = {}
        for post in posts:
            platform_reach[post.platform] = platform_reach.get(post.platform, 0) + post.reach
        
        top_platform = max(platform_reach, key=platform_reach.get)
        insights.append(f"🌐 {top_platform} generated highest reach ({platform_reach[top_platform]:,} impressions)")
        
        # Author type insights
        author_impact = {}
        for post in posts:
            author_impact[post.author_type] = author_impact.get(post.author_type, 0) + post.engagement
        
        top_author = max(author_impact, key=author_impact.get)
        insights.append(f"👤 {top_author}s drove most engagement")
        
        # Timeline insights
        total_reach = sum(hour["total_reach"] for hour in timeline)
        insights.append(f"📈 Total estimated reach: {total_reach:,} people")
        
        return insights


# Convenience function
def simulate_crisis_pr(
    crisis_headline: str,
    company_response: str,
    hours: int = 24
) -> Dict[str, Any]:
    """
    Quick function to simulate a PR crisis.
    
    Example:
        result = simulate_crisis_pr(
            "Company data breach exposes 10M user records",
            "We are investigating and will update within 24 hours"
        )
    """
    simulator = CrisisPRSimulator()
    return simulator.simulate_crisis(crisis_headline, company_response, hours)


if __name__ == "__main__":
    # Test the simulator
    result = simulate_crisis_pr(
        "Major retailer faces backlash over working conditions",
        "We take these concerns seriously and are conducting a full review",
        hours=12
    )
    
    print("Crisis PR Simulation Results")
    print("=" * 50)
    print(f"Crisis: {result['crisis_headline']}")
    print(f"Response: {result['company_response']}")
    print(f"Total Posts: {result['total_posts']:,}")
    print(f"Final Sentiment: {result['final_sentiment']}")
    print("\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
