"""
Helper Agents for Swimming Pauls
Specialized assistants that monitor, optimize, and help manage the Paul ecosystem.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import sqlite3


class AgentRole(Enum):
    """Types of helper agents."""
    MONITOR = "monitor"           # Watches system health
    OPTIMIZER = "optimizer"       # Improves performance
    CURATOR = "curator"          # Manages Paul quality
    ANALYST = "analyst"          # Generates insights
    COACH = "coach"              # Helps users
    ARCHITECT = "architect"      # Designs new features


@dataclass
class AgentReport:
    """Report from a helper agent."""
    agent_name: str
    role: AgentRole
    timestamp: datetime
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    recommendations: List[str]
    data: Optional[Dict] = None


class HelperAgent:
    """
    Base class for helper agents.
    
    Helper agents run alongside the main system to:
    - Monitor health and performance
    - Suggest improvements
    - Automate tasks
    - Provide insights
    """
    
    def __init__(self, name: str, role: AgentRole, check_interval: int = 300):
        self.name = name
        self.role = role
        self.check_interval = check_interval  # seconds
        self.active = False
        self.report_history: List[AgentReport] = []
        
    async def run(self):
        """Main agent loop."""
        self.active = True
        while self.active:
            try:
                report = await self.check()
                if report:
                    self.report_history.append(report)
                    await self.act(report)
            except Exception as e:
                print(f"❌ {self.name} error: {e}")
                
            await asyncio.sleep(self.check_interval)
            
    async def check(self) -> Optional[AgentReport]:
        """
        Check the system. Override in subclass.
        Returns report if issue/opportunity found.
        """
        pass
    
    async def act(self, report: AgentReport):
        """
        Take action based on report. Override in subclass.
        """
        pass
    
    def stop(self):
        """Stop the agent."""
        self.active = False


class MonitorAgent(HelperAgent):
    """
    Watches system health and alerts on issues.
    
    Checks:
    - Database size (alert if > 1GB)
    - Memory usage (alert if > 80%)
    - Failed predictions (alert if accuracy < 50%)
    - Stuck Pauls (alert if Paul hasn't acted in 24h)
    """
    
    def __init__(self):
        super().__init__("MonitorAgent", AgentRole.MONITOR, check_interval=60)
        
    async def check(self) -> Optional[AgentReport]:
        """Check system health."""
        import psutil
        
        issues = []
        data = {}
        
        # Check memory
        memory = psutil.virtual_memory()
        data['memory_percent'] = memory.percent
        if memory.percent > 80:
            issues.append(f"High memory usage: {memory.percent}%")
            
        # Check database
        try:
            import os
            db_size = os.path.getsize("data/predictions.db") / (1024**2)  # MB
            data['db_size_mb'] = db_size
            if db_size > 1000:
                issues.append(f"Database large: {db_size:.0f}MB")
        except:
            pass
            
        # Check Paul activity
        conn = sqlite3.connect("data/paul_performance.db")
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT paul_name, last_active FROM paul_performance
                WHERE last_active < datetime('now', '-1 day')
            ''')
            inactive = cursor.fetchall()
            if inactive:
                issues.append(f"{len(inactive)} Pauls inactive for 24h+")
                data['inactive_pauls'] = [p[0] for p in inactive[:5]]
        except:
            pass
        finally:
            conn.close()
            
        if issues:
            return AgentReport(
                agent_name=self.name,
                role=self.role,
                timestamp=datetime.now(),
                severity="WARNING" if len(issues) < 3 else "CRITICAL",
                message="; ".join(issues),
                recommendations=[
                    "Run database cleanup" if "Database" in "; ".join(issues) else None,
                    "Restart local_agent" if "memory" in "; ".join(issues).lower() else None,
                ],
                data=data
            )
        return None


class OptimizerAgent(HelperAgent):
    """
    Suggests performance improvements.
    
    Analyzes:
    - Slow queries (predictions taking > 5s)
    - Cache hit rates
    - Skill response times
    - Optimal Paul counts for hardware
    """
    
    def __init__(self):
        super().__init__("OptimizerAgent", AgentRole.OPTIMIZER, check_interval=600)
        
    async def check(self) -> Optional[AgentReport]:
        """Analyze performance and suggest optimizations."""
        recommendations = []
        data = {}
        
        # Check prediction speed
        conn = sqlite3.connect("data/predictions.db")
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT AVG(duration_ms) FROM predictions 
                WHERE timestamp > datetime('now', '-1 hour')
            ''')
            avg_time = cursor.fetchone()[0] or 0
            data['avg_prediction_time_ms'] = avg_time
            
            if avg_time > 5000:  # 5 seconds
                recommendations.append(f"Predictions slow ({avg_time:.0f}ms avg). Consider reducing Paul count or using faster LLM.")
        except:
            pass
        finally:
            conn.close()
            
        # Suggest optimal Paul count based on memory
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        suggested_pauls = int(available_gb / 0.05)  # 50MB per Paul
        
        recommendations.append(f"Optimal Paul count for your system: ~{suggested_pauls}")
        
        if recommendations:
            return AgentReport(
                agent_name=self.name,
                role=self.role,
                timestamp=datetime.now(),
                severity="INFO",
                message="Performance analysis complete",
                recommendations=recommendations,
                data=data
            )
        return None


class CuratorAgent(HelperAgent):
    """
    Manages Paul quality and diversity.
    
    Tasks:
    - Identify underperforming Pauls (accuracy < 40%)
    - Suggest new Paul archetypes to add
    - Check for duplicate/similar Pauls
    - Recommend Pauls to retire
    """
    
    def __init__(self):
        super().__init__("CuratorAgent", AgentRole.CURATOR, check_interval=3600)
        
    async def check(self) -> Optional[AgentReport]:
        """Analyze Paul roster quality."""
        conn = sqlite3.connect("data/paul_performance.db")
        cursor = conn.cursor()
        
        recommendations = []
        data = {}
        
        try:
            # Find underperformers
            cursor.execute('''
                SELECT paul_name, accuracy_rate, total_predictions
                FROM paul_performance
                WHERE accuracy_rate < 0.4 AND total_predictions > 20
                ORDER BY accuracy_rate ASC
            ''')
            underperformers = cursor.fetchall()
            
            if underperformers:
                data['underperformers'] = [
                    {"name": p[0], "accuracy": f"{p[1]:.0%}", "predictions": p[2]}
                    for p in underperformers[:5]
                ]
                recommendations.append(
                    f"Consider retiring {len(underperformers)} underperforming Pauls (accuracy < 40%)"
                )
                
            # Check for top performers
            cursor.execute('''
                SELECT paul_name, accuracy_rate
                FROM paul_performance
                WHERE accuracy_rate > 0.7 AND total_predictions > 20
                ORDER BY accuracy_rate DESC
                LIMIT 5
            ''')
            top_performers = cursor.fetchall()
            
            if top_performers:
                data['top_performers'] = [
                    {"name": p[0], "accuracy": f"{p[1]:.0%}"}
                    for p in top_performers
                ]
                recommendations.append(
                    f"Clone top performers: {', '.join([p[0] for p in top_performers[:3]])}"
                )
                
        except:
            pass
        finally:
            conn.close()
            
        if recommendations:
            return AgentReport(
                agent_name=self.name,
                role=self.role,
                timestamp=datetime.now(),
                severity="INFO",
                message="Paul roster analysis complete",
                recommendations=recommendations,
                data=data
            )
        return None


class AnalystAgent(HelperAgent):
    """
    Generates insights from prediction data.
    
    Creates:
    - Daily/weekly prediction summaries
    - Trend analysis (what topics are hot)
    - Accuracy reports by Paul type
    - Market sentiment over time
    """
    
    def __init__(self):
        super().__init__("AnalystAgent", AgentRole.ANALYST, check_interval=86400)  # Daily
        
    async def check(self) -> Optional[AgentReport]:
        """Generate daily insights report."""
        conn = sqlite3.connect("data/predictions.db")
        cursor = conn.cursor()
        
        try:
            # Yesterday's stats
            cursor.execute('''
                SELECT 
                    COUNT(*),
                    AVG(consensus_confidence),
                    consensus_direction
                FROM predictions
                WHERE timestamp > datetime('now', '-1 day')
                GROUP BY consensus_direction
            ''')
            stats = cursor.fetchall()
            
            if not stats:
                return None
                
            insights = []
            total = sum(s[0] for s in stats)
            
            for count, avg_conf, direction in stats:
                pct = count / total * 100
                insights.append(f"{direction}: {count} predictions ({pct:.0f}%)")
                
            return AgentReport(
                agent_name=self.name,
                role=self.role,
                timestamp=datetime.now(),
                severity="INFO",
                message=f"Daily Summary: {total} predictions made",
                recommendations=insights,
                data={"total_predictions": total, "breakdown": stats}
            )
            
        except:
            return None
        finally:
            conn.close()


class CoachAgent(HelperAgent):
    """
    Helps users create better Pauls and predictions.
    
    Provides:
    - Paul creation tips
    - Question optimization
    - Skill recommendations
    - Tutorial guidance
    """
    
    def __init__(self):
        super().__init__("CoachAgent", AgentRole.COACH)
        self.user_sessions: Dict[str, Dict] = {}
        
    def get_tip(self, context: str) -> str:
        """Get contextual help tip."""
        tips = {
            "creating_paul": [
                "Give your Paul a strong backstory - where did they learn their expertise?",
                "Define their blindspots - what biases do they have?",
                "Choose specialties that match their personality",
            ],
            "asking_question": [
                "Be specific: 'Will BTC hit $100K by Dec 2025?' beats 'Will crypto go up?'",
                "Define timeframe - short term vs long term changes everything",
                "Consider: what data would help answer this?",
            ],
            "choosing_pauls": [
                "Use diverse Pauls - mix of optimists and skeptics",
                "More Pauls = deeper debate but longer wait",
                "For market questions, include Trader + Professor + Skeptic",
            ],
        }
        
        if context in tips:
            import random
            return random.choice(tips[context])
        return "Tip: Start with a specific question and diverse Pauls."
        
    def suggest_skills(self, paul_type: str) -> List[str]:
        """Suggest skills for a Paul type."""
        suggestions = {
            "trader": ["crypto_price", "yahoo_finance", "market_sentiment"],
            "professor": ["wikipedia", "rss_feed", "academic_search"],
            "developer": ["github_activity", "tech_news", "documentation"],
            "analyst": ["web_search", "trend_analysis", "data_scraper"],
        }
        return suggestions.get(paul_type.lower(), ["web_search"])


class AgentOrchestrator:
    """
    Manages all helper agents.
    
    Usage:
        orchestrator = AgentOrchestrator()
        await orchestrator.start_all()
        
        # Get all reports
        reports = orchestrator.get_recent_reports()
        
        # Ask coach for tip
        tip = orchestrator.coach.get_tip("creating_paul")
    """
    
    def __init__(self):
        self.agents: Dict[str, HelperAgent] = {}
        self.monitor = MonitorAgent()
        self.optimizer = OptimizerAgent()
        self.curator = CuratorAgent()
        self.analyst = AnalystAgent()
        self.coach = CoachAgent()
        
        self.agents = {
            "monitor": self.monitor,
            "optimizer": self.optimizer,
            "curator": self.curator,
            "analyst": self.analyst,
            "coach": self.coach,
        }
        
    async def start_all(self):
        """Start all background agents."""
        print("🤖 Starting Helper Agents...")
        for name, agent in self.agents.items():
            if name != "coach":  # Coach is on-demand
                asyncio.create_task(agent.run())
                print(f"  ✓ {name} started")
                
    def stop_all(self):
        """Stop all agents."""
        for agent in self.agents.values():
            agent.stop()
            
    def get_recent_reports(self, hours: int = 24) -> List[AgentReport]:
        """Get all reports from last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        reports = []
        
        for agent in self.agents.values():
            for report in agent.report_history:
                if report.timestamp > cutoff:
                    reports.append(report)
                    
        return sorted(reports, key=lambda r: r.timestamp, reverse=True)
        
    def get_system_health(self) -> Dict:
        """Get overall system health summary."""
        return {
            "agents_running": sum(1 for a in self.agents.values() if a.active),
            "total_reports_24h": len(self.get_recent_reports(24)),
            "critical_issues": len([r for r in self.get_recent_reports(24) 
                                   if r.severity == "CRITICAL"]),
            "recommendations_pending": sum(
                len(r.recommendations) for r in self.get_recent_reports(24)
            ),
        }


# CLI
async def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Helper Agent Commands:")
        print("  status      - Check system health")
        print("  start       - Start all agents")
        print("  tip         - Get a coaching tip")
        print("  optimize    - Run optimizer once")
        print("  analyze     - Run analyst once")
        sys.exit(0)
        
    command = sys.argv[1]
    
    orchestrator = AgentOrchestrator()
    
    if command == "status":
        health = orchestrator.get_system_health()
        print("\n🤖 Helper Agent Status")
        print(f"Agents: {health['agents_running']}/4 running")
        print(f"Reports (24h): {health['total_reports_24h']}")
        print(f"Critical issues: {health['critical_issues']}")
        
        # Get recent reports
        reports = orchestrator.get_recent_reports(1)
        if reports:
            print("\nRecent alerts:")
            for r in reports[:3]:
                emoji = "🔴" if r.severity == "CRITICAL" else "🟡" if r.severity == "WARNING" else "🟢"
                print(f"  {emoji} {r.agent_name}: {r.message[:60]}...")
                
    elif command == "tip":
        context = sys.argv[2] if len(sys.argv) > 2 else "general"
        tip = orchestrator.coach.get_tip(context)
        print(f"\n💡 {tip}")
        
    elif command == "start":
        print("Starting helper agents (Ctrl+C to stop)...")
        await orchestrator.start_all()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop_all()
            print("\nStopped.")


if __name__ == "__main__":
    asyncio.run(main())
