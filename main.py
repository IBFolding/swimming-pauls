#!/usr/bin/env python3
"""
SwimmingPauls v2.0 - Command Line Interface

A comprehensive multi-agent prediction and analysis platform.

Usage:
    python main.py                       # Run default simulation
    python main.py --rounds 20           # Run 20 rounds
    python main.py --live --market BTC,ETH  # Use live market data
    python main.py --monte-carlo         # Run Monte Carlo analysis
    python main.py --full-analysis       # Run complete analysis suite
    python main.py --interactive         # Interactive mode
    python main.py --demo                # Run comprehensive demo

Examples:
    # Basic simulation with custom team
    python main.py --analysts 2 --traders 2 --rounds 15

    # Live data simulation
    python main.py --live --news bitcoin --market BTC,ETH --sentiment crypto

    # Full analysis with export
    python main.py --full-analysis --export ./output --html-report

    # Monte Carlo only
    python main.py --monte-carlo --mc-runs 5000

    # Backtest against historical data
    python main.py --backtest data/historical.json
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

from swimming_pauls import (
    SwimmingPauls,
    SwimmingPaulsConfig,
    PersonaType,
    Agent,
    create_agent_team,
    create_film_industry_team,
)


__version__ = "2.0.0"


def print_banner():
    """Print the SwimmingPauls banner."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🏊 SWIMMING PAULS v2.0 - Multi-Agent Simulation Platform       ║
║                                                                   ║
║   Agent-Based Prediction • Live Data • Advanced Analytics        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)


def print_personas():
    """Print available persona types."""
    print("\n📋 AVAILABLE PERSONAS:")
    print("=" * 60)
    
    print("\n🎯 Financial Personas:")
    descriptions = {
        PersonaType.ANALYST: "Data-driven, analytical, conservative confidence",
        PersonaType.TRADER: "Risk-tolerant, aggressive, high adaptability",
        PersonaType.HEDGIE: "Conservative, risk-aware, skeptical of momentum",
        PersonaType.VISIONARY: "Intuitive, forward-looking, pattern-focused",
        PersonaType.SKEPTIC: "Pessimistic, contrarian, analytical",
    }
    
    from agent import PERSONA_PROFILES
    for persona, profile in PERSONA_PROFILES.items():
        if persona in descriptions:
            print(f"\n  🔹 {persona.value.upper()}")
            print(f"     Bias: {profile['bias']:+.2f} | Confidence: {profile['confidence']:.0%}")
            print(f"     Traits: {', '.join(t.value for t in profile['traits'])}")
            print(f"     {descriptions[persona]}")
    
    print("\n🎬 Film Industry Personas:")
    film_descriptions = {
        PersonaType.PRODUCER: "Budget-focused, ROI-driven, analytical",
        PersonaType.DIRECTOR: "Creative, vision-driven, intuitive",
        PersonaType.SCREENWRITER: "Narrative-driven, story-first, intuitive",
        PersonaType.STUDIO_EXEC: "Risk-averse, franchise-focused, conservative",
        PersonaType.INDIE_FILMMAKER: "Innovation-focused, artistic, experimental",
    }
    
    for persona, profile in PERSONA_PROFILES.items():
        if persona in film_descriptions:
            print(f"\n  🔹 {persona.value.upper()}")
            print(f"     Bias: {profile['bias']:+.2f} | Confidence: {profile['confidence']:.0%}")
            print(f"     Traits: {', '.join(t.value for t in profile['traits'])}")
            print(f"     {film_descriptions[persona]}")


def create_agent_team_from_args(args) -> List[Agent]:
    """Create agent team based on CLI arguments."""
    if args.film_team:
        return create_film_industry_team(
            producer=args.producers or 1,
            director=args.directors or 1,
            screenwriter=args.screenwriters or 1,
            studio_exec=args.studio_execs or 1,
            indie_filmmaker=args.indie_filmmakers or 1,
        )
    else:
        return create_agent_team(
            analyst_count=args.analysts or 1,
            trader_count=args.traders or 1,
            hedgie_count=args.hedgies or 1,
            visionary_count=args.visionaries or 1,
            skeptic_count=args.skeptics or 1,
        )


async def run_simulation(args, pauls: SwimmingPauls):
    """Run basic simulation."""
    print("\n📊 RUNNING SIMULATION")
    print("=" * 60)
    
    if args.live:
        print("🌐 Using live data feeds...")
        result = await pauls.run_with_data_feeds(
            news_query=args.news,
            market_symbols=args.market.split(",") if args.market else None,
            sentiment_topic=args.sentiment,
            rounds=args.rounds,
            delay=args.delay,
        )
    else:
        result = await pauls.run_simulation(
            rounds=args.rounds,
            delay=args.delay,
        )
    
    # Print summary
    print(f"\n✅ Simulation complete!")
    print(f"   Duration: {result.end_time - result.start_time:.2f}s")
    print(f"   Rounds: {len(result.rounds)}")
    print(f"   Final Consensus: {result.final_consensus['direction'].upper()}")
    print(f"   Sentiment: {result.final_consensus['sentiment']:+.3f}")
    print(f"   Consistency: {result.final_consensus['consistency']:.1%}")
    
    return result


async def run_monte_carlo(args, pauls: SwimmingPauls):
    """Run Monte Carlo simulation."""
    print("\n🔬 MONTE CARLO SIMULATION")
    print("=" * 60)
    print(f"Running {args.mc_runs} simulations...")
    
    def progress(completed, total):
        pct = completed / total * 100
        print(f"   Progress: {completed}/{total} ({pct:.0f}%)", end="\r")
    
    result = await pauls.monte_carlo(
        runs=args.mc_runs,
        progress_callback=progress if args.verbose else None,
    )
    
    print("\n\n📈 Results:")
    print(f"   Bullish Probability: {result.bullish_probability:.1%}")
    print(f"   Bearish Probability: {result.bearish_probability:.1%}")
    print(f"   Neutral Probability: {result.neutral_probability:.1%}")
    print(f"   Expected Outcome: {result.expected_outcome:+.3f}")
    print(f"   Average Sentiment: {result.avg_sentiment:+.3f}")
    print(f"   Sentiment Std Dev: {result.sentiment_std:.3f}")
    print(f"   95% CI: [{result.confidence_interval_95[0]:+.3f}, {result.confidence_interval_95[1]:+.3f}]")
    print(f"   99% CI: [{result.confidence_interval_99[0]:+.3f}, {result.confidence_interval_99[1]:+.3f}]")
    print(f"   Value at Risk (95%): {result.value_at_risk_95:.3f}")
    print(f"   Value at Risk (99%): {result.value_at_risk_99:.3f}")
    print(f"   Skewness: {result.skewness:.3f}")
    print(f"   Kurtosis: {result.kurtosis:.3f}")
    
    return result


async def run_sensitivity(args, pauls: SwimmingPauls):
    """Run sensitivity analysis."""
    print("\n📊 SENSITIVITY ANALYSIS")
    print("=" * 60)
    print(f"Running with {args.sensitivity_samples} samples per variable...")
    
    variables = args.variables.split(",") if args.variables else None
    results = await pauls.sensitivity_analysis(
        variables=variables,
        samples=args.sensitivity_samples,
    )
    
    print("\n🎯 Variable Impact Rankings:")
    print(f"   {'Rank':<6}{'Variable':<15}{'Impact':<12}{'Sentiment Corr':<15}{'Accuracy Corr'}")
    print("   " + "-" * 65)
    for r in results:
        print(f"   {r.rank:<6}{r.variable_name:<15}{r.impact_score:<12.3f}{r.correlation_with_sentiment:+.3f}         {r.correlation_with_accuracy:+.3f}")
    
    return results


async def run_scenario_comparison(args, pauls: SwimmingPauls):
    """Run scenario comparison."""
    print("\n⚖️  SCENARIO COMPARISON")
    print("=" * 60)
    
    # Define scenarios
    scenario_a = {
        "price_trend": args.scenario_a_price or 0.5,
        "volume": args.scenario_a_volume or 0.8,
        "sentiment": args.scenario_a_sentiment or 0.6,
        "volatility": args.scenario_a_volatility or 0.2,
        "momentum": args.scenario_a_momentum or 0.4,
    }
    scenario_b = {
        "price_trend": args.scenario_b_price or -0.5,
        "volume": args.scenario_b_volume or 0.4,
        "sentiment": args.scenario_b_sentiment or -0.6,
        "volatility": args.scenario_b_volatility or 0.7,
        "momentum": args.scenario_b_momentum or -0.4,
    }
    
    print(f"Comparing: {args.scenario_a_name} vs {args.scenario_b_name}")
    
    result = await pauls.compare_scenarios(
        scenario_a, scenario_b,
        name_a=args.scenario_a_name,
        name_b=args.scenario_b_name,
        runs=args.scenario_runs,
    )
    
    print(f"\n📊 Results:")
    print(f"   {args.scenario_a_name} Win Probability: {result.win_probability_a:.1%}")
    print(f"   {args.scenario_b_name} Win Probability: {result.win_probability_b:.1%}")
    print(f"   Sentiment Difference: {result.sentiment_diff:+.3f}")
    print(f"   Expected Value A: {result.expected_value_a:+.3f}")
    print(f"   Expected Value B: {result.expected_value_b:+.3f}")
    print(f"   Risk Ratio (A/B): {result.risk_ratio:.2f}")
    print(f"   Statistical Significance: p={result.statistical_significance:.3f}")
    print(f"\n   → {result.recommendation}")
    
    return result


async def run_backtest(args, pauls: SwimmingPauls):
    """Run backtest against historical data."""
    print("\n📉 BACKTESTING")
    print("=" * 60)
    
    # Load historical data
    data_path = Path(args.backtest)
    if not data_path.exists():
        print(f"❌ File not found: {args.backtest}")
        return None
    
    with open(data_path) as f:
        historical_data = json.load(f)
    
    print(f"Loaded {len(historical_data)} historical data points")
    
    result = await pauls.backtest(
        historical_data=historical_data,
        outcome_key=args.outcome_key,
    )
    
    print(f"\n📊 Results:")
    print(f"   Total Predictions: {result.total_predictions}")
    print(f"   Correct: {result.correct_predictions}")
    print(f"   Accuracy: {result.accuracy_rate:.1%}")
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
    
    return result


async def run_full_analysis(args, pauls: SwimmingPauls):
    """Run complete analysis suite."""
    print("\n🔬 FULL ANALYSIS SUITE")
    print("=" * 60)
    
    results = await pauls.run_full_analysis()
    
    print("\n📊 Monte Carlo Results:")
    mc = results["monte_carlo"]
    print(f"   Bullish: {mc['probabilities']['bullish']:.1%}")
    print(f"   Bearish: {mc['probabilities']['bearish']:.1%}")
    print(f"   Expected: {mc['expected_outcome']:+.3f}")
    
    print("\n📈 Sensitivity Analysis:")
    for r in results["sensitivity_analysis"][:5]:
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
    
    return results


async def run_interactive(pauls: SwimmingPauls):
    """Run interactive mode."""
    print_banner()
    print("\n🎮 INTERACTIVE MODE")
    print("=" * 60)
    
    print("\nAgents loaded:")
    for agent in pauls.list_agents():
        print(f"  • {agent['name']} ({agent['persona']})")
    
    print("\nCommands:")
    print("  predict <price> <volume> <sentiment> <volatility>")
    print("  live <news_query> <market_symbols> <sentiment_topic>")
    print("  simulate <rounds>")
    print("  status")
    print("  quit")
    
    while True:
        print("\n" + "-" * 60)
        cmd = input("🎯 pauls> ").strip()
        
        if cmd == "quit":
            break
        elif cmd == "status":
            status = pauls.get_status()
            print(f"\nAgents: {status['agents']['count']}")
            print(f"Session: {status['session']['uuid'][:8]}...")
            print(f"Has result: {status['session']['has_result']}")
        elif cmd.startswith("predict"):
            parts = cmd.split()
            if len(parts) >= 2:
                try:
                    market_data = {
                        "price_trend": float(parts[1]),
                        "volume": float(parts[2]) if len(parts) > 2 else 0.5,
                        "sentiment": float(parts[3]) if len(parts) > 3 else 0.0,
                        "volatility": float(parts[4]) if len(parts) > 4 else 0.3,
                    }
                    result = pauls.quick_predict(market_data)
                    print(f"\nConsensus: {result['consensus']['direction'].upper()}")
                    print(f"Sentiment: {result['consensus']['sentiment']:+.3f}")
                    print(f"Confidence: {result['consensus']['confidence']:.2f}")
                    print("\nAgent Predictions:")
                    for p in result['predictions'][:5]:
                        print(f"  {p['agent'][:8]}: {p['direction']:8} (conf: {p['confidence']:.2f})")
                except ValueError:
                    print("❌ Invalid input. Use: predict <price> <volume> <sentiment> <volatility>")
            else:
                print("Usage: predict <price> <volume> <sentiment> <volatility>")
        elif cmd.startswith("simulate"):
            parts = cmd.split()
            rounds = int(parts[1]) if len(parts) > 1 else 10
            print(f"\nRunning {rounds} rounds...")
            await pauls.run_simulation(rounds=rounds, delay=0.1)
            pauls.print_terminal_charts()
        elif cmd.startswith("live"):
            parts = cmd.split()
            news = parts[1] if len(parts) > 1 else "technology"
            markets = parts[2].split(",") if len(parts) > 2 else ["BTC"]
            sentiment = parts[3] if len(parts) > 3 else "crypto"
            print(f"\nFetching live data: news='{news}', markets={markets}, sentiment='{sentiment}'...")
            result = await pauls.run_with_data_feeds(
                news_query=news,
                market_symbols=markets,
                sentiment_topic=sentiment,
                rounds=5,
            )
            print(f"Final consensus: {result.final_consensus['direction'].upper()}")
        else:
            print(f"Unknown command: {cmd}")
    
    print("\n👋 Goodbye!")


async def run_demo():
    """Run comprehensive demo."""
    from swimming_pauls import demo
    await demo()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="SwimmingPauls v2.0 - Multi-Agent Simulation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic simulation
  python main.py --rounds 20

  # Live data simulation
  python main.py --live --market BTC,ETH --sentiment crypto

  # Monte Carlo analysis
  python main.py --monte-carlo --mc-runs 5000

  # Full analysis suite
  python main.py --full-analysis --export ./output

  # Custom team composition
  python main.py --analysts 2 --traders 3 --skeptics 1

  # Film industry team
  python main.py --film-team --producers 2 --directors 1

  # Interactive mode
  python main.py --interactive
        """
    )
    
    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--demo", action="store_true", help="Run comprehensive demo")
    mode_group.add_argument("--monte-carlo", action="store_true", help="Run Monte Carlo simulation")
    mode_group.add_argument("--sensitivity", action="store_true", help="Run sensitivity analysis")
    mode_group.add_argument("--compare", action="store_true", help="Run scenario comparison")
    mode_group.add_argument("--backtest", type=str, metavar="FILE", help="Backtest against historical data")
    mode_group.add_argument("--full-analysis", action="store_true", help="Run complete analysis suite")
    mode_group.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    mode_group.add_argument("--list-personas", action="store_true", help="List available personas")
    
    # Simulation settings
    sim_group = parser.add_argument_group("Simulation Settings")
    sim_group.add_argument("--rounds", type=int, default=10, help="Number of rounds (default: 10)")
    sim_group.add_argument("--delay", type=float, default=0.1, help="Delay between rounds (default: 0.1)")
    
    # Team composition
    team_group = parser.add_argument_group("Team Composition")
    team_group.add_argument("--analysts", type=int, default=1, help="Number of analyst agents")
    team_group.add_argument("--traders", type=int, default=1, help="Number of trader agents")
    team_group.add_argument("--hedgies", type=int, default=1, help="Number of hedge agents")
    team_group.add_argument("--visionaries", type=int, default=1, help="Number of visionary agents")
    team_group.add_argument("--skeptics", type=int, default=1, help="Number of skeptic agents")
    
    # Film industry team
    film_group = parser.add_argument_group("Film Industry Team")
    film_group.add_argument("--film-team", action="store_true", help="Use film industry personas")
    film_group.add_argument("--producers", type=int, default=1, help="Number of producer agents")
    film_group.add_argument("--directors", type=int, default=1, help="Number of director agents")
    film_group.add_argument("--screenwriters", type=int, default=1, help="Number of screenwriter agents")
    film_group.add_argument("--studio-execs", type=int, default=1, help="Number of studio exec agents")
    film_group.add_argument("--indie-filmmakers", type=int, default=1, help="Number of indie filmmaker agents")
    
    # Live data settings
    data_group = parser.add_argument_group("Live Data Feeds")
    data_group.add_argument("--live", action="store_true", help="Use live data feeds")
    data_group.add_argument("--news", type=str, help="News query (e.g., 'bitcoin')")
    data_group.add_argument("--market", type=str, help="Market symbols (e.g., 'BTC,ETH')")
    data_group.add_argument("--sentiment", type=str, help="Sentiment topic (e.g., 'crypto')")
    
    # Monte Carlo settings
    mc_group = parser.add_argument_group("Monte Carlo Settings")
    mc_group.add_argument("--mc-runs", type=int, default=1000, help="Number of Monte Carlo runs")
    
    # Sensitivity settings
    sens_group = parser.add_argument_group("Sensitivity Settings")
    sens_group.add_argument("--sensitivity-samples", type=int, default=500, help="Samples per variable")
    sens_group.add_argument("--variables", type=str, help="Variables to analyze (comma-separated)")
    
    # Scenario comparison settings
    comp_group = parser.add_argument_group("Scenario Comparison Settings")
    comp_group.add_argument("--scenario-runs", type=int, default=1000, help="Runs per scenario")
    comp_group.add_argument("--scenario-a-name", type=str, default="Scenario A", help="Name for scenario A")
    comp_group.add_argument("--scenario-b-name", type=str, default="Scenario B", help="Name for scenario B")
    comp_group.add_argument("--scenario-a-price", type=float, help="Scenario A price trend")
    comp_group.add_argument("--scenario-a-volume", type=float, help="Scenario A volume")
    comp_group.add_argument("--scenario-a-sentiment", type=float, help="Scenario A sentiment")
    comp_group.add_argument("--scenario-a-volatility", type=float, help="Scenario A volatility")
    comp_group.add_argument("--scenario-a-momentum", type=float, help="Scenario A momentum")
    comp_group.add_argument("--scenario-b-price", type=float, help="Scenario B price trend")
    comp_group.add_argument("--scenario-b-volume", type=float, help="Scenario B volume")
    comp_group.add_argument("--scenario-b-sentiment", type=float, help="Scenario B sentiment")
    comp_group.add_argument("--scenario-b-volatility", type=float, help="Scenario B volatility")
    comp_group.add_argument("--scenario-b-momentum", type=float, help="Scenario B momentum")
    
    # Backtest settings
    bt_group = parser.add_argument_group("Backtest Settings")
    bt_group.add_argument("--outcome-key", type=str, default="actual_outcome", help="Key for actual outcome")
    
    # Output settings
    out_group = parser.add_argument_group("Output Settings")
    out_group.add_argument("--export", type=str, help="Export directory for all outputs")
    out_group.add_argument("--html-report", action="store_true", help="Generate HTML report")
    out_group.add_argument("--no-viz", action="store_true", help="Skip visualizations")
    out_group.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Config settings
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument("--db-path", type=str, help="Database path for persistence")
    config_group.add_argument("--no-memory", action="store_true", help="Disable persistence")
    
    args = parser.parse_args()
    
    # Handle simple commands
    if args.list_personas:
        print_banner()
        print_personas()
        return
    
    if args.demo:
        await run_demo()
        return
    
    # Create configuration
    config = SwimmingPaulsConfig()
    if args.db_path:
        config.db_path = args.db_path
    if args.no_memory:
        config.enable_persistence = False
    
    # Initialize SwimmingPauls
    print_banner()
    
    if not args.interactive:
        agents = create_agent_team_from_args(args)
        pauls = SwimmingPauls(agents=agents, config=config)
        
        print(f"\n🎭 Loaded {len(pauls.agents)} agents")
        if args.verbose:
            for agent in pauls.agents:
                print(f"   • {agent.name} ({agent.persona.value})")
    else:
        pauls = SwimmingPauls(config=config)
    
    try:
        # Run based on mode
        if args.interactive:
            await run_interactive(pauls)
        elif args.monte_carlo:
            await run_monte_carlo(args, pauls)
        elif args.sensitivity:
            await run_sensitivity(args, pauls)
        elif args.compare:
            await run_scenario_comparison(args, pauls)
        elif args.backtest:
            await run_backtest(args, pauls)
        elif args.full_analysis:
            result = await run_full_analysis(args, pauls)
            if not args.no_viz:
                pauls.print_terminal_charts()
        else:
            # Default: run simulation
            result = await run_simulation(args, pauls)
            
            # Visualize unless disabled
            if not args.no_viz:
                if args.html_report:
                    output_dir = Path(args.export or "./output")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    pauls.generate_html_report(str(output_dir / "report.html"))
                
                pauls.print_terminal_charts()
                
                if args.export:
                    pauls.visualize(output_dir=args.export)
        
        # Export if requested
        if args.export and not args.no_viz and not args.monte_carlo and not args.sensitivity:
            pauls.visualize(output_dir=args.export)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    finally:
        await pauls.close()


if __name__ == "__main__":
    asyncio.run(main())
