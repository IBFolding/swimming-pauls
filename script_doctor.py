"""
Swimming Pauls - Script Doctor
Analyze and improve screenplays with 50 Pauls

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IssueType(Enum):
    PLOT = "plot"
    CHARACTER = "character"
    DIALOGUE = "dialogue"
    PACING = "pacing"
    CONTINUITY = "continuity"
    THEME = "theme"
    FORMAT = "format"
    CLICHE = "cliche"
    SUBTEXT = "subtext"
    EMOTION = "emotion"


@dataclass
class ScriptIssue:
    """A note from a Paul about the script."""
    paul_name: str
    paul_specialty: str
    issue_type: IssueType
    severity: int  # 1-5 (minor to critical)
    location: str  # "Scene 3", "Page 12", "Line 45"
    description: str
    suggestion: str
    confidence: float  # 0.0-1.0
    
    def to_string(self) -> str:
        severity_labels = {1: "Note", 2: "Suggestion", 3: "Issue", 4: "Problem", 5: "Critical"}
        return f"""
[{severity_labels[self.severity]}] {self.paul_name} ({self.paul_specialty})
Location: {self.location}
Issue: {self.description}
Suggestion: {self.suggestion}
Confidence: {self.confidence:.0%}
"""


class ScriptParser:
    """Parse screenplay files (.txt, .fdx, .pdf)."""
    
    def __init__(self):
        self.scene_pattern = re.compile(r'INT\.|EXT\.', re.IGNORECASE)
        self.dialogue_pattern = re.compile(r'^[A-Z][A-Z\s]+\n', re.MULTILINE)
        
    def parse(self, script_text: str) -> Dict[str, Any]:
        """Extract structure from script."""
        lines = script_text.split('\n')
        
        scenes = []
        characters = set()
        current_scene = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect scene headings
            if self.scene_pattern.match(line):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    'heading': line,
                    'line_number': i,
                    'content': [],
                    'characters': []
                }
            
            # Detect character names (all caps, followed by dialogue)
            elif line.isupper() and len(line) > 1 and len(line) < 30:
                if current_scene:
                    current_scene['characters'].append(line)
                    characters.add(line)
            
            if current_scene:
                current_scene['content'].append(line)
        
        if current_scene:
            scenes.append(current_scene)
        
        return {
            'scenes': scenes,
            'characters': list(characters),
            'line_count': len(lines),
            'scene_count': len(scenes),
            'raw_text': script_text
        }


class PaulDoctor:
    """Each Paul specializes in different script aspects."""
    
    PAULS = [
        {"name": "Plot Paul", "specialty": "Structure & Story", "focus": [IssueType.PLOT, IssueType.PACING]},
        {"name": "Character Paul", "specialty": "Character Arcs", "focus": [IssueType.CHARACTER, IssueType.EMOTION]},
        {"name": "Dialogue Paul", "specialty": "Natural Speech", "focus": [IssueType.DIALOGUE, IssueType.SUBTEXT]},
        {"name": "Pacing Paul", "specialty": "Rhythm & Flow", "focus": [IssueType.PACING, IssueType.PLOT]},
        {"name": "Continuity Paul", "specialty": "Logic & Consistency", "focus": [IssueType.CONTINUITY]},
        {"name": "Subversion Paul", "specialty": "Avoiding Clichés", "focus": [IssueType.CLICHE, IssueType.PLOT]},
        {"name": "Theme Paul", "specialty": "Thematic Depth", "focus": [IssueType.THEME]},
        {"name": "Format Paul", "specialty": "Industry Standards", "focus": [IssueType.FORMAT]},
        {"name": "Psychologist Paul", "specialty": "Emotional Truth", "focus": [IssueType.EMOTION, IssueType.CHARACTER]},
        {"name": "Opening Paul", "specialty": "First 10 Pages", "focus": [IssueType.PLOT, IssueType.PACING]},
        {"name": "Ending Paul", "specialty": "Satisfying Finishes", "focus": [IssueType.PLOT, IssueType.THEME]},
        {"name": "Conflict Paul", "specialty": "Stakes & Tension", "focus": [IssueType.PLOT, IssueType.EMOTION]},
        {"name": "Worldbuilding Paul", "specialty": "Setting & Rules", "focus": [IssueType.CONTINUITY, IssueType.THEME]},
        {"name": "Irony Paul", "specialty": "Subtext & Layers", "focus": [IssueType.SUBTEXT, IssueType.DIALOGUE]},
        {"name": "Rhythm Paul", "specialty": "Scene Beats", "focus": [IssueType.PACING, IssueType.DIALOGUE]},
    ]
    
    def __init__(self):
        self.issues_found: List[ScriptIssue] = []
    
    async def analyze(self, script_data: Dict[str, Any]) -> List[ScriptIssue]:
        """Run all Pauls on the script."""
        self.issues_found = []
        
        # Each Paul analyzes from their specialty
        tasks = [self._run_paul(paul, script_data) for paul in self.PAULS]
        await asyncio.gather(*tasks)
        
        # Sort by severity (highest first)
        self.issues_found.sort(key=lambda x: x.severity, reverse=True)
        
        return self.issues_found
    
    async def _run_paul(self, paul: Dict, script_data: Dict[str, Any]):
        """Simulate a Paul analyzing the script."""
        # In real implementation, this would call LLM API
        # For demo, generate deterministic issues based on script content
        
        issues = self._generate_issues(paul, script_data)
        self.issues_found.extend(issues)
    
    def _generate_issues(self, paul: Dict, script_data: Dict) -> List[ScriptIssue]:
        """Generate realistic script issues based on Paul's specialty."""
        issues = []
        scenes = script_data['scenes']
        
        if paul['name'] == "Plot Paul":
            if len(scenes) < 3:
                issues.append(ScriptIssue(
                    paul_name="Plot Paul",
                    paul_specialty="Structure & Story",
                    issue_type=IssueType.PLOT,
                    severity=5,
                    location="Overall",
                    description="Script lacks three-act structure. Too few scenes for feature length.",
                    suggestion="Add a clear inciting incident by scene 2, midpoint twist at 50%, and climactic sequence.",
                    confidence=0.95
                ))
            else:
                # Check for midpoint
                midpoint_scene = len(scenes) // 2
                issues.append(ScriptIssue(
                    paul_name="Plot Paul",
                    paul_specialty="Structure & Story",
                    issue_type=IssueType.PLOT,
                    severity=3,
                    location=f"Scene {midpoint_scene}",
                    description="Midpoint may lack sufficient escalation or revelation.",
                    suggestion="Ensure midpoint raises stakes significantly or reveals game-changing information.",
                    confidence=0.72
                ))
        
        elif paul['name'] == "Character Paul":
            if len(script_data['characters']) < 2:
                issues.append(ScriptIssue(
                    paul_name="Character Paul",
                    paul_specialty="Character Arcs",
                    issue_type=IssueType.CHARACTER,
                    severity=4,
                    location="Overall",
                    description="Only one major character detected. Limited opportunity for conflict and growth.",
                    suggestion="Add a strong supporting character or antagonist to challenge protagonist.",
                    confidence=0.88
                ))
            
            # Check first scene for character intro
            if scenes:
                first_scene_chars = scenes[0].get('characters', [])
                if len(first_scene_chars) == 0:
                    issues.append(ScriptIssue(
                        paul_name="Character Paul",
                        paul_specialty="Character Arcs",
                        issue_type=IssueType.CHARACTER,
                        severity=3,
                        location="Scene 1",
                        description="Opening scene lacks character introduction or clear POV.",
                        suggestion="Establish protagonist and their want/need in first 5 pages.",
                        confidence=0.81
                    ))
        
        elif paul['name'] == "Dialogue Paul":
            # Check for on-the-nose dialogue (simplified detection)
            text = script_data['raw_text'].lower()
            exposition_indicators = ['i feel', 'i think', 'the thing is', 'you know what']
            for indicator in exposition_indicators:
                if indicator in text:
                    issues.append(ScriptIssue(
                        paul_name="Dialogue Paul",
                        paul_specialty="Natural Speech",
                        issue_type=IssueType.DIALOGUE,
                        severity=2,
                        location="Multiple locations",
                        description=f"Detected on-the-nose phrases ('{indicator}'). Characters explaining feelings.",
                        suggestion="Show don't tell. Use action and subtext instead of explicit emotional statements.",
                        confidence=0.68
                    ))
                    break
        
        elif paul['name'] == "Pacing Paul":
            if len(scenes) > 0:
                avg_scene_length = script_data['line_count'] / len(scenes)
                if avg_scene_length > 50:
                    issues.append(ScriptIssue(
                        paul_name="Pacing Paul",
                        paul_specialty="Rhythm & Flow",
                        issue_type=IssueType.PACING,
                        severity=3,
                        location="Multiple scenes",
                        description=f"Scenes run long (avg {avg_scene_length:.0f} lines). Risk of losing audience attention.",
                        suggestion="Trim scenes to essential beats. Enter late, exit early.",
                        confidence=0.75
                    ))
        
        elif paul['name'] == "Continuity Paul":
            # Check for time jumps without indication
            text = script_data['raw_text']
            if 'later' in text.lower() and 'later that' not in text.lower():
                issues.append(ScriptIssue(
                    paul_name="Continuity Paul",
                    paul_specialty="Logic & Consistency",
                    issue_type=IssueType.CONTINUITY,
                    severity=2,
                    location="Unclear",
                    description="Potential time jumps without clear transitions.",
                    suggestion="Use sluglines or action lines to clarify time passage: 'LATER THAT DAY' or 'THREE WEEKS LATER'.",
                    confidence=0.61
                ))
        
        elif paul['name'] == "Subversion Paul":
            # Check for cliché openings
            text = script_data['raw_text'].lower()
            cliches = ['wake up', 'alarm clock', 'dream sequence', 'voice over']
            for cliche in cliches:
                if cliche in text[:500]:  # First 500 chars
                    issues.append(ScriptIssue(
                        paul_name="Subversion Paul",
                        paul_specialty="Avoiding Clichés",
                        issue_type=IssueType.CLICHE,
                        severity=3,
                        location="Opening",
                        description=f"Opening uses familiar trope: {cliche}. May feel unoriginal.",
                        suggestion="Consider starting in-scene with action rather than waking up/voiceover. Or subvert expectation.",
                        confidence=0.70
                    ))
                    break
        
        elif paul['name'] == "Opening Paul":
            text = script_data['raw_text']
            first_10_pages = '\n'.join(text.split('\n')[:100])
            
            if '?' not in first_10_pages and '!' not in first_10_pages:
                issues.append(ScriptIssue(
                    paul_name="Opening Paul",
                    paul_specialty="First 10 Pages",
                    issue_type=IssueType.PLOT,
                    severity=3,
                    location="Pages 1-10",
                    description="Opening lacks hook or compelling question. May not grab reader.",
                    suggestion="Introduce mystery, conflict, or unusual situation within first 3 pages.",
                    confidence=0.78
                ))
        
        elif paul['name'] == "Ending Paul":
            if len(scenes) >= 3:
                last_scene = scenes[-1]
                last_content = ' '.join(last_scene['content']).lower()
                
                if 'fade out' not in last_content and 'the end' not in last_content:
                    issues.append(ScriptIssue(
                        paul_name="Ending Paul",
                        paul_specialty="Satisfying Finishes",
                        issue_type=IssueType.PLOT,
                        severity=2,
                        location="Final scene",
                        description="Ending may lack clear resolution marker (FADE OUT, THE END).",
                        suggestion="Ensure final image resonates. Consider emotional payoff over plot wrap-up.",
                        confidence=0.55
                    ))
        
        return issues


class ScriptDoctor:
    """Main interface for script analysis."""
    
    def __init__(self):
        self.parser = ScriptParser()
        self.doctor = PaulDoctor()
        self.script_data: Optional[Dict] = None
        self.issues: List[ScriptIssue] = []
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a script file and return full report."""
        with open(file_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        return await self.analyze_text(script_text)
    
    async def analyze_text(self, script_text: str) -> Dict[str, Any]:
        """Analyze script text and return full report."""
        self.script_data = self.parser.parse(script_text)
        self.issues = await self.doctor.analyze(self.script_data)
        
        return {
            'metadata': {
                'scenes': self.script_data['scene_count'],
                'characters': len(self.script_data['characters']),
                'lines': self.script_data['line_count'],
                'analyzed_at': datetime.now().isoformat()
            },
            'issues': self.issues,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate report summary."""
        if not self.issues:
            return {
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'top_concerns': []
            }
        
        severity_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for issue in self.issues:
            severity_counts[issue.severity] += 1
        
        # Top concerns (severity 4-5)
        critical_issues = [i for i in self.issues if i.severity >= 4][:3]
        
        return {
            'total_issues': len(self.issues),
            'critical': severity_counts[5],
            'high': severity_counts[4],
            'medium': severity_counts[3],
            'low': severity_counts[2],
            'notes': severity_counts[1],
            'top_concerns': [i.description for i in critical_issues]
        }
    
    def generate_notes_report(self) -> str:
        """Generate studio notes format from Pauls."""
        if not self.issues:
            return "🎬 PAUL NOTES: No major issues found! Script looks solid."
        
        report_lines = [
            "=" * 60,
            "🎬 SWIMMING PAULS - SCRIPT DOCTOR NOTES",
            "=" * 60,
            f"Script: {self.script_data['scene_count']} scenes, {len(self.script_data['characters'])} characters",
            f"Total Notes: {len(self.issues)} from {len(self.doctor.PAULS)} Pauls",
            "",
            "📊 SEVERITY BREAKDOWN:",
            f"  Critical (5): {self._generate_summary()['critical']}",
            f"  High (4): {self._generate_summary()['high']}",
            f"  Medium (3): {self._generate_summary()['medium']}",
            f"  Low (2): {self._generate_summary()['low']}",
            f"  Notes (1): {self._generate_summary()['notes']}",
            "",
            "=" * 60,
            "🚨 TOP PRIORITY FIXES",
            "=" * 60,
            ""
        ]
        
        # Critical and High issues first
        critical = [i for i in self.issues if i.severity >= 4]
        for issue in critical:
            report_lines.append(issue.to_string())
            report_lines.append("")
        
        if not critical:
            report_lines.append("✅ No critical issues found!")
            report_lines.append("")
        
        report_lines.extend([
            "=" * 60,
            "📝 ADDITIONAL NOTES",
            "=" * 60,
            ""
        ])
        
        # Medium and lower
        other = [i for i in self.issues if i.severity < 4]
        for issue in other[:10]:  # Limit to first 10
            report_lines.append(issue.to_string())
            report_lines.append("")
        
        if len(other) > 10:
            report_lines.append(f"... and {len(other) - 10} more notes")
        
        report_lines.extend([
            "",
            "=" * 60,
            "💡 NEXT STEPS",
            "=" * 60,
            "1. Address CRITICAL issues first",
            "2. Consider HIGH priority suggestions",
            "3. MEDIUM/LOW at your discretion",
            "4. Run script doctor again after revisions",
            "",
            "🦷 Happy rewriting!",
            "=" * 60
        ])
        
        return '\n'.join(report_lines)
    
    def interactive_mode(self) -> str:
        """Interactive mode for applying fixes."""
        if not self.issues:
            return "No issues to address!"
        
        output = [
            "\n🎬 INTERACTIVE SCRIPT DOCTOR\n",
            "Review each issue and choose: (y)es, (n)o, (m)aybe\n",
            "-" * 60
        ]
        
        approved_fixes = []
        
        for i, issue in enumerate(self.issues[:20], 1):  # First 20 issues
            output.append(f"\n[{i}/{min(len(self.issues), 20)}] {issue.paul_name}")
            output.append(f"Location: {issue.location}")
            output.append(f"Issue: {issue.description}")
            output.append(f"Suggestion: {issue.suggestion}")
            output.append(f"Severity: {'🔴' * issue.severity}{'⚪' * (5-issue.severity)}")
            output.append("\nApply this fix? (y/n/m/s)kip all")
            output.append("-" * 60)
            
            # In real interactive mode, wait for user input
            # For demo, auto-approve high-confidence, high-severity
            if issue.severity >= 4 and issue.confidence >= 0.8:
                approved_fixes.append(issue)
                output.append("[Auto-approved: High severity + confidence]")
            elif issue.confidence >= 0.9:
                approved_fixes.append(issue)
                output.append("[Auto-approved: High confidence]")
            else:
                output.append("[Pending user decision]")
        
        output.extend([
            "\n" + "=" * 60,
            f"APPROVED FIXES: {len(approved_fixes)}",
            "=" * 60
        ])
        
        for fix in approved_fixes:
            output.append(f"\n✓ {fix.paul_name}: {fix.description[:50]}...")
        
        return '\n'.join(output)


# CLI Interface
def print_usage():
    print("""
🎬 Swimming Pauls - Script Doctor

USAGE:
    python script_doctor.py <script.txt> [options]

OPTIONS:
    --report          Generate full Paul Notes report (default)
    --interactive     Interactive mode - choose which fixes to apply
    --summary         Quick summary only
    --json            Output as JSON
    --format <type>   studio (default), inline, or json

EXAMPLES:
    python script_doctor.py myscript.txt
    python script_doctor.py myscript.txt --interactive
    python script_doctor.py myscript.txt --format json > report.json

The 15 Paul Doctors:
  • Plot Paul - Structure & story
  • Character Paul - Arcs & development
  • Dialogue Paul - Natural speech
  • Pacing Paul - Rhythm & flow
  • Continuity Paul - Logic checks
  • Subversion Paul - Avoid clichés
  • Theme Paul - Thematic depth
  • Format Paul - Industry standards
  • Psychologist Paul - Emotional truth
  • Opening Paul - First 10 pages
  • Ending Paul - Satisfying finish
  • Conflict Paul - Stakes & tension
  • Worldbuilding Paul - Setting & rules
  • Irony Paul - Subtext & layers
  • Rhythm Paul - Scene beats
""")


async def main():
    import sys
    
    if len(sys.argv) < 2:
        print_usage()
        return
    
    file_path = sys.argv[1]
    mode = "report"
    output_format = "studio"
    
    # Parse args
    for arg in sys.argv[2:]:
        if arg == "--interactive":
            mode = "interactive"
        elif arg == "--summary":
            mode = "summary"
        elif arg == "--json":
            output_format = "json"
        elif arg.startswith("--format"):
            output_format = arg.split("=")[-1] if "=" in arg else "studio"
    
    print(f"🎬 Analyzing {file_path}...")
    print("👥 Summoning 15 Paul Doctors...\n")
    
    doctor = ScriptDoctor()
    result = await doctor.analyze_file(file_path)
    
    if mode == "summary":
        summary = result['summary']
        print(f"✅ Analysis Complete!")
        print(f"   Scenes: {result['metadata']['scenes']}")
        print(f"   Characters: {result['metadata']['characters']}")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Critical: {summary['critical']} | High: {summary['high']} | Medium: {summary['medium']}")
        
        if summary['top_concerns']:
            print("\n🚨 Top Concerns:")
            for concern in summary['top_concerns']:
                print(f"   • {concern}")
    
    elif mode == "interactive":
        print(doctor.interactive_mode())
    
    else:  # report mode
        if output_format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            print(doctor.generate_notes_report())


if __name__ == "__main__":
    asyncio.run(main())
