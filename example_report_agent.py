"""
ReportAgent Usage Example
Demonstrates how to use the ReportAgent system for Swimming Pauls.
"""

import asyncio
from swimming_pauls import SwimmingPauls, ReportAgent


async def basic_example():
    """Basic example: Run simulation and generate report."""
    print("=" * 60)
    print("🏊 SWIMMING PAULS REPORT AGENT - Basic Example")
    print("=" * 60)
    
    # Initialize Swimming Pauls
    pauls = SwimmingPauls()
    print(f"\n✅ Initialized with {len(pauls.agents)} agents")
    
    # Run simulation
    print("\n📊 Running simulation...")
    result = await pauls.run_simulation(rounds=10, delay=0.1)
    print(f"✅ Simulation complete! Final consensus: {result.final_consensus['direction'].upper()}")
    
    # Create ReportAgent
    report_agent = ReportAgent()
    print("\n📄 Generating report...")
    
    # Generate and save report
    report, paths = await report_agent.generate_and_save(
        result=result,
        agents=pauls.agents,
        topic="BTC price prediction",
        title="Bitcoin Market Analysis Report"
    )
    
    print(f"\n✅ Report generated!")
    print(f"   Report ID: {report.metadata.report_id}")
    print(f"   Consensus: {report.consensus.direction.upper()} ({report.consensus.strength})")
    print(f"   Confidence: {report.consensus.confidence:.1%}")
    
    # Print insights
    print("\n💡 Key Insights:")
    for i, insight in enumerate(report.insights[:3], 1):
        print(f"   {i}. {insight}")
    
    # Show file paths
    print(f"\n📁 Report saved to:")
    print(f"   HTML: {paths['html']}")
    print(f"   Markdown: {paths['markdown']}")
    print(f"   JSON: {paths['json']}")
    
    # Clean up
    await pauls.close()
    return report


async def skill_enriched_example():
    """Example with skill integration for enriched data."""
    print("\n" + "=" * 60)
    print("🔧 SKILL-ENRICHED REPORT EXAMPLE")
    print("=" * 60)
    
    # Initialize
    pauls = SwimmingPauls()
    report_agent = ReportAgent()
    
    # Run simulation
    result = await pauls.run_simulation(rounds=5, delay=0.1)
    
    # Generate report with topic for skill enrichment
    report, paths = await report_agent.generate_and_save(
        result=result,
        agents=pauls.agents,
        topic="crypto market analysis",
        title="Crypto Market Intelligence Report"
    )
    
    print(f"\n✅ Skill-enriched report generated!")
    print(f"   Report ID: {report.metadata.report_id}")
    print(f"   Skills integrated: {len(report.skill_data)}")
    
    # Show skill data
    if report.skill_data:
        print("\n🔧 Integrated Skills:")
        for sd in report.skill_data:
            print(f"   • {sd.skill_name}: {sd.query}")
    
    await pauls.close()
    return report


async def api_server_example():
    """Example of starting the API server."""
    print("\n" + "=" * 60)
    print("🌐 API SERVER EXAMPLE")
    print("=" * 60)
    
    from swimming_pauls.report_api import start_report_api
    
    # Start API server
    server = start_report_api(port=8080)
    
    print("\n📊 API Server started!")
    print("   URL: http://localhost:8080")
    print("\n   Available endpoints:")
    print("   • GET  /api/health          - Health check")
    print("   • GET  /api/reports         - List all reports")
    print("   • GET  /api/reports/{id}    - Get report by ID")
    print("   • POST /api/simulate        - Run simulation and generate report")
    print("   • GET  /api/skills          - List available skills")
    
    print("\n   Press Ctrl+C to stop the server")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("\n✅ Server stopped")


def quick_report_example():
    """Example using quick_report convenience function."""
    print("\n" + "=" * 60)
    print("⚡ QUICK REPORT EXAMPLE")
    print("=" * 60)
    
    async def run():
        # Create agents and run simulation
        pauls = SwimmingPauls()
        result = await pauls.run_simulation(rounds=5, delay=0.1)
        
        # Quick report generation
        from swimming_pauls import quick_report
        report, paths = await quick_report(result, pauls.agents, topic="Quick Analysis")
        
        print(f"\n✅ Quick report generated!")
        print(f"   ID: {report.metadata.report_id}")
        print(f"   Consensus: {report.consensus.direction.upper()}")
        
        await pauls.close()
    
    asyncio.run(run())


def markdown_export_example():
    """Example of exporting to Markdown."""
    print("\n" + "=" * 60)
    print("📝 MARKDOWN EXPORT EXAMPLE")
    print("=" * 60)
    
    async def run():
        pauls = SwimmingPauls()
        result = await pauls.run_simulation(rounds=3, delay=0.1)
        
        report_agent = ReportAgent()
        report = await report_agent.generate_report(result, pauls.agents)
        
        # Export to Markdown without saving
        from swimming_pauls import format_report_markdown
        markdown = format_report_markdown(report)
        
        print("\n--- MARKDOWN PREVIEW ---")
        print(markdown[:1000])
        print("...")
        print("--- END PREVIEW ---")
        
        await pauls.close()
    
    asyncio.run(run())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "basic":
            asyncio.run(basic_example())
        elif example == "skills":
            asyncio.run(skill_enriched_example())
        elif example == "api":
            asyncio.run(api_server_example())
        elif example == "quick":
            quick_report_example()
        elif example == "markdown":
            markdown_export_example()
        else:
            print(f"Unknown example: {example}")
            print("Available: basic, skills, api, quick, markdown")
    else:
        # Run all examples
        print("\n" + "=" * 60)
        print("🏊 SWIMMING PAULS REPORT AGENT - EXAMPLES")
        print("=" * 60)
        print("\nRun specific examples with: python example_report_agent.py <example>")
        print("Examples: basic, skills, api, quick, markdown")
        print("\nRunning basic example...\n")
        
        asyncio.run(basic_example())