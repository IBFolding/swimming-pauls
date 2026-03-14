#!/usr/bin/env python3
"""
SwimmingPauls v2.0 - Comprehensive Examples

This file demonstrates all features of the SwimmingPauls platform:
1. Basic simulations with different agent teams
2. Live data integration
3. Advanced analytics (Monte Carlo, Sensitivity, Backtesting)
4. Visualizations and reports
5. Custom agent creation
6. Memory and persistence

Run with:
    python example.py
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path

from swimming_pauls import (
    SwimmingPauls,
    SwimmingPaulsConfig,
    Agent,
    PersonaType,
    create_agent_team,
    create_film_industry_team,
)


def section(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def example_1_basic_simulation():
    """Example 1: Basic simulation with default settings."""
    section("Example 1: Basic Simulation")
    
    # Initialize with default settings
    pauls = SwimmingPauls()
    
    print("Running 10-round simulation with default agent team...")
    result = await pauls.run_simulation(rounds=10, delay=0.05)
    
    print(f"\n✅ Simulation complete!")
    print(f"   Duration: {result.end_time - result.start_time:.2f}s")
    print(f"   Final consensus: {result.final_consensus['direction'].upper()}")
    print(f"   Sentiment: {result.final_consensus['sentiment']:+.3f}")
    print(f"   Consistency: {result.final_consensus['consistency']:.1%}")
    
    # Show terminal charts
    pauls.print_terminal_charts()
    
    await pauls.close()
    return result


async def example_2_custom_team():
    """Example 2: Custom agent team composition."""
    section("Example 2: Custom Agent Team")
    
    # Create custom team with more analysts and skeptics
    agents = create_agent_team(
        analyst_count=3,
        trader_count=1,
        hedgie_count=2,
        visionary_count=1,
        skeptic_count=2,
    )
    
    print(f"Created team with {len(agents)} agents:")
    for agent in agents:
        print(f"   • {agent.name} ({agent.persona.value})")
    
    pauls = SwimmingPauls(agents=agents)
    
    print("\nRunning simulation...")
    result = await pauls.run_simulation(rounds=15, delay=0.05)
    
    print(f"\nFinal consensus: {result.final_consensus['direction'].upper()}")
    
    await pauls.close()
    return result


async def example_3_film_industry_team():
    """Example 3: Film industry specialized team."""
    section("Example 3: Film Industry Team")
    
    # Create film industry team
    agents = create_film_industry_team(
        producer_count=2,
        director_count=1,
        screenwriter_count=1,
        studio_exec_count=1,
        indie_filmmaker_count=1,
    )
    
    print(f"Created film industry team with {len(agents)} agents:")
    for agent in agents:
        print(f"   • {agent.name} ({agent.persona.value})")
    
    pauls = SwimmingPauls(agents=agents)
    
    # Simulate film project success prediction
    print("\nSimulating film project success prediction...")
    
    # Custom market data for film industry
    def film_market_data(round_num: int):
        return {
            "price_trend": random.uniform(-0.3, 0.3),
            "volume": random.uniform(0.3, 1.0),
            "sentiment": random.uniform(-0.5, 0.5),
            "volatility": random.uniform(0.2, 0.6),
            # Film-specific signals
            "box_office_trend": random.uniform(-0.4, 0.4),
            "audience_score": random.uniform(0.3, 0.9),
            "critic_score": random.uniform(0.2, 0.9),
            "franchise_potential": random.uniform(0.0, 1.0),
        }
    
    result = await pauls.run_simulation(
        rounds=10,
        delay=0.05,
        market_data_feed=film_market_data,
    )
    
    print(f"\nFinal consensus on project success: {result.final_consensus['direction'].upper()}")
    
    await pauls.close()
    return result


async def example_4_monte_carlo():
    """Example 4: Monte Carlo simulation for probabilistic analysis."""
    section("Example 4: Monte Carlo Simulation")
    
    pauls = SwimmingPauls()
    
    print("Running 1000 Monte Carlo simulations...")
    print("(This may take a moment)\n")
    
    def progress(completed, total):
        if completed % 100 == 0:
            pct = completed / total * 100
            print(f"   Progress: {completed}/{total} ({pct:.0f}%)")
    
    result = await pauls.monte_carlo(runs=1000, progress_callback=progress)
    
    print(f"\n📊 Monte Carlo Results:")
    print(f"   Total Runs: {result.total_runs}")
    print(f"   Bullish Probability: {result.bullish_probability:.1%}")
    print(f"   Bearish Probability: {result.bearish_probability:.1%}")
    print(f"   Neutral Probability: {result.neutral_probability:.1%}")
    print(f"   Expected Outcome: {result.expected_outcome:+.3f}")
    print(f"   Average Sentiment: {result.avg_sentiment:+.3f}")
    print(f"   Sentiment Std Dev: {result.sentiment_std:.3f}")
    print(f"   95% Confidence Interval: [{result.confidence_interval_95[0]:+.3f}, {result.confidence_interval_95[1]:+.3f}]")
    print(f"   Value at Risk (95%): {result.value_at_risk_95:.3f}")
    print(f"   Skewness: {result.skewness:.3f}")
    print(f"   Kurtosis: {result.kurtosis:.3f}")
    
    await pauls.close()
    return result


async def example_5_sensitivity_analysis():
    """Example 5: Sensitivity analysis to find key drivers."""
    section("Example 5: Sensitivity Analysis")
    
    pauls = SwimmingPauls()
    
    print("Running sensitivity analysis...")
    print("Testing impact of different market variables...\n")
    
    results = await pauls.sensitivity_analysis(samples=300)
    
    print("📊 Variable Impact Rankings:")
    print(f"   {'Rank':<6}{'Variable':<15}{'Impact':<12}{'Sentiment Corr':<15}{'Accuracy Corr'}")
    print("   " + "-" * 65)
    for r in results:
        print(f"   {r.rank:<6}{r.variable_name:<15}{r.impact_score:<12.3f}{r.correlation_with_sentiment:+.3f}         {r.correlation_with_accuracy:+.3f}")
    
    print(f"\n🎯 Key Insights:")
    print(f"   Most impactful variable: {results[0].variable_name}")
    print(f"   This variable has {results[0].impact_score:.1%} impact on outcomes")
    
    await pauls.close()
    return results


async def example_6_scenario_comparison():
    """Example 6: Compare two market scenarios."""
    section("Example 6: Scenario Comparison")
    
    pauls = SwimmingPauls()
    
    # Define bull vs bear market scenarios
    bull_market = {
        "price_trend": 0.6,
        "volume": 0.9,
        "sentiment": 0.7,
        "volatility": 0.2,
        "momentum": 0.5,
    }
    bear_market = {
        "price_trend": -0.6,
        "volume": 0.4,
        "sentiment": -0.7,
        "volatility": 0.8,
        "momentum": -0.5,
    }
    
    print("Comparing scenarios:")
    print(f"   Bull Market: {bull_market}")
    print(f"   Bear Market: {bear_market}\n")
    
    result = await pauls.compare_scenarios(
        bull_market, bear_market,
        name_a="Bull Market",
        name_b="Bear Market",
        runs=500,
    )
    
    print("📊 Comparison Results:")
    print(f"   Bull Market Win Probability: {result.win_probability_a:.1%}")
    print(f"   Bear Market Win Probability: {result.win_probability_b:.1%}")
    print(f"   Sentiment Difference: {result.sentiment_diff:+.3f}")
    print(f"   Expected Value (Bull): {result.expected_value_a:+.3f}")
    print(f"   Expected Value (Bear): {result.expected_value_b:+.3f}")
    print(f"   Risk Ratio: {result.risk_ratio:.2f}")
    print(f"   Statistical Significance: p={result.statistical_significance:.3f}")
    print(f"\n   → {result.recommendation}")
    
    await pauls.close()
    return result


async def example_7_backtesting():
    """Example 7: Backtest against historical data."""
    section("Example 7: Backtesting")
    
    pauls = SwimmingPauls()
    
    # Generate synthetic historical data
    print("Generating synthetic historical data...")
    historical_data = []
    
    for i in range(100):
        # Random outcome (-1, 0, 1 for bearish, neutral, bullish)
        actual = random.choice([-1, 0, 1])
        
        # Create market data that correlates with outcome
        historical_data.append({
            "price_trend": actual * 0.5 + random.gauss(0, 0.2),
            "volume": random.uniform(0.3, 1.0),
            "sentiment": actual * 0.4 + random.gauss(0, 0.3),
            "volatility": random.uniform(0.1, 0.6),
            "momentum": actual * 0.3 + random.gauss(0, 0.2),
            "actual_outcome": actual,
        })
    
    print(f"Running backtest on {len(historical_data)} data points...\n")
    
    result = await pauls.backtest(historical_data, outcome_key="actual_outcome")
    
    print("📊 Backtest Results:")
    print(f"   Total Predictions: {result.total_predictions}")
    print(f"   Correct: {result.correct_predictions}")
    print(f"   Accuracy Rate: {result.accuracy_rate:.1%}")
    
    print(f"\n   Classification Metrics:")
    for cls in ["bullish", "bearish", "neutral"]:
        if cls in result.precision:
            print(f"     {cls.upper()}:")
            print(f"       Precision: {result.precision[cls]:.1%}")
            print(f"       Recall: {result.recall[cls]:.1%}")
            print(f"       F1 Score: {result.f1_score[cls]:.3f}")
    
    print(f"\n   Trading Metrics:")
    print(f"     Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"     Max Drawdown: {result.max_drawdown:.1%}")
    print(f"     Profit Factor: {result.profit_factor:.2f}")
    
    await pauls.close()
    return result


async def example_8_full_analysis():
    """Example 8: Complete analysis suite."""
    section("Example 8: Full Analysis Suite")
    
    pauls = SwimmingPauls()
    
    print("Running complete analysis suite...")
    print("(Monte Carlo + Sensitivity + Scenario Comparison)\n")
    
    results = await pauls.run_full_analysis()
    
    print("📊 Monte Carlo Results:")
    mc = results["monte_carlo"]
    print(f"   Bullish: {mc['probabilities']['bullish']:.1%}")
    print(f"   Bearish: {mc['probabilities']['bearish']:.1%}")
    print(f"   Expected: {mc['expected_outcome']:+.3f}")
    
    print("\n📈 Sensitivity Analysis:")
    for r in results["sensitivity_analysis"][:3]:
        print(f"   {r['rank']}. {r['variable']}: impact={r['impact_score']:.3f}")
    
    print("\n⚖️  Scenario Comparison:")
    comp = results["scenario_comparison"]
    print(f"   {comp['scenario_a']} vs {comp['scenario_b']}")
    print(f"   Win prob A: {comp['win_probabilities']['a']:.1%}")
    print(f"   Sentiment diff: {comp['sentiment_difference']:+.3f}")
    print(f"   → {comp['recommendation']}")
    
    print("\n📝 Summary:")
    print(f"   Dominant Direction: {results['summary']['dominant_direction']}")
    print(f"   Confidence: {results['summary']['confidence']:.1%}")
    print(f"   Key Drivers: {', '.join(results['summary']['key_drivers'])}")
    
    await pauls.close()
    return results


async def example_9_visualization_export():
    """Example 9: Export visualizations and reports."""
    section("Example 9: Visualization & Export")
    
    pauls = SwimmingPauls()
    
    # Run simulation first
    print("Running simulation for visualization...")
    result = await pauls.run_simulation(rounds=10, delay=0.05)
    
    # Print terminal charts
    print("\n📊 Terminal Charts:")
    pauls.print_terminal_charts()
    
    # Export all visualizations
    output_dir = "./example_output"
    print(f"\n💾 Exporting all visualizations to {output_dir}...")
    exported = pauls.visualize(output_dir=output_dir)
    
    print(f"\n✅ Exported files:")
    for key, path in exported.items():
        print(f"   • {key}: {path}")
    
    # Generate HTML report
    html_path = f"{output_dir}/report.html"
    print(f"\n📄 Generating HTML report: {html_path}")
    pauls.generate_html_report(html_path, title="SwimmingPauls Example Report")
    
    await pauls.close()
    return exported


async def example_10_memory_persistence():
    """Example 10: Memory and persistence features."""
    section("Example 10: Memory & Persistence")
    
    config = SwimmingPaulsConfig(
        enable_persistence=True,
        db_path="~/.swimming_pauls/example_memory.db",
    )
    
    pauls = SwimmingPauls(config=config)
    
    print(f"Session UUID: {pauls.session_uuid}")
    print(f"Memory enabled: {pauls._memory is not None}")
    
    # Run simulation (will be persisted)
    print("\nRunning simulation (data will be persisted)...")
    result = await pauls.run_simulation(rounds=5, delay=0.05)
    
    # Get session history
    print("\n📚 Session History:")
    sessions = pauls.get_session_history()
    print(f"   Total sessions: {len(sessions)}")
    for s in sessions[:3]:
        print(f"   • {s.session_uuid[:8]}... - {s.name} ({s.status})")
    
    # Get agent leaderboard
    print("\n🏆 Agent Leaderboard:")
    leaderboard = pauls.get_accuracy_leaderboard()
    for i, entry in enumerate(leaderboard[:5], 1):
        print(f"   {i}. {entry.get('name', 'Unknown')}: {entry.get('overall_accuracy', 0):.1%}")
    
    await pauls.close()
    return result


async def example_11_custom_agent():
    """Example 11: Create custom agents with specific traits."""
    section("Example 11: Custom Agent Creation")
    
    # Create custom agents
    custom_agents = [
        Agent(
            name="UltraBull",
            persona=PersonaType.TRADER,
            custom_bias=0.8,  # Very bullish
            custom_confidence=0.95,  # Very confident
        ),
        Agent(
            name="UltraBear",
            persona=PersonaType.HEDGIE,
            custom_bias=-0.8,  # Very bearish
            custom_confidence=0.9,
        ),
        Agent(
            name="NeutralNed",
            persona=PersonaType.ANALYST,
            custom_bias=0.0,  # Neutral
            custom_confidence=0.5,  # Uncertain
        ),
    ]
    
    print("Created custom agents:")
    for agent in custom_agents:
        print(f"   • {agent.name}: bias={agent.bias:+.2f}, confidence={agent.base_confidence:.0%}")
    
    pauls = SwimmingPauls(agents=custom_agents)
    
    # Test quick prediction
    print("\n🎯 Quick Prediction Test:")
    market_data = {
        "price_trend": 0.3,
        "volume": 0.7,
        "sentiment": 0.4,
        "volatility": 0.3,
    }
    
    result = pauls.quick_predict(market_data)
    
    print(f"   Consensus: {result['consensus']['direction'].upper()}")
    print(f"   Sentiment: {result['consensus']['sentiment']:+.3f}")
    print(f"   Confidence: {result['consensus']['confidence']:.2f}")
    
    print("\n   Individual Predictions:")
    for p in result['predictions']:
        print(f"     {p['agent'][:8]}: {p['direction']:8} "
              f"(conf: {p['confidence']:.2f}, mag: {p['magnitude']:.2f})")
    
    await pauls.close()
    return result


async def example_12_data_feeds():
    """Example 12: Using external data feeds."""
    section("Example 12: External Data Feeds")
    
    pauls = SwimmingPauls()
    
    print("Fetching external data...")
    print("(Using demo data if API keys not configured)\n")
    
    # Fetch market data
    print("📈 Market Data:")
    try:
        market_data = await pauls.get_market_data(["BTC", "ETH"], asset_type="crypto")
        for price in market_data[:2]:
            change_str = f"{price.change_24h:+.2f}%" if price.change_24h else "N/A"
            print(f"   • {price.symbol}: ${price.price:,.2f} ({change_str})")
    except Exception as e:
        print(f"   (Demo data - API error: {e})")
    
    # Fetch news
    print("\n📰 News Headlines:")
    try:
        news = await pauls.get_news("technology")
        for article in news[:3]:
            print(f"   • {article.title[:50]}... ({article.source})")
    except Exception as e:
        print(f"   (Demo data - API error: {e})")
    
    # Fetch sentiment
    print("\n📊 Social Sentiment:")
    try:
        sentiment = await pauls.get_sentiment("bitcoin", platforms=["reddit"])
        for s in sentiment:
            emoji = "🟢" if s.score > 0.1 else "🔴" if s.score < -0.1 else "⚪"
            print(f"   {emoji} {s.platform}: {s.score:+.2f} ({s.volume} posts)")
            if s.trending:
                print(f"      Trending: {', '.join(s.trending[:3])}")
    except Exception as e:
        print(f"   (Demo data - API error: {e})")
    
    # Run simulation with live data
    print("\n🌐 Running simulation with live data feeds...")
    result = await pauls.run_with_data_feeds(
        news_query="technology",
        market_symbols=["BTC", "ETH"],
        sentiment_topic="crypto",
        rounds=5,
    )
    
    print(f"\nFinal consensus: {result.final_consensus['direction'].upper()}")
    
    await pauls.close()
    return result


async def run_all_examples():
    """Run all examples in sequence."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🏊 SWIMMING PAULS v2.0 - Comprehensive Examples                ║
║                                                                   ║
║   Demonstrating all features of the platform                     ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    examples = [
        ("Basic Simulation", example_1_basic_simulation),
        ("Custom Team", example_2_custom_team),
        ("Film Industry Team", example_3_film_industry_team),
        ("Monte Carlo", example_4_monte_carlo),
        ("Sensitivity Analysis", example_5_sensitivity_analysis),
        ("Scenario Comparison", example_6_scenario_comparison),
        ("Backtesting", example_7_backtesting),
        ("Full Analysis", example_8_full_analysis),
        ("Visualization Export", example_9_visualization_export),
        ("Memory Persistence", example_10_memory_persistence),
        ("Custom Agent", example_11_custom_agent),
        ("Data Feeds", example_12_data_feeds),
    ]
    
    print(f"\n📋 Running {len(examples)} examples...")
    print("=" * 70)
    
    for i, (name, func) in enumerate(examples, 1):
        try:
            await func()
        except KeyboardInterrupt:
            print(f"\n\n⚠️ Interrupted by user at example {i}")
            break
        except Exception as e:
            print(f"\n❌ Error in example {i} ({name}): {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✅ All examples complete!")
    print("=" * 70)


async def run_specific_example(example_num: int):
    """Run a specific example by number."""
    examples = [
        example_1_basic_simulation,
        example_2_custom_team,
        example_3_film_industry_team,
        example_4_monte_carlo,
        example_5_sensitivity_analysis,
        example_6_scenario_comparison,
        example_7_backtesting,
        example_8_full_analysis,
        example_9_visualization_export,
        example_10_memory_persistence,
        example_11_custom_agent,
        example_12_data_feeds,
    ]
    
    if 1 <= example_num <= len(examples):
        await examples[example_num - 1]()
    else:
        print(f"Invalid example number. Choose 1-{len(examples)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Run specific example
        try:
            example_num = int(sys.argv[1])
            asyncio.run(run_specific_example(example_num))
        except ValueError:
            print("Usage: python example.py [example_number]")
            print("   or: python example.py        # Run all examples")
    else:
        # Run all examples
        asyncio.run(run_all_examples())
