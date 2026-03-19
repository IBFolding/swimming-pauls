"""
Swimming Pauls - Custom Skill API Framework
Allows users to create and attach custom skills to Pauls.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class SkillResult:
    """Result from executing a skill."""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class SkillMetadata:
    """Metadata for a custom skill."""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Anonymous"
    best_for: List[str] = field(default_factory=list)  # Which Paul types benefit most
    requires_api_key: bool = False
    api_key_env: Optional[str] = None
    cache_ttl: int = 300  # seconds
    rate_limit: int = 100  # calls per hour


class Skill(ABC):
    """
    Base class for all Swimming Pauls skills.
    
    To create a custom skill:
    1. Inherit from this class
    2. Define metadata
    3. Implement execute() method
    4. Place in skills/custom/ directory
    
    Example:
        class WeatherSkill(Skill):
            metadata = SkillMetadata(
                name="weather_check",
                description="Get weather for location",
                best_for=["Farmer Paul", "Travel Paul"]
            )
            
            async def execute(self, location: str) -> SkillResult:
                # Your implementation
                return SkillResult(success=True, data={"temp": 72})
    """
    
    metadata: SkillMetadata = None
    
    def __init__(self):
        self.call_count = 0
        self.last_called = None
        self.cache: Dict[str, Any] = {}
        
    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """
        Execute the skill.
        
        Args:
            **kwargs: Skill-specific parameters
            
        Returns:
            SkillResult with success status and data
        """
        pass
    
    async def execute_with_cache(self, **kwargs) -> SkillResult:
        """Execute with caching support."""
        cache_key = json.dumps(kwargs, sort_keys=True)
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_result = self.cache[cache_key]
            if asyncio.get_event_loop().time() - cached_time < self.metadata.cache_ttl:
                return cached_result
        
        # Execute
        start = asyncio.get_event_loop().time()
        result = await self.execute(**kwargs)
        result.execution_time_ms = (asyncio.get_event_loop().time() - start) * 1000
        
        # Cache successful results
        if result.success:
            self.cache[cache_key] = (asyncio.get_event_loop().time(), result)
        
        self.call_count += 1
        self.last_called = asyncio.get_event_loop().time()
        
        return result
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment if required."""
        if self.metadata and self.metadata.api_key_env:
            import os
            return os.getenv(self.metadata.api_key_env)
        return None
    
    def to_dict(self) -> Dict:
        """Serialize skill info."""
        return {
            "name": self.metadata.name if self.metadata else "unknown",
            "description": self.metadata.description if self.metadata else "",
            "version": self.metadata.version if self.metadata else "1.0.0",
            "author": self.metadata.author if self.metadata else "Anonymous",
            "call_count": self.call_count,
            "best_for": self.metadata.best_for if self.metadata else [],
        }


class SkillRegistry:
    """
    Registry for managing custom skills.
    
    Usage:
        registry = SkillRegistry()
        registry.discover_skills()  # Auto-load from skills/custom/
        
        # Get skill for a Paul
        skill = registry.get_skill("weather_check")
        result = await skill.execute(location="NYC")
    """
    
    def __init__(self, skills_dir: str = "skills/custom"):
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.paul_skills: Dict[str, List[str]] = {}  # paul_name -> [skill_names]
        
    def discover_skills(self) -> int:
        """
        Auto-discover skills from skills/custom/ directory.
        
        Returns:
            Number of skills discovered
        """
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True)
            return 0
        
        count = 0
        for skill_file in self.skills_dir.glob("*.py"):
            if skill_file.stem.startswith("_"):
                continue
                
            try:
                skill = self._load_skill_from_file(skill_file)
                if skill:
                    self.register_skill(skill)
                    count += 1
            except Exception as e:
                print(f"⚠️  Failed to load skill {skill_file}: {e}")
                
        return count
    
    def _load_skill_from_file(self, file_path: Path) -> Optional[Skill]:
        """Load a skill class from a Python file."""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Skill subclasses
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Skill) and 
                obj is not Skill and
                hasattr(obj, 'metadata')):
                return obj()
                
        return None
    
    def register_skill(self, skill: Skill):
        """Register a skill instance."""
        if skill.metadata:
            self.skills[skill.metadata.name] = skill
            print(f"✅ Registered skill: {skill.metadata.name}")
        
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def get_skills_for_paul(self, paul_name: str) -> List[Skill]:
        """Get all skills assigned to a Paul."""
        skill_names = self.paul_skills.get(paul_name, [])
        return [self.skills[name] for name in skill_names if name in self.skills]
    
    def assign_skill_to_paul(self, paul_name: str, skill_name: str):
        """Assign a skill to a Paul."""
        if skill_name not in self.skills:
            raise ValueError(f"Skill {skill_name} not found")
            
        if paul_name not in self.paul_skills:
            self.paul_skills[paul_name] = []
            
        if skill_name not in self.paul_skills[paul_name]:
            self.paul_skills[paul_name].append(skill_name)
            
    def remove_skill_from_paul(self, paul_name: str, skill_name: str):
        """Remove a skill from a Paul."""
        if paul_name in self.paul_skills:
            self.paul_skills[paul_name] = [
                s for s in self.paul_skills[paul_name] if s != skill_name
            ]
            
    def get_recommended_skills(self, paul_type: str) -> List[Skill]:
        """Get skills recommended for a Paul type."""
        recommended = []
        for skill in self.skills.values():
            if skill.metadata and paul_type in skill.metadata.best_for:
                recommended.append(skill)
        return recommended
    
    def list_all_skills(self) -> List[Dict]:
        """List all registered skills."""
        return [skill.to_dict() for skill in self.skills.values()]
    
    def create_skill_template(self, skill_name: str, description: str) -> str:
        """Generate a skill template file."""
        template = f'''"""
{skill_name} - Custom Swimming Pauls Skill
{description}
"""

from swimming_pauls.skills import Skill, SkillMetadata, SkillResult


class {skill_name.replace('_', '').title()}Skill(Skill):
    """
    {description}
    """
    
    metadata = SkillMetadata(
        name="{skill_name}",
        description="{description}",
        version="1.0.0",
        author="Your Name",
        best_for=["Trader Paul", "Analyst Paul"],  # Which Pauls benefit most
        requires_api_key=False,  # Set to True if API key needed
        api_key_env=None,  # Environment variable name for API key
        cache_ttl=300,  # Cache results for 5 minutes
    )
    
    async def execute(self, **kwargs) -> SkillResult:
        """
        Execute the skill.
        
        Args:
            query: Description of parameter
            
        Returns:
            SkillResult with data
        """
        try:
            # Your implementation here
            # Can use self.get_api_key() if requires_api_key=True
            
            data = {{
                "result": "your data here",
                "timestamp": "2024-..."
            }}
            
            return SkillResult(success=True, data=data)
            
        except Exception as e:
            return SkillResult(success=False, error=str(e))


# Export for auto-discovery
skill_class = {skill_name.replace('_', '').title()}Skill
'''
        
        # Write template
        file_path = self.skills_dir / f"{skill_name}.py"
        file_path.write_text(template)
        
        return str(file_path)


# Built-in example skills
class WeatherSkill(Skill):
    """Example weather checking skill."""
    
    metadata = SkillMetadata(
        name="weather_local",
        description="Get local weather conditions",
        best_for=["Farmer Paul", "Energy Paul", "Travel Paul"],
        requires_api_key=False,
    )
    
    async def execute(self, location: str = None) -> SkillResult:
        """Get weather for location."""
        try:
            # Example using wttr.in (no API key needed)
            import aiohttp
            
            loc = location or "auto:ip"
            url = f"https://wttr.in/{loc}?format=j1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
                    
                    current = data['current_condition'][0]
                    
                    return SkillResult(success=True, data={
                        "temperature_f": current['temp_F'],
                        "temperature_c": current['temp_C'],
                        "condition": current['weatherDesc'][0]['value'],
                        "humidity": current['humidity'],
                        "location": data['nearest_area'][0]['areaName'][0]['value'],
                    })
                    
        except Exception as e:
            return SkillResult(success=False, error=str(e))


class RSSFeedSkill(Skill):
    """Fetch and parse RSS feeds."""
    
    metadata = SkillMetadata(
        name="rss_feed",
        description="Fetch latest news from RSS feeds",
        best_for=["Professor Paul", "News Paul", "Analyst Paul"],
    )
    
    async def execute(self, feed_url: str, limit: int = 5) -> SkillResult:
        """Fetch RSS feed."""
        try:
            from web_intelligence import WebIntelligence
            
            async with WebIntelligence() as web:
                items = await web.get_rss_feed(feed_url, limit)
                
                return SkillResult(success=True, data={
                    "items": items,
                    "count": len(items),
                })
                
        except Exception as e:
            return SkillResult(success=False, error=str(e))


# Export
__all__ = [
    'Skill',
    'SkillMetadata', 
    'SkillResult',
    'SkillRegistry',
    'WeatherSkill',
    'RSSFeedSkill',
]


# Import optional skills
try:
    from skills.bankr_skill import BankrSkill
    BANKR_AVAILABLE = True
except ImportError:
    BANKR_AVAILABLE = False


# CLI for skill management
if __name__ == "__main__":
    import sys
    
    registry = SkillRegistry()
    
    if len(sys.argv) < 2:
        print("Usage: python skills.py <command> [args]")
        print("\nCommands:")
        print("  list                    List all skills")
        print("  create <name> <desc>    Create new skill template")
        print("  assign <paul> <skill>   Assign skill to Paul")
        print("  discover               Auto-discover custom skills")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "list":
        registry.discover_skills()
        skills = registry.list_all_skills()
        print(f"\n📋 {len(skills)} skills registered:\n")
        for skill in skills:
            print(f"  🔧 {skill['name']}")
            print(f"     {skill['description']}")
            print(f"     Best for: {', '.join(skill['best_for'])}")
            print()
            
    elif command == "create" and len(sys.argv) >= 4:
        name = sys.argv[2]
        desc = sys.argv[3]
        path = registry.create_skill_template(name, desc)
        print(f"✅ Created skill template: {path}")
        print(f"\nEdit the file and implement your skill logic!")
        
    elif command == "discover":
        count = registry.discover_skills()
        print(f"✅ Discovered {count} custom skills")
        
    elif command == "assign" and len(sys.argv) >= 4:
        paul = sys.argv[2]
        skill = sys.argv[3]
        registry.assign_skill_to_paul(paul, skill)
        print(f"✅ Assigned {skill} to {paul}")
