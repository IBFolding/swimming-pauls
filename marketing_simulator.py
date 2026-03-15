"""
Marketing Campaign Testing Module for Swimming Pauls
Simulates A/B testing and market response to campaigns
"""
import random
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class CustomerSegment(Enum):
    EARLY_ADOPTER = "early_adopter"
    MAINSTREAM = "mainstream"
    LATE_ADOPTER = "late_adopter"
    PRICE_SENSITIVE = "price_sensitive"
    LUXURY = "luxury"


@dataclass
class CampaignVariant:
    """A marketing campaign variant for testing."""
    name: str
    headline: str
    messaging: str
    visual_style: str
    price_point: float
    channel_mix: Dict[str, float]  # Channel -> budget %


@dataclass
class CustomerResponse:
    """How a customer responds to a campaign."""
    segment: CustomerSegment
    awareness: bool
    interest: bool
    consideration: bool
    purchase: bool
    advocacy: bool  # Would they recommend
    feedback: str


class MarketingSimulator:
    """
    Simulates marketing campaigns and predicts market response.
    Tests multiple variants to find optimal strategy.
    """
    
    def __init__(self):
        self.segments = list(CustomerSegment)
        self.channels = ["Social Media", "TV", "Influencers", "Search", "Email", "OOH"]
        
        # Segment characteristics
        self.segment_traits = {
            CustomerSegment.EARLY_ADOPTER: {
                "innovation_appeal": 0.9,
                "price_sensitivity": 0.3,
                "social_proof_need": 0.4,
                "influenceability": 0.7
            },
            CustomerSegment.MAINSTREAM: {
                "innovation_appeal": 0.5,
                "price_sensitivity": 0.6,
                "social_proof_need": 0.8,
                "influenceability": 0.6
            },
            CustomerSegment.LATE_ADOPTER: {
                "innovation_appeal": 0.2,
                "price_sensitivity": 0.8,
                "social_proof_need": 0.9,
                "influenceability": 0.4
            },
            CustomerSegment.PRICE_SENSITIVE: {
                "innovation_appeal": 0.3,
                "price_sensitivity": 0.95,
                "social_proof_need": 0.7,
                "influenceability": 0.5
            },
            CustomerSegment.LUXURY: {
                "innovation_appeal": 0.7,
                "price_sensitivity": 0.1,
                "social_proof_need": 0.6,
                "influenceability": 0.5
            }
        }
    
    def test_campaign(
        self,
        product_name: str,
        variants: List[CampaignVariant],
        market_size: int = 100000,
        simulation_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Test multiple campaign variants against simulated market.
        
        Args:
            product_name: Name of product/service
            variants: List of campaign variants to test
            market_size: Size of target market
            simulation_weeks: How many weeks to simulate
            
        Returns:
            Comparison results and recommendations
        """
        results = []
        
        for variant in variants:
            result = self._simulate_variant(
                variant, product_name, market_size, simulation_weeks
            )
            results.append(result)
        
        # Find winner
        winner = max(results, key=lambda r: r["total_revenue"])
        
        return {
            "product_name": product_name,
            "market_size": market_size,
            "simulation_weeks": simulation_weeks,
            "variants_tested": len(variants),
            "results": results,
            "winner": winner,
            "recommendations": self._generate_marketing_recommendations(results, winner),
            "insights": self._extract_marketing_insights(results)
        }
    
    def _simulate_variant(
        self,
        variant: CampaignVariant,
        product_name: str,
        market_size: int,
        weeks: int
    ) -> Dict[str, Any]:
        """Simulate a single campaign variant."""
        
        weekly_data = []
        total_customers = 0
        total_revenue = 0
        segment_breakdown = {seg: 0 for seg in self.segments}
        
        for week in range(weeks):
            # Calculate reach for this week (marketing effect)
            reach = self._calculate_weekly_reach(variant, week, market_size)
            
            # Generate customer responses
            responses = []
            week_customers = 0
            week_revenue = 0
            
            for _ in range(int(reach)):
                response = self._generate_customer_response(variant, product_name)
                responses.append(response)
                
                if response.purchase:
                    week_customers += 1
                    week_revenue += variant.price_point
                    segment_breakdown[response.segment] += 1
            
            total_customers += week_customers
            total_revenue += week_revenue
            
            weekly_data.append({
                "week": week + 1,
                "reach": reach,
                "new_customers": week_customers,
                "revenue": week_revenue,
                "awareness_rate": sum(1 for r in responses if r.awareness) / len(responses) if responses else 0,
                "conversion_rate": sum(1 for r in responses if r.purchase) / len(responses) if responses else 0
            })
        
        return {
            "variant_name": variant.name,
            "headline": variant.headline,
            "total_customers": total_customers,
            "total_revenue": total_revenue,
            "avg_customer_value": total_revenue / total_customers if total_customers > 0 else 0,
            "market_penetration": (total_customers / market_size) * 100,
            "segment_breakdown": segment_breakdown,
            "weekly_data": weekly_data,
            "channel_performance": self._analyze_channels(variant, weekly_data)
        }
    
    def _calculate_weekly_reach(self, variant: CampaignVariant, week: int, market_size: int) -> int:
        """Calculate how many people the campaign reaches each week."""
        # Marketing spend effect (diminishing returns over time)
        base_reach = market_size * 0.02  # 2% weekly reach
        
        # Channel effectiveness
        channel_multiplier = sum(variant.channel_mix.values()) / len(variant.channel_mix)
        
        # Week effect (highest at launch, then stabilizes)
        if week == 0:
            week_multiplier = 2.0  # Launch week boost
        elif week < 4:
            week_multiplier = 1.5  # Early campaign
        else:
            week_multiplier = 1.0  # Steady state
        
        reach = int(base_reach * channel_multiplier * week_multiplier)
        return min(reach, market_size - int(base_reach * week))  # Don't exceed market
    
    def _generate_customer_response(self, variant: CampaignVariant, product_name: str) -> CustomerResponse:
        """Generate how a customer responds to the campaign."""
        # Select segment
        segment = random.choice(self.segments)
        traits = self.segment_traits[segment]
        
        # Awareness (did they see the campaign?)
        awareness = random.random() < 0.7  # 70% baseline awareness
        
        if not awareness:
            return CustomerResponse(
                segment=segment,
                awareness=False,
                interest=False,
                consideration=False,
                purchase=False,
                advocacy=False,
                feedback="Never saw the campaign"
            )
        
        # Interest based on messaging appeal
        messaging_appeal = self._calculate_messaging_appeal(variant, segment, traits)
        interest = random.random() < messaging_appeal
        
        if not interest:
            return CustomerResponse(
                segment=segment,
                awareness=True,
                interest=False,
                consideration=False,
                purchase=False,
                advocacy=False,
                feedback=self._generate_feedback(variant, segment, "not_interested")
            )
        
        # Consideration (price check, comparison)
        price_acceptance = 1 - (traits["price_sensitivity"] * (variant.price_point / 100))
        consideration = random.random() < price_acceptance
        
        if not consideration:
            return CustomerResponse(
                segment=segment,
                awareness=True,
                interest=True,
                consideration=False,
                purchase=False,
                advocacy=False,
                feedback=self._generate_feedback(variant, segment, "price_too_high")
            )
        
        # Purchase decision
        purchase_probability = self._calculate_purchase_probability(variant, traits)
        purchase = random.random() < purchase_probability
        
        # Advocacy (would they recommend?)
        advocacy = purchase and random.random() < (traits["influenceability"] * 0.6)
        
        return CustomerResponse(
            segment=segment,
            awareness=True,
            interest=True,
            consideration=True,
            purchase=purchase,
            advocacy=advocacy,
            feedback=self._generate_feedback(variant, segment, "purchased" if purchase else "considered")
        )
    
    def _calculate_messaging_appeal(self, variant: CampaignVariant, segment: CustomerSegment, traits: Dict) -> float:
        """Calculate how appealing the messaging is to a segment."""
        base_appeal = 0.5
        
        # Innovation messaging appeals to early adopters
        if "innovation" in variant.messaging.lower() or "new" in variant.messaging.lower():
            base_appeal += traits["innovation_appeal"] * 0.3
        
        # Price messaging appeals to price-sensitive
        if "save" in variant.messaging.lower() or "deal" in variant.messaging.lower():
            base_appeal += (1 - traits["price_sensitivity"]) * 0.2
        
        # Social proof appeals to mainstream/late adopters
        if "best" in variant.messaging.lower() or "popular" in variant.messaging.lower():
            base_appeal += traits["social_proof_need"] * 0.2
        
        return min(0.9, max(0.1, base_appeal))
    
    def _calculate_purchase_probability(self, variant: CampaignVariant, traits: Dict) -> float:
        """Calculate probability of purchase."""
        base_prob = 0.3
        
        # Price sensitivity adjustment
        price_factor = 1 - (traits["price_sensitivity"] * 0.5)
        
        # Influenceability
        influence_factor = traits["influenceability"] * 0.2
        
        return min(0.8, base_prob * price_factor + influence_factor)
    
    def _generate_feedback(self, variant: CampaignVariant, segment: CustomerSegment, stage: str) -> str:
        """Generate realistic customer feedback."""
        feedback = {
            "not_interested": [
                "Doesn't speak to me",
                "Not relevant to my needs",
                "Messaging is confusing"
            ],
            "price_too_high": [
                "Too expensive for what it offers",
                "Waiting for a sale",
                "Found cheaper alternative"
            ],
            "considered": [
                "Still thinking about it",
                "Need to research more",
                "Will decide next month"
            ],
            "purchased": [
                "Exactly what I needed",
                "Great value for money",
                "Love the features"
            ]
        }
        
        return random.choice(feedback.get(stage, ["No comment"]))
    
    def _analyze_channels(self, variant: CampaignVariant, weekly_data: List[Dict]) -> Dict[str, Any]:
        """Analyze which channels performed best."""
        performance = {}
        for channel, budget_pct in variant.channel_mix.items():
            # Simulate ROI based on channel effectiveness
            roi_multipliers = {
                "Social Media": 1.3,
                "TV": 1.0,
                "Influencers": 1.4,
                "Search": 1.5,
                "Email": 2.0,
                "OOH": 0.8
            }
            
            roi = roi_multipliers.get(channel, 1.0) * budget_pct
            performance[channel] = {
                "budget_pct": budget_pct,
                "estimated_roi": round(roi, 2)
            }
        
        return performance
    
    def _generate_marketing_recommendations(self, results: List[Dict], winner: Dict) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Winner insights
        recommendations.append(f"🏆 Winning variant: '{winner['variant_name']}' with ${winner['total_revenue']:,.0f} revenue")
        
        # Segment insights
        top_segment = max(winner['segment_breakdown'], key=winner['segment_breakdown'].get)
        recommendations.append(f"🎯 Focus on {top_segment.value.replace('_', ' ').title()} segment - highest conversion")
        
        # Channel insights
        best_channel = max(winner['channel_performance'], key=lambda k: winner['channel_performance'][k]['estimated_roi'])
        recommendations.append(f"📢 Increase spend on {best_channel} - highest ROI channel")
        
        # Optimization
        worst_performer = min(results, key=lambda r: r['total_revenue'])
        if worst_performer['variant_name'] != winner['variant_name']:
            recommendations.append(f"⚠️  Deprioritize '{worst_performer['variant_name']}' - underperformed by {((winner['total_revenue'] - worst_performer['total_revenue']) / worst_performer['total_revenue'] * 100):.0f}%")
        
        return recommendations
    
    def _extract_marketing_insights(self, results: List[Dict]) -> List[str]:
        """Extract key insights from the tests."""
        insights = []
        
        # Revenue comparison
        revenues = [r['total_revenue'] for r in results]
        avg_revenue = sum(revenues) / len(revenues)
        insights.append(f"💰 Average campaign revenue: ${avg_revenue:,.0f}")
        
        # Market penetration
        penetrations = [r['market_penetration'] for r in results]
        avg_penetration = sum(penetrations) / len(penetrations)
        insights.append(f"📊 Average market penetration: {avg_penetration:.1f}%")
        
        # Best performing headline style
        winning_headlines = [r['headline'] for r in results]
        insights.append(f"📝 Winning messaging themes: {len(set(winning_headlines))} distinct approaches tested")
        
        return insights


# Convenience function
def test_marketing_campaign(
    product_name: str,
    variants: List[Dict[str, Any]],
    market_size: int = 100000,
    weeks: int = 12
) -> Dict[str, Any]:
    """
    Quick function to test marketing campaigns.
    
    Example:
        result = test_marketing_campaign(
            "Smart Home Device",
            [
                {
                    "name": "Innovation Focus",
                    "headline": "The Future of Home",
                    "messaging": "Revolutionary technology",
                    "price": 299
                },
                {
                    "name": "Value Focus", 
                    "headline": "Save on Energy Bills",
                    "messaging": "Cut costs by 30%",
                    "price": 199
                }
            ]
        )
    """
    simulator = MarketingSimulator()
    
    campaign_variants = [
        CampaignVariant(
            name=v["name"],
            headline=v["headline"],
            messaging=v.get("messaging", ""),
            visual_style=v.get("visual_style", "modern"),
            price_point=v["price"],
            channel_mix=v.get("channels", {"Social Media": 0.4, "Search": 0.3, "TV": 0.3})
        )
        for v in variants
    ]
    
    return simulator.test_campaign(product_name, campaign_variants, market_size, weeks)


if __name__ == "__main__":
    # Test example
    result = test_marketing_campaign(
        "Eco-Friendly Water Bottle",
        [
            {
                "name": "Premium",
                "headline": "The Last Bottle You'll Ever Need",
                "messaging": "Premium quality, lifetime warranty",
                "price": 45
            },
            {
                "name": "Eco",
                "headline": "Save the Planet, One Sip at a Time",
                "messaging": "100% recycled materials, carbon neutral",
                "price": 35
            }
        ],
        market_size=50000,
        weeks=8
    )
    
    print("\nMarketing Campaign Test Results")
    print("=" * 50)
    print(f"Winner: {result['winner']['variant_name']}")
    print(f"Revenue: ${result['winner']['total_revenue']:,.0f}")
    print(f"Customers: {result['winner']['total_customers']:,}")
