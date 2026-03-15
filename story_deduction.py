"""
Story & Fiction Deduction Module for Swimming Pauls
Analyzes narratives, plots, and story structures
"""
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class StoryElement(Enum):
    CHARACTER = "character"
    PLOT_POINT = "plot_point"
    THEME = "theme"
    SETTING = "setting"
    CONFLICT = "conflict"
    TWIST = "twist"


@dataclass
class NarrativeNode:
    """A node in the story graph."""
    id: str
    element_type: StoryElement
    description: str
    connections: List[str]  # IDs of connected nodes
    likelihood: float  # 0-1 probability this happens
    impact: float  # 0-1 story impact if it happens


class StoryDeductionEngine:
    """
    Analyzes story narratives, predicts plot developments,
    and identifies possible twists or outcomes.
    """
    
    def __init__(self):
        self.story_patterns = {
            "hero_journey": ["call", "refusal", "mentor", "trials", "crisis", "victory", "return"],
            "mystery": ["crime", "clues", "red_herrings", "reveal", "confrontation"],
            "romance": ["meet", "obstacle", "separation", "reunion", "commitment"],
            "tragedy": ["rise", "flaw", "downfall", "catharsis"]
        }
    
    def analyze_story(
        self,
        premise: str,
        characters: List[Dict[str, Any]],
        current_plot: str,
        genre: str = "mystery"
    ) -> Dict[str, Any]:
        """
        Analyze a story and predict possible outcomes.
        
        Args:
            premise: Story premise/setup
            characters: List of characters with traits
            current_plot: Where the story currently is
            genre: Story genre
            
        Returns:
            Plot predictions, character arcs, possible endings
        """
        # Build narrative graph
        narrative_graph = self._build_narrative_graph(premise, characters, genre)
        
        # Predict plot developments
        plot_predictions = self._predict_plot_developments(
            narrative_graph, current_plot, genre
        )
        
        # Analyze character arcs
        character_arcs = self._analyze_character_arcs(characters, plot_predictions)
        
        # Generate possible endings
        endings = self._generate_possible_endings(
            narrative_graph, plot_predictions, genre
        )
        
        # Identify likely twists
        twists = self._identify_potential_twists(narrative_graph, plot_predictions)
        
        return {
            "premise": premise,
            "genre": genre,
            "narrative_graph": narrative_graph,
            "plot_predictions": plot_predictions,
            "character_arcs": character_arcs,
            "possible_endings": endings,
            "potential_twists": twists,
            "themes": self._extract_themes(narrative_graph),
            "recommendations": self._generate_story_recommendations(
                plot_predictions, character_arcs, endings
            )
        }
    
    def _build_narrative_graph(
        self,
        premise: str,
        characters: List[Dict],
        genre: str
    ) -> List[NarrativeNode]:
        """Build a graph of narrative possibilities."""
        nodes = []
        
        # Add premise as root
        nodes.append(NarrativeNode(
            id="premise",
            element_type=StoryElement.PLOT_POINT,
            description=premise,
            connections=[],
            likelihood=1.0,
            impact=1.0
        ))
        
        # Add character nodes
        for i, char in enumerate(characters):
            node = NarrativeNode(
                id=f"char_{i}",
                element_type=StoryElement.CHARACTER,
                description=f"{char.get('name', 'Unknown')}: {char.get('trait', 'Complex')}",
                connections=["premise"],
                likelihood=1.0,
                impact=char.get('importance', 0.5)
            )
            nodes.append(node)
        
        # Add genre-specific plot points
        pattern = self.story_patterns.get(genre, self.story_patterns["mystery"])
        
        for i, stage in enumerate(pattern):
            node = NarrativeNode(
                id=f"plot_{stage}",
                element_type=StoryElement.PLOT_POINT,
                description=stage.replace("_", " ").title(),
                connections=["premise"] if i == 0 else [f"plot_{pattern[i-1]}"],
                likelihood=0.7 + (random.random() * 0.2),
                impact=0.5 + (random.random() * 0.5)
            )
            nodes.append(node)
        
        # Add possible conflicts
        conflicts = [
            "internal_doubt", "betrayal", "external_threat", 
            "moral_dilemma", "time_pressure"
        ]
        
        for i, conflict in enumerate(conflicts):
            node = NarrativeNode(
                id=f"conflict_{i}",
                element_type=StoryElement.CONFLICT,
                description=conflict.replace("_", " ").title(),
                connections=[f"plot_{random.choice(pattern)}"],
                likelihood=0.4 + (random.random() * 0.4),
                impact=0.6 + (random.random() * 0.4)
            )
            nodes.append(node)
        
        return nodes
    
    def _predict_plot_developments(
        self,
        narrative_graph: List[NarrativeNode],
        current_plot: str,
        genre: str
    ) -> List[Dict[str, Any]]:
        """Predict what happens next in the story."""
        predictions = []
        
        # Find current position in graph
        current_nodes = [n for n in narrative_graph if current_plot.lower() in n.description.lower()]
        
        if not current_nodes:
            current_nodes = [narrative_graph[0]]  # Default to premise
        
        # Predict next 3 plot points
        for i in range(3):
            likelihood = 0.8 - (i * 0.15)  # Decreasing certainty
            
            prediction = {
                "sequence": i + 1,
                "event": self._generate_plot_event(genre, i),
                "likelihood": round(likelihood, 2),
                "triggers": self._generate_triggers(narrative_graph),
                "consequences": self._generate_consequences(genre)
            }
            predictions.append(prediction)
        
        return predictions
    
    def _generate_plot_event(self, genre: str, step: int) -> str:
        """Generate a specific plot event based on genre."""
        events = {
            "mystery": [
                "New evidence reveals unexpected suspect",
                "Key witness comes forward with crucial testimony",
                "Detective discovers pattern linking cases",
                "Red herring leads investigation astray",
                "Hidden connection between victims exposed"
            ],
            "romance": [
                "Misunderstanding creates temporary rift",
                "Grand gesture wins back trust",
                "External pressure tests relationship",
                "Secret past threatens future together",
                "Mutual realization of true feelings"
            ],
            "thriller": [
                "Ticking clock raises stakes",
                "Betrayal by trusted ally",
                "Hero's plan backfires spectacularly",
                "Villain reveals true motive",
                "Impossible choice must be made"
            ],
            "scifi": [
                "Technology malfunctions unexpectedly",
                "Alien intelligence makes contact",
                "Time paradox creates complications",
                "Hidden AI agenda revealed",
                "Humanity's fate hangs in balance"
            ]
        }
        
        genre_events = events.get(genre, events["mystery"])
        return random.choice(genre_events)
    
    def _generate_triggers(self, narrative_graph: List[NarrativeNode]) -> List[str]:
        """Generate what triggers this plot event."""
        triggers = [
            "Character makes impulsive decision",
            "Hidden information comes to light",
            "External force intervenes",
            "Coincidence brings characters together",
            "Secret plan is set in motion"
        ]
        return random.sample(triggers, 2)
    
    def _generate_consequences(self, genre: str) -> List[str]:
        """Generate consequences of this plot event."""
        consequences = [
            "Raises stakes for all characters",
            "Forces unlikely alliance",
            "Reveals hidden motivations",
            "Changes power dynamics",
            "Creates ticking clock scenario"
        ]
        return random.sample(consequences, 2)
    
    def _analyze_character_arcs(
        self,
        characters: List[Dict],
        plot_predictions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Analyze how characters will develop."""
        arcs = []
        
        for char in characters:
            arc = {
                "character": char.get("name", "Unknown"),
                "starting_state": char.get("starting_state", "Neutral"),
                "predicted_arc": self._predict_arc_type(char),
                "key_moments": [
                    f"Moment of doubt at {random.choice(['midpoint', 'crisis', 'climax'])}",
                    f"Growth through {random.choice(['sacrifice', 'victory', 'failure'])}",
                    f"Final state: {random.choice(['transformed', 'confirmed', 'tragic'])}"
                ],
                "relationships": self._predict_relationship_changes(char)
            }
            arcs.append(arc)
        
        return arcs
    
    def _predict_arc_type(self, character: Dict) -> str:
        """Predict the type of character arc."""
        traits = character.get("traits", [])
        
        if "flawed" in traits or "arrogant" in traits:
            return "Redemption arc - learning humility"
        elif "timid" in traits or "insecure" in traits:
            return "Empowerment arc - finding confidence"
        elif "corrupt" in traits or "evil" in traits:
            return "Fall arc - descent into darkness"
        else:
            return "Growth arc - overcoming internal obstacle"
    
    def _predict_relationship_changes(self, character: Dict) -> List[str]:
        """Predict how character's relationships evolve."""
        changes = [
            "Alliance with former rival",
            "Betrayal by trusted friend",
            "Romantic tension with ally",
            "Mentorship of younger character",
            "Reconciliation with estranged family"
        ]
        return random.sample(changes, 2)
    
    def _generate_possible_endings(
        self,
        narrative_graph: List[NarrativeNode],
        plot_predictions: List[Dict],
        genre: str
    ) -> List[Dict[str, Any]]:
        """Generate possible story endings."""
        endings = []
        
        ending_types = {
            "mystery": [
                ("Justice served", 0.6),
                ("Criminal escapes", 0.2),
                ("Moral ambiguity remains", 0.2)
            ],
            "romance": [
                ("Happy ever after", 0.7),
                ("Bittersweet parting", 0.2),
                ("Open ending", 0.1)
            ],
            "thriller": [
                ("Hero prevails", 0.5),
                ("Pyrrhic victory", 0.3),
                ("Villain wins", 0.2)
            ]
        }
        
        for ending_type, prob in ending_types.get(genre, ending_types["mystery"]):
            ending = {
                "type": ending_type,
                "likelihood": prob,
                "description": self._describe_ending(ending_type, genre),
                "emotional_impact": random.choice(["Uplifting", "Tragic", "Thought-provoking", "Satisfying"])
            }
            endings.append(ending)
        
        return endings
    
    def _describe_ending(self, ending_type: str, genre: str) -> str:
        """Generate a description of the ending."""
        descriptions = {
            "Justice served": "The truth is revealed, wrongs are righted, and balance is restored.",
            "Criminal escapes": "The antagonist evades capture, leaving threads for future stories.",
            "Moral ambiguity remains": "Questions linger about right and wrong, leaving readers to decide.",
            "Happy ever after": "Loose ends tied up, characters find fulfillment and peace.",
            "Bittersweet parting": "Growth achieved but at personal cost, characters separate.",
            "Hero prevails": "Courage and determination overcome overwhelming odds.",
            "Villain wins": "The antagonist's plan succeeds, setting up sequel potential."
        }
        return descriptions.get(ending_type, "Resolution that fits the story's themes.")
    
    def _identify_potential_twists(
        self,
        narrative_graph: List[NarrativeNode],
        plot_predictions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Identify potential plot twists."""
        twists = []
        
        twist_types = [
            {
                "type": "Character revelation",
                "description": "Trusted ally revealed as antagonist",
                "likelihood": 0.25,
                "impact": 0.9
            },
            {
                "type": "False protagonist",
                "description": "Side character becomes central to resolution",
                "likelihood": 0.2,
                "impact": 0.7
            },
            {
                "type": "Time twist",
                "description": "Events occur in different order than presented",
                "likelihood": 0.15,
                "impact": 0.95
            },
            {
                "type": "Reality shift",
                "description": "Perceived reality is false/unreliable",
                "likelihood": 0.1,
                "impact": 0.85
            }
        ]
        
        for twist in twist_types:
            if random.random() < twist["likelihood"]:
                twists.append(twist)
        
        return twists
    
    def _extract_themes(self, narrative_graph: List[NarrativeNode]) -> List[str]:
        """Extract major themes from the narrative."""
        possible_themes = [
            "Redemption and forgiveness",
            "Power and corruption",
            "Identity and self-discovery",
            "Love and sacrifice",
            "Justice vs mercy",
            "Truth and deception",
            "Technology and humanity",
            "Tradition vs progress"
        ]
        return random.sample(possible_themes, 3)
    
    def _generate_story_recommendations(
        self,
        plot_predictions: List[Dict],
        character_arcs: List[Dict],
        endings: List[Dict]
    ) -> List[str]:
        """Generate recommendations for the story."""
        recommendations = []
        
        # Check plot pacing
        if len(plot_predictions) >= 3:
            recommendations.append("📖 Consider varying pacing - alternate action with character moments")
        
        # Character arc check
        flat_arcs = [a for a in character_arcs if "static" in a.get("predicted_arc", "")]
        if len(flat_arcs) > len(character_arcs) / 2:
            recommendations.append("👥 Too many static characters - give more protagonists growth arcs")
        
        # Ending variety
        if len(endings) < 2:
            recommendations.append("🎯 Develop alternative endings for more satisfying conclusion")
        
        # General advice
        recommendations.append("✨ Plant foreshadowing early for predicted plot points")
        recommendations.append("💡 Ensure character decisions drive plot, not coincidence")
        
        return recommendations


# Convenience function
def analyze_story(
    premise: str,
    characters: List[Dict[str, Any]],
    current_plot: str = "Beginning",
    genre: str = "mystery"
) -> Dict[str, Any]:
    """
    Quick function to analyze a story.
    
    Example:
        result = analyze_story(
            premise="Detective investigates murder at exclusive island resort",
            characters=[
                {"name": "Detective Chen", "trait": "Brilliant but alcoholic", "importance": 1.0},
                {"name": "Resort Owner", "trait": "Charming but secretive", "importance": 0.8}
            ],
            current_plot="First victim discovered",
            genre="mystery"
        )
    """
    engine = StoryDeductionEngine()
    return engine.analyze_story(premise, characters, current_plot, genre)


if __name__ == "__main__":
    # Test example
    result = analyze_story(
        premise="A detective with perfect memory investigates a murder that hasn't happened yet",
        characters=[
            {"name": "Detective Memento", "trait": "Perfect recall, emotionally distant", "importance": 1.0},
            {"name": "Victim-to-be", "trait": "Wealthy, many enemies", "importance": 0.9}
        ],
        current_plot="Detective receives vision of future murder",
        genre="mystery"
    )
    
    print("Story Analysis Results")
    print("=" * 50)
    print(f"Premise: {result['premise']}")
    print(f"Possible endings: {len(result['possible_endings'])}")
    for ending in result['possible_endings']:
        print(f"  - {ending['type']} ({ending['likelihood']*100:.0f}%)")
