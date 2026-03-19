"""
ReportAgent System for Swimming Pauls
Automated report generation with integrated OpenClaw skill outputs.

This module provides:
- ReportAgent: Compiles prediction findings into formatted reports
- Skill integration: Crypto prices, news, market data, weather, etc.
- Report generation: Markdown and HTML formats
- Unique report IDs with persistence
- API endpoints for serving reports
"""

import os
import json
import uuid
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import Swimming Pauls modules
try:
    from .simulation import SimulationResult, SimulationRound
    from .agent import Agent, AgentPrediction
    from .visualization import ScalesVisualizer, HTMLReportGenerator, HTMLReportConfig
except ImportError:
    # Fallback for direct execution
    from simulation import SimulationResult, SimulationRound
    from agent import Agent, AgentPrediction
    from visualization import ScalesVisualizer, HTMLReportGenerator, HTMLReportConfig


class ReportFormat(Enum):
    """Supported report output formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


@dataclass
class SkillData:
    """Data fetched from OpenClaw skills."""
    skill_name: str
    query: str
    result: Any
    timestamp: float
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "query": self.query,
            "result": self.result if isinstance(self.result, (dict, list, str, int, float, bool)) else str(self.result),
            "timestamp": self.timestamp,
            "success": self.success,
            "error_message": self.error_message,
        }


@dataclass
class AgentReasoning:
    """Individual Paul reasoning extracted from simulation."""
    agent_id: str
    agent_name: str
    persona: str
    direction: str
    confidence: float
    magnitude: float
    reasoning: str
    accuracy_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "persona": self.persona,
            "direction": self.direction,
            "confidence": round(self.confidence, 3),
            "magnitude": round(self.magnitude, 3),
            "reasoning": self.reasoning,
            "accuracy_score": round(self.accuracy_score, 3),
        }


@dataclass
class ConsensusSummary:
    """Consensus summary from simulation."""
    direction: str
    confidence: float
    sentiment: float
    strength: str
    consistency: float
    bullish_rounds: int
    bearish_rounds: int
    neutral_rounds: int
    total_rounds: int
    agreement_ratio: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "direction": self.direction,
            "confidence": round(self.confidence, 3),
            "sentiment": round(self.sentiment, 3),
            "strength": self.strength,
            "consistency": round(self.consistency, 3),
            "bullish_rounds": self.bullish_rounds,
            "bearish_rounds": self.bearish_rounds,
            "neutral_rounds": self.neutral_rounds,
            "total_rounds": self.total_rounds,
            "agreement_ratio": round(self.agreement_ratio, 3),
        }


@dataclass
class ReportMetadata:
    """Metadata for a generated report."""
    report_id: str
    title: str
    created_at: str
    format: str
    simulation_duration: float
    num_agents: int
    num_rounds: int
    topic: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "title": self.title,
            "created_at": self.created_at,
            "format": self.format,
            "simulation_duration": round(self.simulation_duration, 3),
            "num_agents": self.num_agents,
            "num_rounds": self.num_rounds,
            "topic": self.topic,
            "tags": self.tags,
        }


@dataclass
class Report:
    """Complete report with all components."""
    metadata: ReportMetadata
    consensus: ConsensusSummary
    agent_reasonings: List[AgentReasoning]
    skill_data: List[SkillData]
    visualizations: Dict[str, str]
    insights: List[str]
    raw_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "consensus": self.consensus.to_dict(),
            "agent_reasonings": [ar.to_dict() for ar in self.agent_reasonings],
            "skill_data": [sd.to_dict() for sd in self.skill_data],
            "visualizations": self.visualizations,
            "insights": self.insights,
            "raw_data": self.raw_data,
        }


class SkillIntegrator:
    """
    Integrates OpenClaw skills to enrich reports with real-time data.
    """
    
    # Available skills and their query patterns
    SKILL_PATTERNS = {
        "crypto-price": {
            "patterns": ["btc", "eth", "sol", "crypto", "bitcoin", "ethereum", "price", "trading"],
            "description": "Cryptocurrency prices and charts",
            "emoji": "💰",
        },
        "yahoo-finance": {
            "patterns": ["stock", "equity", "market", "spy", "qqq", "nasdaq", "nyse"],
            "description": "Stock prices and financial data",
            "emoji": "📈",
        },
        "polymarket": {
            "patterns": ["prediction", "will", "election", "odds", "bet", "market probability"],
            "description": "Prediction market odds",
            "emoji": "🎯",
        },
        "news-summarizer": {
            "patterns": ["news", "headlines", "latest", "update", "what happened"],
            "description": "Latest news with bias detection",
            "emoji": "📰",
        },
        "weather": {
            "patterns": ["weather", "forecast", "rain", "temperature", "sunny"],
            "description": "Weather forecasts",
            "emoji": "🌤️",
        },
        "base": {
            "patterns": ["base", "onchain", "blockchain", "defi", "gas"],
            "description": "Base blockchain data",
            "emoji": "🔷",
        },
        "web_search": {
            "patterns": ["search", "find", "lookup", "research", "info about"],
            "description": "Web search results",
            "emoji": "🔍",
        },
    }
    
    def __init__(self):
        self.skill_cache: Dict[str, SkillData] = {}
        self.call_history: List[SkillData] = []
    
    def detect_relevant_skills(self, topic: str) -> List[str]:
        """Detect which skills are relevant for a given topic."""
        topic_lower = topic.lower()
        relevant = []
        
        for skill_name, config in self.SKILL_PATTERNS.items():
            if any(pattern in topic_lower for pattern in config["patterns"]):
                relevant.append(skill_name)
        
        return relevant
    
    async def call_skill(self, skill_name: str, query: str) -> SkillData:
        """
        Call an OpenClaw skill and return structured data.
        In production, this would use the actual skill bridge.
        """
        cache_key = f"{skill_name}:{query}"
        
        # Check cache (valid for 5 minutes)
        if cache_key in self.skill_cache:
            cached = self.skill_cache[cache_key]
            if time.time() - cached.timestamp < 300:
                return cached
        
        try:
            # Simulate skill call - in production, use actual skill_bridge
            result = await self._mock_skill_call(skill_name, query)
            
            skill_data = SkillData(
                skill_name=skill_name,
                query=query,
                result=result,
                timestamp=time.time(),
                success=True,
            )
        except Exception as e:
            skill_data = SkillData(
                skill_name=skill_name,
                query=query,
                result=None,
                timestamp=time.time(),
                success=False,
                error_message=str(e),
            )
        
        # Cache and record
        self.skill_cache[cache_key] = skill_data
        self.call_history.append(skill_data)
        
        return skill_data
    
    async def _mock_skill_call(self, skill_name: str, query: str) -> Any:
        """Mock skill call for demonstration."""
        await asyncio.sleep(0.01)  # Simulate network delay
        
        if skill_name == "crypto-price":
            return {
                "symbol": query.upper(),
                "price": round(45000 + (hash(query) % 10000), 2),
                "change_24h": round(-5 + (hash(query) % 10), 2),
                "volume_24h": round(1000000000 * (1 + hash(query) % 5), 0),
            }
        elif skill_name == "yahoo-finance":
            return {
                "ticker": query.upper(),
                "price": round(400 + (hash(query) % 100), 2),
                "change": round(-2 + (hash(query) % 4), 2),
                "market_cap": "2.5T",
            }
        elif skill_name == "news-summarizer":
            return {
                "headlines": [
                    f"Latest updates on {query}",
                    f"Market analysis: {query} trends",
                    f"Breaking: {query} developments",
                ],
                "sentiment": "neutral",
                "bias_score": 0.2,
            }
        elif skill_name == "weather":
            return {
                "location": query,
                "temperature": 22,
                "condition": "Partly cloudy",
                "forecast": ["Sunny", "Cloudy", "Rain"],
            }
        elif skill_name == "polymarket":
            return {
                "market": query,
                "yes_odds": 0.65,
                "volume": "$2.5M",
                "resolution_date": "2024-12-31",
            }
        else:
            return {"query": query, "result": f"Mock data for {skill_name}"}
    
    async def enrich_topic(self, topic: str) -> List[SkillData]:
        """Enrich a topic with data from relevant skills."""
        relevant_skills = self.detect_relevant_skills(topic)
        
        tasks = []
        for skill in relevant_skills[:3]:  # Limit to top 3 skills
            tasks.append(self.call_skill(skill, topic))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        skill_data_list = []
        for result in results:
            if isinstance(result, SkillData):
                skill_data_list.append(result)
            elif isinstance(result, Exception):
                skill_data_list.append(SkillData(
                    skill_name="unknown",
                    query=topic,
                    result=None,
                    timestamp=time.time(),
                    success=False,
                    error_message=str(result),
                ))
        
        return skill_data_list


class ReportCompiler:
    """
    Compiles simulation results, agent reasonings, and skill data into reports.
    """
    
    def __init__(self, skill_integrator: Optional[SkillIntegrator] = None):
        self.skill_integrator = skill_integrator or SkillIntegrator()
    
    def extract_consensus(self, result: SimulationResult) -> ConsensusSummary:
        """Extract consensus summary from simulation result."""
        fc = result.final_consensus
        
        # Get the last round's consensus for agreement ratio
        last_round = result.rounds[-1] if result.rounds else None
        agreement_ratio = last_round.consensus.get("agreement_ratio", 0.5) if last_round else 0.5
        
        return ConsensusSummary(
            direction=fc.get("direction", "neutral"),
            confidence=fc.get("consistency", 0.0),  # Use consistency as confidence
            sentiment=fc.get("sentiment", 0.0),
            strength=self._calculate_strength(fc),
            consistency=fc.get("consistency", 0.0),
            bullish_rounds=fc.get("bullish_rounds", 0),
            bearish_rounds=fc.get("bearish_rounds", 0),
            neutral_rounds=fc.get("neutral_rounds", 0),
            total_rounds=len(result.rounds),
            agreement_ratio=agreement_ratio,
        )
    
    def _calculate_strength(self, consensus: Dict[str, Any]) -> str:
        """Calculate consensus strength."""
        consistency = consensus.get("consistency", 0)
        if consistency >= 0.7:
            return "strong"
        elif consistency >= 0.4:
            return "moderate"
        return "weak"
    
    def extract_agent_reasonings(
        self, 
        result: SimulationResult, 
        agents: List[Agent]
    ) -> List[AgentReasoning]:
        """Extract individual agent reasonings from simulation."""
        agent_map = {a.id: a for a in agents}
        reasonings = []
        
        # Get the last round's predictions
        if not result.rounds:
            return reasonings
        
        last_round = result.rounds[-1]
        
        for pred in last_round.predictions:
            agent = agent_map.get(pred.agent_id)
            if agent:
                reasonings.append(AgentReasoning(
                    agent_id=pred.agent_id,
                    agent_name=agent.name,
                    persona=agent.persona.value,
                    direction=pred.direction,
                    confidence=pred.confidence,
                    magnitude=pred.magnitude,
                    reasoning=pred.reasoning,
                    accuracy_score=agent.memory.accuracy_score,
                ))
        
        # Sort by confidence
        reasonings.sort(key=lambda x: x.confidence, reverse=True)
        return reasonings
    
    def generate_insights(
        self, 
        consensus: ConsensusSummary, 
        reasonings: List[AgentReasoning],
        skill_data: List[SkillData]
    ) -> List[str]:
        """Generate strategic insights from all data."""
        insights = []
        
        # Consensus-based insights
        if consensus.direction == "bullish":
            if consensus.strength == "strong":
                insights.append("Strong bullish consensus indicates sustained momentum potential")
            else:
                insights.append("Moderate bullish signals suggest cautious optimism")
        elif consensus.direction == "bearish":
            if consensus.strength == "strong":
                insights.append("Strong bearish consensus warrants defensive positioning")
            else:
                insights.append("Weak bearish signals may indicate temporary pullback")
        else:
            insights.append("Neutral consensus suggests market indecision or consolidation phase")
        
        # Sentiment insights
        if abs(consensus.sentiment) > 0.5:
            insights.append(f"Extreme sentiment reading ({consensus.sentiment:+.2f}) suggests potential reversal zone")
        elif abs(consensus.sentiment) < 0.2:
            insights.append("Low sentiment dispersion indicates balanced market conditions")
        
        # Agent performance insights
        if reasonings:
            best_agent = reasonings[0]
            insights.append(f"{best_agent.agent_name} ({best_agent.persona}) shows highest confidence — consider weighting their signals")
            
            # Check for disagreement
            directions = set(r.direction for r in reasonings)
            if len(directions) > 1:
                insights.append(f"Agent disagreement detected ({len(directions)} directions) — warrants deeper analysis")
        
        # Skill-based insights
        for skill in skill_data:
            if skill.success and skill.skill_name == "crypto-price":
                result = skill.result
                if isinstance(result, dict) and "change_24h" in result:
                    change = result["change_24h"]
                    if change > 5:
                        insights.append(f"Strong 24h price momentum (+{change}%) supports bullish case")
                    elif change < -5:
                        insights.append(f"Negative 24h price action ({change}%) aligns with bearish sentiment")
            
            elif skill.success and skill.skill_name == "news-summarizer":
                result = skill.result
                if isinstance(result, dict) and "sentiment" in result:
                    news_sentiment = result["sentiment"]
                    insights.append(f"News sentiment: {news_sentiment}")
        
        return insights
    
    async def compile_report(
        self,
        result: SimulationResult,
        agents: List[Agent],
        topic: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Report:
        """Compile a complete report from simulation results."""
        # Generate report ID
        report_id = str(uuid.uuid4())[:12]
        
        # Extract components
        consensus = self.extract_consensus(result)
        reasonings = self.extract_agent_reasonings(result, agents)
        
        # Fetch skill data
        skill_data = []
        if topic:
            skill_data = await self.skill_integrator.enrich_topic(topic)
        
        # Generate insights
        insights = self.generate_insights(consensus, reasonings, skill_data)
        
        # Create visualizations placeholder
        visualizations = {
            "sentiment_chart": f"viz_{report_id}_sentiment.png",
            "confidence_chart": f"viz_{report_id}_confidence.png",
            "agent_chart": f"viz_{report_id}_agents.png",
        }
        
        # Metadata
        metadata = ReportMetadata(
            report_id=report_id,
            title=title or f"Swimming Pauls Report - {consensus.direction.upper()}",
            created_at=datetime.utcnow().isoformat(),
            format="report",
            simulation_duration=result.end_time - result.start_time,
            num_agents=len(agents),
            num_rounds=len(result.rounds),
            topic=topic,
            tags=[consensus.direction, consensus.strength] + [s.skill_name for s in skill_data],
        )
        
        # Raw data for export
        raw_data = {
            "rounds": [
                {
                    "round_number": r.round_number,
                    "consensus": r.consensus,
                    "predictions": [
                        {
                            "agent_id": p.agent_id,
                            "direction": p.direction,
                            "confidence": p.confidence,
                            "magnitude": p.magnitude,
                        }
                        for p in r.predictions
                    ],
                }
                for r in result.rounds
            ],
            "final_consensus": result.final_consensus,
            "agent_performances": result.agent_performances,
        }
        
        return Report(
            metadata=metadata,
            consensus=consensus,
            agent_reasonings=reasonings,
            skill_data=skill_data,
            visualizations=visualizations,
            insights=insights,
            raw_data=raw_data,
        )


class ReportFormatter:
    """
    Formats reports into various output formats (Markdown, HTML, JSON).
    """
    
    @staticmethod
    def to_markdown(report: Report) -> str:
        """Convert report to Markdown format."""
        lines = []
        
        # Header
        lines.append(f"# {report.metadata.title}")
        lines.append("")
        lines.append(f"**Report ID:** `{report.metadata.report_id}`")
        lines.append(f"**Generated:** {report.metadata.created_at}")
        lines.append(f"**Topic:** {report.metadata.topic or 'General'}")
        lines.append("")
        
        # Consensus Summary
        lines.append("## 📊 Consensus Summary")
        lines.append("")
        
        direction_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}.get(
            report.consensus.direction, "⚪"
        )
        strength_emoji = {"strong": "💪", "moderate": "👍", "weak": "👎"}.get(
            report.consensus.strength, "😐"
        )
        
        lines.append(f"{direction_emoji} **Direction:** {report.consensus.direction.upper()}")
        lines.append(f"{strength_emoji} **Strength:** {report.consensus.strength.title()}")
        lines.append(f"📈 **Confidence:** {report.consensus.confidence:.1%}")
        lines.append(f"💭 **Sentiment:** {report.consensus.sentiment:+.3f}")
        lines.append(f"✅ **Consistency:** {report.consensus.consistency:.1%}")
        lines.append("")
        
        # Round breakdown
        lines.append("### Round Breakdown")
        lines.append(f"- Bullish rounds: {report.consensus.bullish_rounds}")
        lines.append(f"- Bearish rounds: {report.consensus.bearish_rounds}")
        lines.append(f"- Neutral rounds: {report.consensus.neutral_rounds}")
        lines.append(f"- **Total rounds:** {report.consensus.total_rounds}")
        lines.append("")
        
        # Agent Reasonings
        lines.append("## 🎭 Individual Paul Reasoning")
        lines.append("")
        
        for i, ar in enumerate(report.agent_reasonings[:10], 1):  # Top 10
            persona_emoji = {
                "analyst": "📊",
                "trader": "⚡",
                "hedgie": "🛡️",
                "visionary": "🔮",
                "skeptic": "🤔",
            }.get(ar.persona, "👤")
            
            dir_emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(ar.direction, "❓")
            
            lines.append(f"### {i}. {persona_emoji} {ar.agent_name} ({ar.persona})")
            lines.append(f"- **Direction:** {dir_emoji} {ar.direction.upper()}")
            lines.append(f"- **Confidence:** {ar.confidence:.1%}")
            lines.append(f"- **Accuracy Score:** {ar.accuracy_score:.1%}")
            lines.append(f"- **Reasoning:** {ar.reasoning}")
            lines.append("")
        
        # Skill Data
        if report.skill_data:
            lines.append("## 🔧 Integrated Skill Data")
            lines.append("")
            
            for sd in report.skill_data:
                if sd.success:
                    skill_emoji = {
                        "crypto-price": "💰",
                        "yahoo-finance": "📈",
                        "polymarket": "🎯",
                        "news-summarizer": "📰",
                        "weather": "🌤️",
                        "base": "🔷",
                    }.get(sd.skill_name, "🔧")
                    
                    lines.append(f"### {skill_emoji} {sd.skill_name}")
                    lines.append(f"- **Query:** {sd.query}")
                    
                    if isinstance(sd.result, dict):
                        for key, value in sd.result.items():
                            lines.append(f"- **{key}:** {value}")
                    else:
                        lines.append(f"- **Result:** {sd.result}")
                    lines.append("")
        
        # Insights
        lines.append("## 💡 Strategic Insights")
        lines.append("")
        
        for insight in report.insights:
            lines.append(f"- {insight}")
        lines.append("")
        
        # Metadata
        lines.append("## 📋 Report Metadata")
        lines.append("")
        lines.append(f"- **Simulation Duration:** {report.metadata.simulation_duration:.2f}s")
        lines.append(f"- **Number of Agents:** {report.metadata.num_agents}")
        lines.append(f"- **Number of Rounds:** {report.metadata.num_rounds}")
        lines.append(f"- **Tags:** {', '.join(report.metadata.tags)}")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by Swimming Pauls ReportAgent*")
        
        return "\n".join(lines)
    
    @staticmethod
    def to_html(report: Report) -> str:
        """Convert report to HTML format."""
        # Use the HTMLReportGenerator from visualization module
        try:
            from .visualization import HTMLReportConfig
        except ImportError:
            from visualization import HTMLReportConfig
        
        # Create a simulated result for the visualizer
        # This is a simplified HTML generation
        # Full implementation would integrate with ScalesVisualizer
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            f"<title>{report.metadata.title}</title>",
            "<style>",
            ReportFormatter._get_css_styles(),
            "</style>",
            "</head>",
            "<body>",
            ReportFormatter._generate_html_body(report),
            "</body>",
            "</html>",
        ]
        
        return "\n".join(html_parts)
    
    @staticmethod
    def _get_css_styles() -> str:
        """Get CSS styles for HTML reports."""
        return """
        :root { --bg: #0a0a0a; --fg: #e0e0e0; --card: #1a1a1a; --accent: #00bcd4; 
                --bullish: #4caf50; --bearish: #f44336; --neutral: #ff9800; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: var(--bg); color: var(--fg); line-height: 1.6; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { text-align: center; padding: 40px 0; border-bottom: 2px solid var(--accent); margin-bottom: 40px; }
        h1 { font-size: 2.5em; color: var(--accent); margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .card { background: var(--card); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card h2 { color: var(--accent); margin-bottom: 15px; font-size: 1.3em; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; }
        .consensus-box { text-align: center; padding: 30px; border-radius: 12px; margin: 20px 0; font-size: 1.5em; font-weight: bold; }
        .consensus-bullish { background: linear-gradient(135deg, rgba(76,175,80,0.2), rgba(76,175,80,0.05)); border: 2px solid var(--bullish); }
        .consensus-bearish { background: linear-gradient(135deg, rgba(244,67,54,0.2), rgba(244,67,54,0.05)); border: 2px solid var(--bearish); }
        .consensus-neutral { background: linear-gradient(135deg, rgba(255,152,0,0.2), rgba(255,152,0,0.05)); border: 2px solid var(--neutral); }
        .agent-item { display: flex; align-items: center; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 10px; }
        .agent-rank { width: 30px; font-weight: bold; color: var(--accent); }
        .agent-name { flex: 1; font-weight: 500; }
        .agent-persona { font-size: 0.8em; opacity: 0.6; margin-left: 10px; }
        .agent-confidence { font-weight: bold; color: var(--accent); }
        .insight-item { padding: 10px; background: rgba(0,188,212,0.1); border-left: 3px solid var(--accent); margin-bottom: 10px; border-radius: 0 8px 8px 0; }
        .skill-data { padding: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; margin-bottom: 10px; }
        footer { text-align: center; padding: 40px 0; opacity: 0.5; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; }
        """
    
    @staticmethod
    def _generate_html_body(report: Report) -> str:
        """Generate HTML body content."""
        consensus_class = f"consensus-{report.consensus.direction}"
        direction_emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖"}.get(report.consensus.direction, "❓")
        
        # Agent items
        agent_items = ""
        for i, ar in enumerate(report.agent_reasonings[:10], 1):
            dir_emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(ar.direction, "❓")
            agent_items += f"""
            <div class="agent-item">
                <span class="agent-rank">{i}.</span>
                <span class="agent-name">{ar.agent_name} ({ar.persona})</span>
                <span>{dir_emoji} {ar.direction.upper()}</span>
                <span class="agent-confidence" style="margin-left: 20px;">{ar.confidence:.1%}</span>
            </div>
            """
        
        # Insights
        insights_html = ""
        for insight in report.insights:
            insights_html += f'<div class="insight-item">💡 {insight}</div>'
        
        # Skill data
        skills_html = ""
        for sd in report.skill_data:
            if sd.success:
                skills_html += f"""
                <div class="skill-data">
                    <strong>{sd.skill_name}</strong> - Query: {sd.query}<br>
                    <pre>{json.dumps(sd.result, indent=2) if isinstance(sd.result, dict) else sd.result}</pre>
                </div>
                """
        
        return f"""
        <div class="container">
            <header>
                <h1>📊 {report.metadata.title}</h1>
                <p>Report ID: {report.metadata.report_id} | Generated: {report.metadata.created_at}</p>
            </header>
            
            <div class="consensus-box {consensus_class}">
                {direction_emoji} FINAL CONSENSUS: {report.consensus.direction.upper()}
                <br>
                <small>Confidence: {report.consensus.confidence:.1%} | Sentiment: {report.consensus.sentiment:+.3f} | Strength: {report.consensus.strength.title()}</small>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>🎭 Agent Reasonings</h2>
                    {agent_items}
                </div>
                
                <div class="card">
                    <h2>💡 Strategic Insights</h2>
                    {insights_html}
                </div>
            </div>
            
            <div class="card">
                <h2>🔧 Integrated Skill Data</h2>
                {skills_html or "<p>No skill data integrated.</p>"}
            </div>
            
            <footer>
                <p>Generated by Swimming Pauls ReportAgent | {report.metadata.num_agents} agents | {report.metadata.num_rounds} rounds</p>
            </footer>
        </div>
        """
    
    @staticmethod
    def to_json(report: Report) -> str:
        """Convert report to JSON format."""
        return json.dumps(report.to_dict(), indent=2)


class ReportStorage:
    """
    Manages persistence of reports with unique IDs.
    """
    
    def __init__(self, base_dir: str = "~/.openclaw/workspace/swimming_pauls/reports"):
        self.base_dir = Path(os.path.expanduser(base_dir))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.markdown_dir = self.base_dir / "markdown"
        self.html_dir = self.base_dir / "html"
        self.json_dir = self.base_dir / "json"
        
        for d in [self.markdown_dir, self.html_dir, self.json_dir]:
            d.mkdir(exist_ok=True)
        
        # Index file
        self.index_file = self.base_dir / "report_index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the report index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return json.load(f)
        return {"reports": [], "count": 0}
    
    def _save_index(self) -> None:
        """Save the report index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, indent=2, fp=f)
    
    def save_report(self, report: Report) -> Dict[str, str]:
        """Save a report in all formats."""
        report_id = report.metadata.report_id
        
        # Generate content
        md_content = ReportFormatter.to_markdown(report)
        html_content = ReportFormatter.to_html(report)
        json_content = ReportFormatter.to_json(report)
        
        # Save files
        md_path = self.markdown_dir / f"{report_id}.md"
        html_path = self.html_dir / f"{report_id}.html"
        json_path = self.json_dir / f"{report_id}.json"
        
        with open(md_path, 'w') as f:
            f.write(md_content)
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        with open(json_path, 'w') as f:
            f.write(json_content)
        
        # Update index
        self.index["reports"].append({
            "report_id": report_id,
            "title": report.metadata.title,
            "created_at": report.metadata.created_at,
            "topic": report.metadata.topic,
            "direction": report.consensus.direction,
            "tags": report.metadata.tags,
        })
        self.index["count"] = len(self.index["reports"])
        self._save_index()
        
        return {
            "report_id": report_id,
            "markdown": str(md_path),
            "html": str(html_path),
            "json": str(json_path),
        }
    
    def get_report(self, report_id: str, format: str = "json") -> Optional[str]:
        """Retrieve a report by ID and format."""
        if format == "markdown":
            path = self.markdown_dir / f"{report_id}.md"
        elif format == "html":
            path = self.html_dir / f"{report_id}.html"
        else:
            path = self.json_dir / f"{report_id}.json"
        
        if path.exists():
            with open(path, 'r') as f:
                return f.read()
        return None
    
    def list_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all reports with metadata."""
        return self.index["reports"][-limit:]
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a report by ID."""
        # Remove files
        for d in [self.markdown_dir, self.html_dir, self.json_dir]:
            for ext in [".md", ".html", ".json"]:
                path = d / f"{report_id}{ext}"
                if path.exists():
                    path.unlink()
        
        # Update index
        self.index["reports"] = [
            r for r in self.index["reports"] if r["report_id"] != report_id
        ]
        self.index["count"] = len(self.index["reports"])
        self._save_index()
        
        return True


class ReportAgent:
    """
    Main agent for generating comprehensive reports from Swimming Pauls simulations.
    
    Features:
    - Compiles prediction findings from simulations
    - Integrates with OpenClaw skills for real-time data
    - Generates formatted reports (Markdown/HTML/JSON)
    - Persists reports with unique IDs
    - Provides insights and visualizations
    
    Example:
        agent = ReportAgent()
        report = await agent.generate_report(simulation_result, agents, topic="BTC price")
        paths = agent.save_report(report)
        print(f"Report saved: {paths['html']}")
    """
    
    def __init__(
        self,
        storage_dir: Optional[str] = None,
        enable_skills: bool = True,
    ):
        self.compiler = ReportCompiler()
        self.storage = ReportStorage(storage_dir) if storage_dir else ReportStorage()
        self.enable_skills = enable_skills
        self.generated_reports: List[str] = []
    
    async def generate_report(
        self,
        result: SimulationResult,
        agents: List[Agent],
        topic: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Report:
        """
        Generate a comprehensive report from simulation results.
        
        Args:
            result: SimulationResult from SwimmingPauls
            agents: List of Agent objects
            topic: Optional topic for skill enrichment
            title: Optional custom report title
            
        Returns:
            Report object with all components
        """
        return await self.compiler.compile_report(result, agents, topic, title)
    
    def save_report(self, report: Report) -> Dict[str, str]:
        """
        Save a report to storage.
        
        Args:
            report: Report object to save
            
        Returns:
            Dictionary with paths to saved files
        """
        paths = self.storage.save_report(report)
        self.generated_reports.append(report.metadata.report_id)
        return paths
    
    async def generate_and_save(
        self,
        result: SimulationResult,
        agents: List[Agent],
        topic: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Tuple[Report, Dict[str, str]]:
        """
        Generate and save a report in one step.
        
        Returns:
            Tuple of (Report, paths dict)
        """
        report = await self.generate_report(result, agents, topic, title)
        paths = self.save_report(report)
        return report, paths
    
    def get_report(self, report_id: str, format: str = "html") -> Optional[str]:
        """
        Retrieve a saved report.
        
        Args:
            report_id: Unique report ID
            format: "html", "markdown", or "json"
            
        Returns:
            Report content as string, or None if not found
        """
        return self.storage.get_report(report_id, format)
    
    def list_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all generated reports."""
        return self.storage.list_reports(limit)
    
    def export_report(
        self, 
        report: Report, 
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """
        Export a report to a specific format without saving.
        
        Args:
            report: Report object
            format: Desired output format
            
        Returns:
            Formatted report string
        """
        if format == ReportFormat.MARKDOWN:
            return ReportFormatter.to_markdown(report)
        elif format == ReportFormat.HTML:
            return ReportFormatter.to_html(report)
        else:
            return ReportFormatter.to_json(report)
    
    def get_insights_summary(self, report: Report) -> str:
        """Get a quick text summary of report insights."""
        lines = [
            f"📊 {report.metadata.title}",
            f"Consensus: {report.consensus.direction.upper()} ({report.consensus.strength})",
            f"Confidence: {report.consensus.confidence:.1%}",
            "",
            "Key Insights:",
        ]
        for i, insight in enumerate(report.insights[:5], 1):
            lines.append(f"  {i}. {insight}")
        
        return "\n".join(lines)


# =============================================================================
# Convenience Functions
# =============================================================================

async def quick_report(
    result: SimulationResult,
    agents: List[Agent],
    topic: Optional[str] = None,
    save: bool = True,
) -> Tuple[Report, Optional[Dict[str, str]]]:
    """
    Quick report generation.
    
    Args:
        result: SimulationResult
        agents: List of agents
        topic: Optional topic
        save: Whether to save the report
        
    Returns:
        Tuple of (Report, paths dict or None)
    """
    agent = ReportAgent()
    report = await agent.generate_report(result, agents, topic)
    
    if save:
        paths = agent.save_report(report)
        return report, paths
    return report, None


def format_report_markdown(report: Report) -> str:
    """Quick markdown export."""
    return ReportFormatter.to_markdown(report)


def format_report_html(report: Report) -> str:
    """Quick HTML export."""
    return ReportFormatter.to_html(report)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Main classes
    "ReportAgent",
    "ReportCompiler",
    "ReportStorage",
    "SkillIntegrator",
    "ReportFormatter",
    
    # Data classes
    "Report",
    "ReportMetadata",
    "ConsensusSummary",
    "AgentReasoning",
    "SkillData",
    "ReportFormat",
    
    # Functions
    "quick_report",
    "format_report_markdown",
    "format_report_html",
]