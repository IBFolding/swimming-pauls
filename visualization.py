"""
Scales v1.0 - Multi-Agent Simulation Engine
Rich visualization outputs for simulation results.

Features:
- ASCII/terminal charts for confidence distributions
- Agent sentiment timelines
- Consensus evolution graphs
- HTML report generator with interactive charts
"""
import json
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

try:
    import plotext as plt
    PLOTEXT_AVAILABLE = True
except ImportError:
    PLOTEXT_AVAILABLE = False

try:
    import matplotlib.pyplot as mpl_plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, FancyBboxPatch
    from matplotlib.collections import LineCollection
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from simulation import SimulationResult, SimulationRound
from agent import Agent, AgentPrediction, PersonaType


# ═══════════════════════════════════════════════════════════════════════════════
# ASCII / TERMINAL VISUALIZATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalCharts:
    """Generate ASCII/terminal charts for simulation results."""
    
    @staticmethod
    def confidence_distribution(
        predictions: List[AgentPrediction],
        agents: List[Agent],
        width: int = 60,
        height: int = 12,
    ) -> str:
        """
        Create ASCII histogram of confidence distribution.
        
        Args:
            predictions: List of agent predictions
            agents: List of agents for name mapping
            width: Chart width in characters
            height: Chart height in characters
            
        Returns:
            ASCII chart as string
        """
        if not predictions:
            return "No predictions to visualize."
        
        # Build agent name map
        agent_map = {a.id: a.name for a in agents}
        
        # Group by direction
        bullish_confs = [p.confidence for p in predictions if p.direction == "bullish"]
        bearish_confs = [p.confidence for p in predictions if p.direction == "bearish"]
        neutral_confs = [p.confidence for p in predictions if p.direction == "neutral"]
        
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + " CONFIDENCE DISTRIBUTION ".center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # Summary stats
        all_confs = [p.confidence for p in predictions]
        avg_conf = sum(all_confs) / len(all_confs)
        lines.append(f"║  📊 Avg Confidence: {avg_conf:.1%}".ljust(width - 1) + "║")
        lines.append(f"║  📈 Bullish: {len(bullish_confs)}  📉 Bearish: {len(bearish_confs)}  ➡️ Neutral: {len(neutral_confs)}".ljust(width - 1) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # Create histogram bars
        bins = 10
        bin_size = 1.0 / bins
        
        bullish_hist = [0] * bins
        bearish_hist = [0] * bins
        neutral_hist = [0] * bins
        
        for c in bullish_confs:
            idx = min(int(c / bin_size), bins - 1)
            bullish_hist[idx] += 1
        for c in bearish_confs:
            idx = min(int(c / bin_size), bins - 1)
            bearish_hist[idx] += 1
        for c in neutral_confs:
            idx = min(int(c / bin_size), bins - 1)
            neutral_hist[idx] += 1
        
        max_count = max(max(bullish_hist), max(bearish_hist), max(neutral_hist), 1)
        
        # Render histogram
        chart_width = width - 15
        lines.append("║  Confidence │ Bullish  │ Bearish  │ Neutral".ljust(width - 1) + "║")
        lines.append("║  " + "─" * (width - 4) + "║")
        
        for i in range(bins - 1, -1, -1):
            low = i * bin_size
            high = (i + 1) * bin_size
            label = f"{low:.1f}-{high:.1f}"
            
            b_bar = "█" * int((bullish_hist[i] / max_count) * (chart_width // 3))
            be_bar = "█" * int((bearish_hist[i] / max_count) * (chart_width // 3))
            n_bar = "█" * int((neutral_hist[i] / max_count) * (chart_width // 3))
            
            line = f"║  {label:>6} │ {b_bar:<8} │ {be_bar:<8} │ {n_bar}".ljust(width - 1) + "║"
            lines.append(line)
        
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def agent_performance_bars(
        agents: List[Agent],
        width: int = 60,
    ) -> str:
        """
        Create ASCII bar chart of agent performance.
        
        Args:
            agents: List of agents
            width: Chart width in characters
            
        Returns:
            ASCII chart as string
        """
        if not agents:
            return "No agents to visualize."
        
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + " AGENT PERFORMANCE RANKING ".center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # Sort by accuracy
        sorted_agents = sorted(agents, key=lambda a: a.memory.accuracy_score, reverse=True)
        
        bar_width = width - 25
        max_acc = max(a.memory.accuracy_score for a in agents) if agents else 1.0
        
        for i, agent in enumerate(sorted_agents, 1):
            acc = agent.memory.accuracy_score
            bar_len = int((acc / max_acc) * bar_width) if max_acc > 0 else 0
            
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            persona_emoji = {
                PersonaType.ANALYST: "📊",
                PersonaType.TRADER: "⚡",
                PersonaType.HEDGIE: "🛡️",
                PersonaType.VISIONARY: "🔮",
                PersonaType.SKEPTIC: "🤔",
            }.get(agent.persona, "👤")
            
            bar = "█" * bar_len + "░" * (bar_width - bar_len)
            line = f"║ {medal} {persona_emoji} {agent.name:10} │{bar}│ {acc:.1%}".ljust(width - 1) + "║"
            lines.append(line)
        
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def sentiment_timeline(
        result: SimulationResult,
        width: int = 70,
        height: int = 15,
    ) -> str:
        """
        Create ASCII line chart of sentiment evolution over rounds.
        
        Args:
            result: Simulation result
            width: Chart width
            height: Chart height
            
        Returns:
            ASCII chart as string
        """
        if not result.rounds:
            return "No rounds to visualize."
        
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + " SENTIMENT EVOLUTION TIMELINE ".center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # Extract sentiment data
        rounds_data = []
        for r in result.rounds:
            sentiment = r.consensus.get("sentiment", 0)
            confidence = r.consensus.get("confidence", 0)
            direction = r.consensus.get("direction", "neutral")
            rounds_data.append((r.round_number, sentiment, confidence, direction))
        
        # Chart area
        chart_width = width - 12
        chart_height = height - 5
        
        # Y-axis labels
        lines.append("║  +1.0 │" + " " * chart_width + "│ Bullish".ljust(width - 10) + "║")
        
        # Plot points
        for row in range(chart_height):
            y_val = 1.0 - (row / (chart_height - 1)) * 2.0  # 1.0 to -1.0
            
            # Build the row
            row_str = ""
            for col in range(chart_width):
                # Map col to round
                round_idx = int((col / (chart_width - 1)) * (len(rounds_data) - 1))
                sentiment = rounds_data[round_idx][1]
                
                # Check if sentiment is near this y_val
                plot_y = int((1.0 - sentiment) / 2.0 * (chart_height - 1))
                if plot_y == row:
                    direction = rounds_data[round_idx][3]
                    if direction == "bullish":
                        row_str += "▲"
                    elif direction == "bearish":
                        row_str += "▼"
                    else:
                        row_str += "●"
                else:
                    # Grid line at 0
                    if row == chart_height // 2:
                        row_str += "·"
                    else:
                        row_str += " "
            
            y_label = f"{y_val:+.1f}"
            lines.append(f"║ {y_label:>5} │{row_str}│".ljust(width - 1) + "║")
        
        lines.append("║  -1.0 │" + "·" * chart_width + "│ Bearish".ljust(width - 10) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # X-axis labels
        x_labels = ""
        num_rounds = len(rounds_data)
        for i in range(chart_width):
            round_idx = int((i / (chart_width - 1)) * (num_rounds - 1))
            if i % (chart_width // min(num_rounds, 5) or 1) == 0:
                x_labels += str(rounds_data[round_idx][0])
            else:
                x_labels += " "
        lines.append(f"║       └{x_labels:<{chart_width}} Round".ljust(width - 1) + "║")
        
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def consensus_evolution(
        result: SimulationResult,
        width: int = 70,
    ) -> str:
        """
        Create ASCII visualization of consensus evolution.
        
        Args:
            result: Simulation result
            width: Chart width
            
        Returns:
            ASCII chart as string
        """
        if not result.rounds:
            return "No rounds to visualize."
        
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + " CONSENSUS EVOLUTION ".center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        # Headers
        lines.append("║  Round │ Direction │ Confidence │ Strength │ Sentiment │ Consistency".ljust(width - 1) + "║")
        lines.append("║  " + "─" * (width - 5) + "║")
        
        for r in result.rounds:
            c = r.consensus
            direction = c.get("direction", "neutral")
            confidence = c.get("confidence", 0)
            strength = c.get("strength", "weak")
            sentiment = c.get("sentiment", 0)
            
            # Calculate consistency based on previous rounds
            consistency = TerminalCharts._calculate_consistency(result, r.round_number)
            
            emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(direction, "❓")
            strength_emoji = {"strong": "🟢", "moderate": "🟡", "weak": "🔴"}.get(strength, "⚪")
            
            line = f"║  {r.round_number:>4} │   {emoji} {direction:<7} │ {confidence:>9.1%} │ {strength_emoji} {strength:<7} │ {sentiment:>+8.2f} │ {consistency:>8.1%}".ljust(width - 1) + "║"
            lines.append(line)
        
        # Final consensus
        lines.append("║  " + "─" * (width - 5) + "║")
        fc = result.final_consensus
        emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖"}.get(fc.get("direction"), "❓")
        lines.append(f"║  FINAL │   {emoji} {fc.get('direction', 'unknown').upper():<7} │ Sentiment: {fc.get('sentiment', 0):>+.3f} │ Consistency: {fc.get('consistency', 0):>.1%}".ljust(width - 1) + "║")
        
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(lines)
    
    @staticmethod
    def _calculate_consistency(result: SimulationResult, up_to_round: int) -> float:
        """Calculate consensus consistency up to a given round."""
        rounds_data = [r for r in result.rounds if r.round_number <= up_to_round]
        if len(rounds_data) < 2:
            return 1.0
        
        directions = [r.consensus.get("direction") for r in rounds_data]
        if not directions:
            return 0.0
        
        most_common = max(set(directions), key=directions.count)
        matches = sum(1 for d in directions if d == most_common)
        return matches / len(directions)
    
    @staticmethod
    def magnitude_scatter(
        predictions: List[AgentPrediction],
        agents: List[Agent],
        width: int = 70,
        height: int = 15,
    ) -> str:
        """
        Create ASCII scatter plot of confidence vs magnitude.
        
        Args:
            predictions: List of predictions
            agents: List of agents
            width: Chart width
            height: Chart height
            
        Returns:
            ASCII chart as string
        """
        if not predictions:
            return "No predictions to visualize."
        
        lines = []
        lines.append("╔" + "═" * (width - 2) + "╗")
        lines.append("║" + " CONFIDENCE vs MAGNITUDE ".center(width - 2) + "║")
        lines.append("╠" + "═" * (width - 2) + "╣")
        
        chart_width = width - 15
        chart_height = height - 4
        
        # Find ranges
        max_mag = max(p.magnitude for p in predictions) if predictions else 1.0
        
        # Build grid
        grid = [[" " for _ in range(chart_width)] for _ in range(chart_height)]
        
        for p in predictions:
            x = int(p.confidence * (chart_width - 1))
            y = int((1 - p.magnitude / max_mag) * (chart_height - 1))
            
            if p.direction == "bullish":
                grid[y][x] = "▲"
            elif p.direction == "bearish":
                grid[y][x] = "▼"
            else:
                grid[y][x] = "○"
        
        # Render
        lines.append("║  Mag │" + " " * chart_width + " Legend:".ljust(width - 10) + "║")
        lines.append(f"║  {max_mag:.1f} │" + "".join(grid[0]) + " ▲ Bullish".ljust(width - 10) + "║")
        
        for i in range(1, chart_height - 1):
            mag_val = max_mag * (1 - i / (chart_height - 1))
            lines.append(f"║  {mag_val:.1f} │" + "".join(grid[i]) + " ▼ Bearish".ljust(width - 10) + "║")
        
        lines.append(f"║  0.0 │" + "".join(grid[-1]) + " ○ Neutral".ljust(width - 10) + "║")
        lines.append("║      └" + "─" * chart_width + "  ── Confidence".ljust(width - 10) + "║")
        lines.append("║       0%" + " " * (chart_width - 8) + "100%".ljust(width - 12) + "║")
        lines.append("╚" + "═" * (width - 2) + "╝")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# PLOTEXT-BASED TERMINAL VISUALIZATIONS (Enhanced)
# ═══════════════════════════════════════════════════════════════════════════════

class PlotextCharts:
    """Generate enhanced terminal charts using plotext."""
    
    @staticmethod
    def sentiment_timeline_plotext(
        result: SimulationResult,
        title: str = "Sentiment Evolution",
    ) -> str:
        """
        Create enhanced sentiment timeline using plotext.
        
        Args:
            result: Simulation result
            title: Chart title
            
        Returns:
            Plotext chart as string (use plt.show() to display)
        """
        if not PLOTEXT_AVAILABLE:
            return "plotext not installed. Use: pip install plotext"
        
        if not result.rounds:
            return "No rounds to visualize."
        
        plt.clear_figure()
        plt.theme("dark")
        plt.title(title)
        plt.xlabel("Round")
        plt.ylabel("Sentiment")
        
        # Extract data
        rounds = [r.round_number for r in result.rounds]
        sentiments = [r.consensus.get("sentiment", 0) for r in result.rounds]
        confidences = [r.consensus.get("confidence", 0) for r in result.rounds]
        
        # Plot sentiment line
        plt.plot(rounds, sentiments, label="Sentiment", color="cyan", marker="●")
        
        # Plot confidence as area
        plt.plot(rounds, confidences, label="Confidence", color="green", marker="▪")
        
        # Add zero line
        plt.hline(0, color="white", style="dashed")
        
        plt.ylim(-1.2, 1.2)
        plt.grid(True)
        plt.legend()
        
        return plt.build()
    
    @staticmethod
    def confidence_histogram_plotext(
        predictions: List[AgentPrediction],
        title: str = "Confidence Distribution",
    ) -> str:
        """
        Create histogram of confidence distribution using plotext.
        
        Args:
            predictions: List of predictions
            title: Chart title
            
        Returns:
            Plotext chart as string
        """
        if not PLOTEXT_AVAILABLE:
            return "plotext not installed. Use: pip install plotext"
        
        if not predictions:
            return "No predictions to visualize."
        
        plt.clear_figure()
        plt.theme("dark")
        plt.title(title)
        plt.xlabel("Confidence")
        plt.ylabel("Count")
        
        # Group by direction
        bullish = [p.confidence for p in predictions if p.direction == "bullish"]
        bearish = [p.confidence for p in predictions if p.direction == "bearish"]
        neutral = [p.confidence for p in predictions if p.direction == "neutral"]
        
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        if bullish:
            plt.hist(bullish, bins=bins, label="Bullish", color="green", fill=True)
        if bearish:
            plt.hist(bearish, bins=bins, label="Bearish", color="red", fill=True)
        if neutral:
            plt.hist(neutral, bins=bins, label="Neutral", color="yellow", fill=True)
        
        plt.grid(True)
        plt.legend()
        
        return plt.build()
    
    @staticmethod
    def agent_accuracy_bars_plotext(
        agents: List[Agent],
        title: str = "Agent Accuracy",
    ) -> str:
        """
        Create bar chart of agent accuracy using plotext.
        
        Args:
            agents: List of agents
            title: Chart title
            
        Returns:
            Plotext chart as string
        """
        if not PLOTEXT_AVAILABLE:
            return "plotext not installed. Use: pip install plotext"
        
        if not agents:
            return "No agents to visualize."
        
        plt.clear_figure()
        plt.theme("dark")
        plt.title(title)
        plt.xlabel("Agent")
        plt.ylabel("Accuracy")
        
        names = [a.name for a in agents]
        accuracies = [a.memory.accuracy_score for a in agents]
        
        # Color based on accuracy
        colors = []
        for acc in accuracies:
            if acc >= 0.7:
                colors.append("green")
            elif acc >= 0.5:
                colors.append("yellow")
            else:
                colors.append("red")
        
        plt.bar(names, accuracies, color=colors)
        plt.ylim(0, 1.0)
        plt.grid(True, axis="y")
        
        return plt.build()


# ═══════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB-BASED STATIC CHARTS
# ═══════════════════════════════════════════════════════════════════════════════

class MatplotlibCharts:
    """Generate static charts using matplotlib."""
    
    @staticmethod
    def save_sentiment_timeline(
        result: SimulationResult,
        filepath: str,
        figsize: Tuple[int, int] = (12, 6),
    ) -> None:
        """
        Save sentiment timeline chart to file.
        
        Args:
            result: Simulation result
            filepath: Output file path
            figsize: Figure size
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not installed. Use: pip install matplotlib")
            return
        
        if not result.rounds:
            print("No rounds to visualize.")
            return
        
        fig, ax = mpl_plt.subplots(figsize=figsize)
        
        # Extract data
        rounds = [r.round_number for r in result.rounds]
        sentiments = [r.consensus.get("sentiment", 0) for r in result.rounds]
        confidences = [r.consensus.get("confidence", 0) for r in result.rounds]
        
        # Plot sentiment
        ax.plot(rounds, sentiments, "o-", label="Sentiment", color="#00bcd4", linewidth=2, markersize=8)
        ax.fill_between(rounds, sentiments, alpha=0.3, color="#00bcd4")
        
        # Plot confidence
        ax.plot(rounds, confidences, "s--", label="Confidence", color="#4caf50", linewidth=2, markersize=6)
        
        # Zero line
        ax.axhline(y=0, color="white", linestyle="--", alpha=0.5)
        
        # Color regions based on sentiment
        for i in range(len(rounds) - 1):
            if sentiments[i] > 0.2:
                ax.axvspan(rounds[i] - 0.4, rounds[i] + 0.4, alpha=0.1, color="green")
            elif sentiments[i] < -0.2:
                ax.axvspan(rounds[i] - 0.4, rounds[i] + 0.4, alpha=0.1, color="red")
        
        ax.set_xlabel("Round", fontsize=12)
        ax.set_ylabel("Score", fontsize=12)
        ax.set_title("Sentiment & Confidence Evolution", fontsize=14, fontweight="bold")
        ax.set_ylim(-1.2, 1.2)
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        
        # Dark theme
        ax.set_facecolor("#1a1a1a")
        fig.patch.set_facecolor("#1a1a1a")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        
        mpl_plt.tight_layout()
        mpl_plt.savefig(filepath, dpi=150, facecolor="#1a1a1a", edgecolor="none")
        mpl_plt.close()
    
    @staticmethod
    def save_confidence_distribution(
        predictions: List[AgentPrediction],
        filepath: str,
        figsize: Tuple[int, int] = (10, 6),
    ) -> None:
        """
        Save confidence distribution chart to file.
        
        Args:
            predictions: List of predictions
            filepath: Output file path
            figsize: Figure size
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not installed.")
            return
        
        if not predictions:
            print("No predictions to visualize.")
            return
        
        fig, ax = mpl_plt.subplots(figsize=figsize)
        
        # Group by direction
        bullish = [p.confidence for p in predictions if p.direction == "bullish"]
        bearish = [p.confidence for p in predictions if p.direction == "bearish"]
        neutral = [p.confidence for p in predictions if p.direction == "neutral"]
        
        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        ax.hist([bullish, bearish, neutral], bins=bins, label=["Bullish", "Bearish", "Neutral"],
                color=["#4caf50", "#f44336", "#ff9800"], alpha=0.8, edgecolor="white")
        
        ax.set_xlabel("Confidence", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title("Confidence Distribution by Direction", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")
        
        # Dark theme
        ax.set_facecolor("#1a1a1a")
        fig.patch.set_facecolor("#1a1a1a")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        
        mpl_plt.tight_layout()
        mpl_plt.savefig(filepath, dpi=150, facecolor="#1a1a1a")
        mpl_plt.close()
    
    @staticmethod
    def save_agent_performance(
        agents: List[Agent],
        filepath: str,
        figsize: Tuple[int, int] = (10, 6),
    ) -> None:
        """
        Save agent performance chart to file.
        
        Args:
            agents: List of agents
            filepath: Output file path
            figsize: Figure size
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not installed.")
            return
        
        if not agents:
            print("No agents to visualize.")
            return
        
        fig, ax = mpl_plt.subplots(figsize=figsize)
        
        # Sort by accuracy
        sorted_agents = sorted(agents, key=lambda a: a.memory.accuracy_score, reverse=True)
        
        names = [a.name for a in sorted_agents]
        accuracies = [a.memory.accuracy_score for a in sorted_agents]
        
        # Color based on persona
        persona_colors = {
            PersonaType.ANALYST: "#2196f3",
            PersonaType.TRADER: "#f44336",
            PersonaType.HEDGIE: "#4caf50",
            PersonaType.VISIONARY: "#9c27b0",
            PersonaType.SKEPTIC: "#ff9800",
        }
        colors = [persona_colors.get(a.persona, "#757575") for a in sorted_agents]
        
        bars = ax.barh(names, accuracies, color=colors, edgecolor="white", alpha=0.8)
        
        # Add value labels
        for bar, acc in zip(bars, accuracies):
            ax.text(acc + 0.02, bar.get_y() + bar.get_height()/2, 
                   f"{acc:.1%}", va="center", color="white", fontsize=10)
        
        ax.set_xlabel("Accuracy Score", fontsize=12)
        ax.set_title("Agent Performance Ranking", fontsize=14, fontweight="bold")
        ax.set_xlim(0, 1.1)
        ax.grid(True, alpha=0.3, axis="x")
        
        # Dark theme
        ax.set_facecolor("#1a1a1a")
        fig.patch.set_facecolor("#1a1a1a")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        
        # Legend for personas
        legend_elements = [mpl_plt.Rectangle((0,0),1,1, facecolor=color, label=persona.value.title())
                          for persona, color in persona_colors.items()]
        ax.legend(handles=legend_elements, loc="lower right", facecolor="#1a1a1a", 
                 edgecolor="white", labelcolor="white")
        
        mpl_plt.tight_layout()
        mpl_plt.savefig(filepath, dpi=150, facecolor="#1a1a1a")
        mpl_plt.close()


# ═══════════════════════════════════════════════════════════════════════════════
# HTML REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HTMLReportConfig:
    """Configuration for HTML report generation."""
    title: str = "Scales Simulation Report"
    theme: str = "dark"  # "dark" or "light"
    include_charts: bool = True
    include_raw_data: bool = False
    max_rounds_display: int = 100


class HTMLReportGenerator:
    """Generate interactive HTML reports with embedded charts."""
    
    def __init__(self, config: Optional[HTMLReportConfig] = None):
        self.config = config or HTMLReportConfig()
    
    def generate(
        self,
        result: SimulationResult,
        agents: List[Agent],
    ) -> str:
        """
        Generate complete HTML report.
        
        Args:
            result: Simulation result
            agents: List of agents
            
        Returns:
            HTML string
        """
        # Prepare data for charts
        chart_data = self._prepare_chart_data(result, agents)
        
        # Build HTML
        html_parts = [
            self._generate_head(),
            self._generate_body(result, agents, chart_data),
            self._generate_scripts(chart_data),
        ]
        
        return "\n".join(html_parts)
    
    def _prepare_chart_data(
        self,
        result: SimulationResult,
        agents: List[Agent],
    ) -> Dict[str, Any]:
        """Prepare data for Chart.js."""
        # Round data
        rounds = [r.round_number for r in result.rounds]
        sentiments = [r.consensus.get("sentiment", 0) for r in result.rounds]
        confidences = [r.consensus.get("confidence", 0) for r in result.rounds]
        
        # Direction counts per round
        bullish_counts = []
        bearish_counts = []
        neutral_counts = []
        for r in result.rounds:
            preds = r.predictions
            bullish_counts.append(sum(1 for p in preds if p.direction == "bullish"))
            bearish_counts.append(sum(1 for p in preds if p.direction == "bearish"))
            neutral_counts.append(sum(1 for p in preds if p.direction == "neutral"))
        
        # Agent performance
        sorted_agents = sorted(agents, key=lambda a: a.memory.accuracy_score, reverse=True)
        agent_names = [a.name for a in sorted_agents]
        agent_accuracies = [a.memory.accuracy_score for a in sorted_agents]
        agent_personas = [a.persona.value for a in sorted_agents]
        
        # Confidence distribution
        all_predictions = []
        for r in result.rounds:
            all_predictions.extend(r.predictions)
        
        conf_bins = {"bullish": [0]*10, "bearish": [0]*10, "neutral": [0]*10}
        for p in all_predictions:
            bin_idx = min(int(p.confidence * 10), 9)
            conf_bins[p.direction][bin_idx] += 1
        
        return {
            "rounds": rounds,
            "sentiments": sentiments,
            "confidences": confidences,
            "bullish_counts": bullish_counts,
            "bearish_counts": bearish_counts,
            "neutral_counts": neutral_counts,
            "agent_names": agent_names,
            "agent_accuracies": agent_accuracies,
            "agent_personas": agent_personas,
            "conf_bins": conf_bins,
            "final_consensus": result.final_consensus,
            "metadata": {
                "start_time": result.start_time,
                "end_time": result.end_time,
                "duration": result.end_time - result.start_time,
                "num_rounds": len(result.rounds),
                "num_agents": len(agents),
            }
        }
    
    def _generate_head(self) -> str:
        """Generate HTML head section."""
        theme_bg = "#0a0a0a" if self.config.theme == "dark" else "#ffffff"
        theme_fg = "#e0e0e0" if self.config.theme == "dark" else "#1a1a1a"
        theme_card = "#1a1a1a" if self.config.theme == "dark" else "#f5f5f5"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg: {theme_bg};
            --fg: {theme_fg};
            --card: {theme_card};
            --accent: #00bcd4;
            --bullish: #4caf50;
            --bearish: #f44336;
            --neutral: #ff9800;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--fg);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 40px;
        }}
        
        h1 {{
            font-size: 2.5em;
            color: var(--accent);
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            opacity: 0.7;
            font-size: 1.1em;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: var(--card);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        
        .card h2 {{
            color: var(--accent);
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat {{
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.7;
            margin-top: 5px;
        }}
        
        .consensus-box {{
            text-align: center;
            padding: 30px;
            border-radius: 12px;
            margin: 20px 0;
            font-size: 1.5em;
            font-weight: bold;
        }}
        
        .consensus-bullish {{
            background: linear-gradient(135deg, rgba(76,175,80,0.2), rgba(76,175,80,0.05));
            border: 2px solid var(--bullish);
        }}
        
        .consensus-bearish {{
            background: linear-gradient(135deg, rgba(244,67,54,0.2), rgba(244,67,54,0.05));
            border: 2px solid var(--bearish);
        }}
        
        .consensus-neutral {{
            background: linear-gradient(135deg, rgba(255,152,0,0.2), rgba(255,152,0,0.05));
            border: 2px solid var(--neutral);
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 15px;
        }}
        
        .chart-container.large {{
            height: 400px;
        }}
        
        .agent-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .agent-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            transition: background 0.2s;
        }}
        
        .agent-item:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        .agent-rank {{
            width: 30px;
            font-weight: bold;
            color: var(--accent);
        }}
        
        .agent-name {{
            flex: 1;
            font-weight: 500;
        }}
        
        .agent-persona {{
            font-size: 0.8em;
            opacity: 0.6;
            margin-left: 10px;
        }}
        
        .agent-accuracy {{
            font-weight: bold;
            color: var(--accent);
        }}
        
        .accuracy-bar {{
            width: 100px;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-left: 15px;
            overflow: hidden;
        }}
        
        .accuracy-fill {{
            height: 100%;
            background: var(--accent);
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        th {{
            color: var(--accent);
            font-weight: 600;
        }}
        
        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge-bullish {{
            background: rgba(76,175,80,0.2);
            color: var(--bullish);
        }}
        
        .badge-bearish {{
            background: rgba(244,67,54,0.2);
            color: var(--bearish);
        }}
        
        .badge-neutral {{
            background: rgba(255,152,0,0.2);
            color: var(--neutral);
        }}
        
        footer {{
            text-align: center;
            padding: 40px 0;
            opacity: 0.5;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 40px;
        }}
    </style>
</head>"""
    
    def _generate_body(
        self,
        result: SimulationResult,
        agents: List[Agent],
        chart_data: Dict[str, Any],
    ) -> str:
        """Generate HTML body section."""
        metadata = chart_data["metadata"]
        final = chart_data["final_consensus"]
        
        direction = final.get("direction", "neutral")
        consensus_class = f"consensus-{direction}"
        direction_emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖"}.get(direction, "❓")
        
        # Agent performance HTML
        agent_list_html = self._generate_agent_list(agents)
        
        # Round table HTML
        round_table_html = self._generate_round_table(result)
        
        return f"""
<body>
    <div class="container">
        <header>
            <h1>📊 {self.config.title}</h1>
            <p class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat">
                <div class="stat-value">{metadata['num_rounds']}</div>
                <div class="stat-label">Rounds</div>
            </div>
            <div class="stat">
                <div class="stat-value">{metadata['num_agents']}</div>
                <div class="stat-label">Agents</div>
            </div>
            <div class="stat">
                <div class="stat-value">{metadata['duration']:.1f}s</div>
                <div class="stat-label">Duration</div>
            </div>
        </div>
        
        <div class="consensus-box {consensus_class}">
            {direction_emoji} FINAL CONSENSUS: {direction.upper()}
            <br>
            <small>Sentiment: {final.get('sentiment', 0):+.3f} | Consistency: {final.get('consistency', 0):.1%}</small>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📈 Sentiment Evolution</h2>
                <div class="chart-container large">
                    <canvas id="sentimentChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Direction Distribution</h2>
                <div class="chart-container large">
                    <canvas id="directionChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Confidence Distribution</h2>
                <div class="chart-container">
                    <canvas id="confidenceChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <h2>🏆 Agent Performance</h2>
                <div class="chart-container">
                    <canvas id="agentChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎭 Agent Rankings</h2>
            <div class="agent-list">
                {agent_list_html}
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Round-by-Round Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Round</th>
                        <th>Direction</th>
                        <th>Sentiment</th>
                        <th>Confidence</th>
                        <th>Strength</th>
                        <th>Predictions</th>
                    </tr>
                </thead>
                <tbody>
                    {round_table_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Generated by Scales v1.0 Multi-Agent Simulation Engine</p>
        </footer>
    </div>
"""
    
    def _generate_agent_list(self, agents: List[Agent]) -> str:
        """Generate HTML for agent rankings."""
        sorted_agents = sorted(agents, key=lambda a: a.memory.accuracy_score, reverse=True)
        
        html_parts = []
        for i, agent in enumerate(sorted_agents, 1):
            acc = agent.memory.accuracy_score
            acc_pct = int(acc * 100)
            
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
            
            html_parts.append(f"""
            <div class="agent-item">
                <span class="agent-rank">{medal}</span>
                <span class="agent-name">{agent.name}</span>
                <span class="agent-persona">({agent.persona.value})</span>
                <div class="accuracy-bar">
                    <div class="accuracy-fill" style="width: {acc_pct}%"></div>
                </div>
                <span class="agent-accuracy">{acc:.1%}</span>
            </div>""")
        
        return "\n".join(html_parts)
    
    def _generate_round_table(self, result: SimulationResult) -> str:
        """Generate HTML for round table."""
        rows = []
        for r in result.rounds:
            c = r.consensus
            direction = c.get("direction", "neutral")
            badge_class = f"badge-{direction}"
            
            num_preds = len(r.predictions)
            
            rows.append(f"""
            <tr>
                <td>{r.round_number}</td>
                <td><span class="badge {badge_class}">{direction.upper()}</span></td>
                <td>{c.get('sentiment', 0):+.3f}</td>
                <td>{c.get('confidence', 0):.1%}</td>
                <td>{c.get('strength', 'weak').title()}</td>
                <td>{num_preds}</td>
            </tr>""")
        
        return "\n".join(rows)
    
    def _generate_scripts(self, chart_data: Dict[str, Any]) -> str:
        """Generate JavaScript for interactive charts."""
        data_json = json.dumps(chart_data)
        
        theme_colors = {
            "dark": {
                "text": "#e0e0e0",
                "grid": "rgba(255,255,255,0.1)",
            },
            "light": {
                "text": "#1a1a1a",
                "grid": "rgba(0,0,0,0.1)",
            }
        }
        colors = theme_colors.get(self.config.theme, theme_colors["dark"])
        
        return f"""
    <script>
        const chartData = {data_json};
        
        Chart.defaults.color = '{colors["text"]}';
        Chart.defaults.borderColor = '{colors["grid"]}';
        
        // Sentiment Evolution Chart
        new Chart(document.getElementById('sentimentChart'), {{
            type: 'line',
            data: {{
                labels: chartData.rounds,
                datasets: [
                    {{
                        label: 'Sentiment',
                        data: chartData.sentiments,
                        borderColor: '#00bcd4',
                        backgroundColor: 'rgba(0,188,212,0.2)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }},
                    {{
                        label: 'Confidence',
                        data: chartData.confidences,
                        borderColor: '#4caf50',
                        backgroundColor: 'transparent',
                        borderDash: [5, 5],
                        tension: 0.4,
                        pointRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }},
                scales: {{
                    y: {{
                        min: -1.2,
                        max: 1.2,
                        grid: {{
                            color: (ctx) => ctx.tick.value === 0 ? 'rgba(255,255,255,0.5)' : '{colors["grid"]}'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top'
                    }}
                }}
            }}
        }});
        
        // Direction Distribution Chart
        new Chart(document.getElementById('directionChart'), {{
            type: 'bar',
            data: {{
                labels: chartData.rounds,
                datasets: [
                    {{
                        label: 'Bullish',
                        data: chartData.bullish_counts,
                        backgroundColor: 'rgba(76,175,80,0.8)',
                        borderColor: '#4caf50',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Bearish',
                        data: chartData.bearish_counts,
                        backgroundColor: 'rgba(244,67,54,0.8)',
                        borderColor: '#f44336',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Neutral',
                        data: chartData.neutral_counts,
                        backgroundColor: 'rgba(255,152,0,0.8)',
                        borderColor: '#ff9800',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Confidence Distribution Chart
        new Chart(document.getElementById('confidenceChart'), {{
            type: 'bar',
            data: {{
                labels: ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
                datasets: [
                    {{
                        label: 'Bullish',
                        data: chartData.conf_bins.bullish,
                        backgroundColor: 'rgba(76,175,80,0.8)',
                        borderColor: '#4caf50',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Bearish',
                        data: chartData.conf_bins.bearish,
                        backgroundColor: 'rgba(244,67,54,0.8)',
                        borderColor: '#f44336',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Neutral',
                        data: chartData.conf_bins.neutral,
                        backgroundColor: 'rgba(255,152,0,0.8)',
                        borderColor: '#ff9800',
                        borderWidth: 1
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Agent Performance Chart
        const personaColors = {{
            analyst: '#2196f3',
            trader: '#f44336',
            hedgie: '#4caf50',
            visionary: '#9c27b0',
            skeptic: '#ff9800'
        }};
        
        new Chart(document.getElementById('agentChart'), {{
            type: 'bar',
            data: {{
                labels: chartData.agent_names,
                datasets: [{{
                    label: 'Accuracy',
                    data: chartData.agent_accuracies,
                    backgroundColor: chartData.agent_personas.map(p => personaColors[p] || '#757575'),
                    borderColor: chartData.agent_personas.map(p => personaColors[p] || '#757575'),
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: {{
                    x: {{
                        min: 0,
                        max: 1
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    def save(
        self,
        result: SimulationResult,
        agents: List[Agent],
        filepath: str,
    ) -> None:
        """
        Generate and save HTML report to file.
        
        Args:
            result: Simulation result
            agents: List of agents
            filepath: Output file path
        """
        html = self.generate(result, agents)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"📄 HTML report saved to: {filepath}")


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED VISUALIZATION INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class ScalesVisualizer:
    """
    Unified interface for all Scales visualizations.
    
    Usage:
        viz = ScalesVisualizer(result, agents)
        viz.print_terminal_summary()
        viz.generate_html_report("report.html")
        viz.save_all_charts("./charts/")
    """
    
    def __init__(
        self,
        result: SimulationResult,
        agents: List[Agent],
    ):
        self.result = result
        self.agents = agents
        self.terminal = TerminalCharts()
        self.plotext = PlotextCharts()
        self.matplotlib = MatplotlibCharts()
        self.html_gen = HTMLReportGenerator()
    
    def print_terminal_summary(self, width: int = 70) -> None:
        """Print complete terminal visualization summary."""
        print("\n" + "=" * width)
        print("📊 SCALES VISUALIZATION SUMMARY".center(width))
        print("=" * width + "\n")
        
        # Get all predictions
        all_predictions = []
        for r in self.result.rounds:
            all_predictions.extend(r.predictions)
        
        # Confidence distribution
        print(self.terminal.confidence_distribution(all_predictions, self.agents, width))
        print()
        
        # Sentiment timeline
        print(self.terminal.sentiment_timeline(self.result, width))
        print()
        
        # Consensus evolution
        print(self.terminal.consensus_evolution(self.result, width))
        print()
        
        # Agent performance
        print(self.terminal.agent_performance_bars(self.agents, width))
        print()
        
        # Magnitude scatter
        print(self.terminal.magnitude_scatter(all_predictions, self.agents, width))
        print()
        
        print("=" * width)
    
    def show_plotext_charts(self) -> None:
        """Display charts using plotext in terminal."""
        if not PLOTEXT_AVAILABLE:
            print("plotext not installed. Use: pip install plotext")
            return
        
        all_predictions = []
        for r in self.result.rounds:
            all_predictions.extend(r.predictions)
        
        print("\n📈 SENTIMENT TIMELINE")
        self.plotext.sentiment_timeline_plotext(self.result)
        plt.show()
        
        print("\n📊 CONFIDENCE DISTRIBUTION")
        self.plotext.confidence_histogram_plotext(all_predictions)
        plt.show()
        
        print("\n🏆 AGENT PERFORMANCE")
        self.plotext.agent_accuracy_bars_plotext(self.agents)
        plt.show()
    
    def save_all_charts(
        self,
        output_dir: str,
        prefix: str = "scales",
    ) -> None:
        """
        Save all matplotlib charts to directory.
        
        Args:
            output_dir: Output directory path
            prefix: Filename prefix
        """
        import os
        
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib not installed. Use: pip install matplotlib")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        all_predictions = []
        for r in self.result.rounds:
            all_predictions.extend(r.predictions)
        
        # Save charts
        self.matplotlib.save_sentiment_timeline(
            self.result,
            os.path.join(output_dir, f"{prefix}_sentiment.png")
        )
        print(f"📈 Saved: {prefix}_sentiment.png")
        
        self.matplotlib.save_confidence_distribution(
            all_predictions,
            os.path.join(output_dir, f"{prefix}_confidence.png")
        )
        print(f"📊 Saved: {prefix}_confidence.png")
        
        self.matplotlib.save_agent_performance(
            self.agents,
            os.path.join(output_dir, f"{prefix}_agents.png")
        )
        print(f"🏆 Saved: {prefix}_agents.png")
    
    def generate_html_report(
        self,
        filepath: str,
        title: Optional[str] = None,
    ) -> None:
        """
        Generate interactive HTML report.
        
        Args:
            filepath: Output file path
            title: Report title
        """
        if title:
            self.html_gen.config.title = title
        self.html_gen.save(self.result, self.agents, filepath)
    
    def export_all(
        self,
        output_dir: str,
        name: str = "simulation",
    ) -> Dict[str, str]:
        """
        Export all visualization formats.
        
        Args:
            output_dir: Output directory
            name: Base name for files
            
        Returns:
            Dictionary of exported file paths
        """
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        exported = {}
        
        # Terminal summary (text file)
        summary_path = os.path.join(output_dir, f"{name}_summary.txt")
        with open(summary_path, "w") as f:
            # Redirect print to file
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            self.print_terminal_summary()
            output = sys.stdout.getvalue()
            sys.stdout = old_stdout
            
            f.write(output)
        exported["terminal_summary"] = summary_path
        
        # HTML report
        html_path = os.path.join(output_dir, f"{name}_report.html")
        self.generate_html_report(html_path, title=f"Scales: {name.title()}")
        exported["html_report"] = html_path
        
        # Matplotlib charts
        if MATPLOTLIB_AVAILABLE:
            charts_dir = os.path.join(output_dir, "charts")
            self.save_all_charts(charts_dir, prefix=name)
            exported["charts_dir"] = charts_dir
        
        return exported


# ═══════════════════════════════════════════════════════════════════════════════
# QUICK UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def quick_visualize(
    result: SimulationResult,
    agents: List[Agent],
    output_dir: Optional[str] = None,
) -> None:
    """
    Quick visualization of simulation results.
    
    Args:
        result: Simulation result
        agents: List of agents
        output_dir: Optional directory to save outputs
    """
    viz = ScalesVisualizer(result, agents)
    
    # Always print terminal summary
    viz.print_terminal_summary()
    
    # Save to files if output dir provided
    if output_dir:
        exported = viz.export_all(output_dir)
        print(f"\n📁 Exported to: {output_dir}")
        for key, path in exported.items():
            print(f"   • {key}: {path}")


def print_confidence_chart(
    predictions: List[AgentPrediction],
    agents: List[Agent],
) -> None:
    """Quick print confidence distribution chart."""
    chart = TerminalCharts.confidence_distribution(predictions, agents)
    print(chart)


def print_sentiment_timeline(result: SimulationResult) -> None:
    """Quick print sentiment timeline."""
    chart = TerminalCharts.sentiment_timeline(result)
    print(chart)


def print_agent_ranking(agents: List[Agent]) -> None:
    """Quick print agent ranking."""
    chart = TerminalCharts.agent_performance_bars(agents)
    print(chart)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Demo with mock data
    print("Scales Visualization Module")
    print("=" * 50)
    print("\nThis module provides rich visualization for Scales simulations.")
    print("\nFeatures:")
    print("  • ASCII/Terminal charts (no dependencies)")
    print("  • Plotext-enhanced terminal charts")
    print("  • Matplotlib static charts")
    print("  • Interactive HTML reports with Chart.js")
    print("\nUsage:")
    print("  from visualization import ScalesVisualizer, quick_visualize")
    print("  viz = ScalesVisualizer(result, agents)")
    print("  viz.print_terminal_summary()")
    print("  viz.generate_html_report('report.html')")
