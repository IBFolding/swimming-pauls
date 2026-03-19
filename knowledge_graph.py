"""
Knowledge Graph - Semantic Graph Construction from Seed Data

Constructs semantic knowledge graphs from various data sources (PDFs, text, JSON)
using entity extraction and relationship mapping.

Part of Paul's World - Enhanced Knowledge System for Swimming Pauls

Author: Howard (H.O.W.A.R.D)
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import asyncio
from datetime import datetime

# Optional imports with fallbacks
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import networkx as nx
    NETWORKX_SUPPORT = True
except ImportError:
    NETWORKX_SUPPORT = False


@dataclass
class Entity:
    """Represents an extracted entity from text."""
    id: str
    name: str
    entity_type: str  # person, organization, location, concept, technology, etc.
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    id: str
    source_id: str
    target_id: str
    relation_type: str  # works_at, founded, invested_in, competitor, etc.
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Relationship):
            return self.id == other.id
        return False


@dataclass
class KnowledgeGraph:
    """Container for entities and relationships."""
    name: str
    entities: Dict[str, Entity] = field(default_factory=dict)
    relationships: Dict[str, Relationship] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_entity(self, entity: Entity) -> Entity:
        """Add an entity to the graph."""
        if entity.id in self.entities:
            # Merge with existing
            existing = self.entities[entity.id]
            existing.aliases = list(set(existing.aliases + entity.aliases))
            existing.source_refs = list(set(existing.source_refs + entity.source_refs))
            existing.confidence = max(existing.confidence, entity.confidence)
            existing.metadata.update(entity.metadata)
            return existing
        self.entities[entity.id] = entity
        return entity
    
    def add_relationship(self, rel: Relationship) -> Relationship:
        """Add a relationship to the graph."""
        if rel.id in self.relationships:
            existing = self.relationships[rel.id]
            existing.confidence = max(existing.confidence, rel.confidence)
            existing.evidence = list(set(existing.evidence + rel.evidence))
            existing.metadata.update(rel.metadata)
            return existing
        self.relationships[rel.id] = rel
        return rel
    
    def get_entity_relationships(self, entity_id: str) -> Tuple[List[Relationship], List[Relationship]]:
        """Get all relationships where entity is source or target."""
        outgoing = [r for r in self.relationships.values() if r.source_id == entity_id]
        incoming = [r for r in self.relationships.values() if r.target_id == entity_id]
        return outgoing, incoming
    
    def get_neighbors(self, entity_id: str) -> List[Entity]:
        """Get all entities directly connected to the given entity."""
        outgoing, incoming = self.get_entity_relationships(entity_id)
        neighbor_ids = set()
        for rel in outgoing:
            neighbor_ids.add(rel.target_id)
        for rel in incoming:
            neighbor_ids.add(rel.source_id)
        return [self.entities[eid] for eid in neighbor_ids if eid in self.entities]
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[Relationship]]:
        """Find a path between two entities using BFS."""
        if source_id not in self.entities or target_id not in self.entities:
            return None
        
        if NETWORKX_SUPPORT:
            # Use NetworkX for efficient pathfinding
            G = self.to_networkx()
            try:
                path_nodes = nx.shortest_path(G, source_id, target_id)
                # Convert node path to edge path
                path_edges = []
                for i in range(len(path_nodes) - 1):
                    for rel in self.relationships.values():
                        if rel.source_id == path_nodes[i] and rel.target_id == path_nodes[i+1]:
                            path_edges.append(rel)
                            break
                return path_edges
            except nx.NetworkXNoPath:
                return None
        else:
            # Fallback BFS implementation
            visited = {source_id}
            queue = [(source_id, [])]
            
            while queue:
                current, path = queue.pop(0)
                if current == target_id:
                    return path
                
                if len(path) >= max_depth:
                    continue
                
                outgoing, incoming = self.get_entity_relationships(current)
                for rel in outgoing + incoming:
                    next_id = rel.target_id if rel.source_id == current else rel.source_id
                    if next_id not in visited:
                        visited.add(next_id)
                        queue.append((next_id, path + [rel]))
            
            return None
    
    def query_entities(self, entity_type: Optional[str] = None, 
                       name_pattern: Optional[str] = None) -> List[Entity]:
        """Query entities by type and/or name pattern."""
        results = []
        for entity in self.entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if name_pattern and not re.search(name_pattern, entity.name, re.IGNORECASE):
                continue
            results.append(entity)
        return results
    
    def query_relationships(self, relation_type: Optional[str] = None,
                           source_type: Optional[str] = None,
                           target_type: Optional[str] = None) -> List[Relationship]:
        """Query relationships with optional filters."""
        results = []
        for rel in self.relationships.values():
            if relation_type and rel.relation_type != relation_type:
                continue
            if source_type:
                source = self.entities.get(rel.source_id)
                if not source or source.entity_type != source_type:
                    continue
            if target_type:
                target = self.entities.get(rel.target_id)
                if not target or target.entity_type != target_type:
                    continue
            results.append(rel)
        return results
    
    def get_subgraph(self, entity_ids: List[str], depth: int = 1) -> 'KnowledgeGraph':
        """Extract a subgraph centered around specified entities."""
        subgraph = KnowledgeGraph(name=f"{self.name}_subgraph")
        
        # Add initial entities
        for eid in entity_ids:
            if eid in self.entities:
                subgraph.add_entity(self.entities[eid])
        
        # Expand by depth
        current_ids = set(entity_ids)
        for _ in range(depth):
            next_ids = set()
            for eid in current_ids:
                outgoing, incoming = self.get_entity_relationships(eid)
                for rel in outgoing + incoming:
                    subgraph.add_relationship(rel)
                    other_id = rel.target_id if rel.source_id == eid else rel.source_id
                    if other_id in self.entities:
                        subgraph.add_entity(self.entities[other_id])
                        next_ids.add(other_id)
            current_ids = next_ids
        
        return subgraph
    
    def to_networkx(self) -> Any:
        """Convert to NetworkX graph for advanced analysis."""
        if not NETWORKX_SUPPORT:
            raise ImportError("NetworkX is required for this operation")
        
        G = nx.DiGraph()
        
        for entity in self.entities.values():
            G.add_node(entity.id, **{
                'name': entity.name,
                'type': entity.entity_type,
                'confidence': entity.confidence
            })
        
        for rel in self.relationships.values():
            G.add_edge(rel.source_id, rel.target_id, **{
                'type': rel.relation_type,
                'confidence': rel.confidence
            })
        
        return G
    
    def calculate_centrality(self) -> Dict[str, float]:
        """Calculate PageRank centrality for all entities."""
        if not NETWORKX_SUPPORT:
            raise ImportError("NetworkX is required for centrality calculation")
        
        G = self.to_networkx()
        return nx.pagerank(G)
    
    def find_communities(self) -> List[List[str]]:
        """Find communities in the graph using Louvain algorithm."""
        if not NETWORKX_SUPPORT:
            raise ImportError("NetworkX is required for community detection")
        
        G = self.to_networkx().to_undirected()
        communities = nx.community.louvain_communities(G)
        return [list(c) for c in communities]
    
    def export_json(self, path: Optional[str] = None) -> str:
        """Export graph to JSON format."""
        data = {
            'name': self.name,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'entities': [
                {
                    'id': e.id,
                    'name': e.name,
                    'type': e.entity_type,
                    'confidence': e.confidence,
                    'aliases': e.aliases,
                    'metadata': e.metadata
                }
                for e in self.entities.values()
            ],
            'relationships': [
                {
                    'id': r.id,
                    'source': r.source_id,
                    'target': r.target_id,
                    'type': r.relation_type,
                    'confidence': r.confidence,
                    'evidence': r.evidence
                }
                for r in self.relationships.values()
            ]
        }
        
        json_str = json.dumps(data, indent=2, default=str)
        
        if path:
            Path(path).write_text(json_str)
        
        return json_str
    
    @classmethod
    def import_json(cls, json_data: Union[str, Dict]) -> 'KnowledgeGraph':
        """Import graph from JSON format."""
        if isinstance(json_data, str):
            # Check if it's a file path or JSON string
            # First check if it looks like a path (reasonable length and simple chars)
            if len(json_data) < 200 and ('/' in json_data or '\\' in json_data or json_data.endswith('.json')):
                json_path = Path(json_data)
                try:
                    if json_path.exists() and json_path.suffix == '.json':
                        data = json.loads(json_path.read_text())
                    else:
                        data = json.loads(json_data)
                except OSError:
                    # Path too long or other OS error, treat as JSON string
                    data = json.loads(json_data)
            else:
                data = json.loads(json_data)
        else:
            data = json_data
        
        graph = cls(name=data.get('name', 'imported'))
        graph.metadata = data.get('metadata', {})
        
        for e_data in data.get('entities', []):
            entity = Entity(
                id=e_data['id'],
                name=e_data['name'],
                entity_type=e_data['type'],
                confidence=e_data.get('confidence', 1.0),
                aliases=e_data.get('aliases', []),
                metadata=e_data.get('metadata', {})
            )
            graph.add_entity(entity)
        
        for r_data in data.get('relationships', []):
            rel = Relationship(
                id=r_data['id'],
                source_id=r_data['source'],
                target_id=r_data['target'],
                relation_type=r_data['type'],
                confidence=r_data.get('confidence', 1.0),
                evidence=r_data.get('evidence', [])
            )
            graph.add_relationship(rel)
        
        return graph


class EntityExtractor:
    """Extracts entities from various text sources."""
    
    # Common entity patterns and types
    ENTITY_PATTERNS = {
        'PERSON': [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # First Last
            r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.) [A-Z][a-z]+\b',
            r'\bCEO \w+\b', r'\bFounder \w+\b', r'\bDirector \w+\b',
        ],
        'ORGANIZATION': [
            r'\b[A-Z][a-z]* (?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems|Labs)\b',
            r'\b(?:The )?[A-Z][a-zA-Z]+ (?:Group|Fund|Capital|Ventures|Partners)\b',
            r'\b[A-Z]{2,}(?:\s+[A-Z][a-z]+)*\b',  # Acronyms like "ABC Corp"
        ],
        'LOCATION': [
            r'\b(?:New York|San Francisco|Los Angeles|Chicago|Boston|Austin|Seattle)\b',
            r'\b(?:Silicon Valley|Wall Street|Bay Area)\b',
            r'\b[A-Z][a-z]+, [A-Z]{2}\b',  # City, ST
        ],
        'TECHNOLOGY': [
            r'\b(?:AI|ML|Blockchain|Crypto|Web3|DeFi|NFT|Smart Contract)\b',
            r'\b(?:Ethereum|Bitcoin|Solana|Polygon|Base)\b',
            r'\b(?:React|Node\.js|Python|Rust|Go|TypeScript)\b',
        ],
        'FINANCIAL': [
            r'\$[\d,]+(?:\.\d{2})?(?:[MBK])?\b',  # Dollar amounts
            r'\b(?:Series [A-F]|IPO|Acquisition|Merger|Valuation)\b',
            r'\b(?:Seed|Angel|Venture|Growth|Private Equity)\b',
        ],
        'MARKET': [
            r'\b(?:Bull|Bear|Bullish|Bearish|Long|Short|Longs|Shorts)\b',
            r'\b(?:Support|Resistance|Breakout|Pullback|Rally|Correction)\b',
            r'\b(?:Volume|Liquidity|Volatility|Momentum)\b',
        ]
    }
    
    # Relationship patterns
    RELATIONSHIP_PATTERNS = {
        'founded_by': [
            r'(\w+\s+\w+) founded (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) was founded by (\w+\s+\w+)',
        ],
        'works_at': [
            r'(\w+\s+\w+) (?:works?|employed) at (\w+(?:\s+\w+)*)',
            r'(\w+\s+\w+) (?:joined|hired by) (\w+(?:\s+\w+)*)',
        ],
        'invested_in': [
            r'(\w+(?:\s+\w+)*) invested in (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) led (?:the )?(?:round|investment) in (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) participated in (?:the )?(?:round|investment) in (\w+(?:\s+\w+)*)',
        ],
        'acquired': [
            r'(\w+(?:\s+\w+)*) acquired (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) bought (\w+(?:\s+\w+)*)',
            r'acquisition of (\w+(?:\s+\w+)*) by (\w+(?:\s+\w+)*)',
        ],
        'competitor': [
            r'(\w+(?:\s+\w+)*) competes with (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) vs\.? (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) rival (\w+(?:\s+\w+)*)',
        ],
        'partnership': [
            r'(\w+(?:\s+\w+)*) partnered with (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) collaboration with (\w+(?:\s+\w+)*)',
            r'partnership between (\w+(?:\s+\w+)*) and (\w+(?:\s+\w+)*)',
        ],
    }
    
    def __init__(self, custom_patterns: Optional[Dict] = None):
        self.patterns = custom_patterns or self.ENTITY_PATTERNS
        self.extracted_entities: Dict[str, Entity] = {}
    
    def extract_from_text(self, text: str, source_ref: str = "") -> Tuple[List[Entity], List[Relationship]]:
        """Extract entities and relationships from raw text."""
        entities = []
        relationships = []
        
        # Extract entities
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(0)
                    entity_id = self._generate_id(name)
                    
                    if entity_id not in self.extracted_entities:
                        entity = Entity(
                            id=entity_id,
                            name=name,
                            entity_type=entity_type,
                            source_refs=[source_ref] if source_ref else [],
                            confidence=0.7  # Base confidence for pattern matching
                        )
                        self.extracted_entities[entity_id] = entity
                        entities.append(entity)
        
        # Extract relationships
        for rel_type, patterns in self.RELATIONSHIP_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        source_name = match.group(1)
                        target_name = match.group(2)
                        
                        source_id = self._generate_id(source_name)
                        target_id = self._generate_id(target_name)
                        
                        # Only create relationship if both entities exist
                        if source_id in self.extracted_entities and target_id in self.extracted_entities:
                            rel = Relationship(
                                id=f"{source_id}_{rel_type}_{target_id}",
                                source_id=source_id,
                                target_id=target_id,
                                relation_type=rel_type,
                                evidence=[match.group(0)],
                                timestamp=datetime.now()
                            )
                            relationships.append(rel)
        
        return entities, relationships
    
    def extract_from_pdf(self, pdf_path: str) -> Tuple[List[Entity], List[Relationship]]:
        """Extract entities from a PDF file."""
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 is required for PDF extraction")
        
        text = ""
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        
        return self.extract_from_text(text, source_ref=pdf_path)
    
    def extract_from_json(self, json_path: str, 
                          entity_fields: Optional[List[str]] = None,
                          relation_fields: Optional[List[str]] = None) -> Tuple[List[Entity], List[Relationship]]:
        """Extract entities from structured JSON data."""
        with open(json_path) as f:
            data = json.load(f)
        
        entities = []
        relationships = []
        
        def process_item(item: Any, path: str = ""):
            if isinstance(item, dict):
                # Check for entity fields
                if entity_fields:
                    for field in entity_fields:
                        if field in item:
                            value = item[field]
                            if isinstance(value, str):
                                entity_type = item.get('type', 'concept')
                                entity_id = self._generate_id(value)
                                
                                if entity_id not in self.extracted_entities:
                                    entity = Entity(
                                        id=entity_id,
                                        name=value,
                                        entity_type=entity_type,
                                        metadata={'source_path': path},
                                        source_refs=[json_path]
                                    )
                                    self.extracted_entities[entity_id] = entity
                                    entities.append(entity)
                
                # Process nested structures
                for key, value in item.items():
                    process_item(value, f"{path}.{key}" if path else key)
                    
            elif isinstance(item, list):
                for i, subitem in enumerate(item):
                    process_item(subitem, f"{path}[{i}]")
        
        process_item(data)
        
        # Extract relationships if specified
        if relation_fields and isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    source = item.get(relation_fields[0])
                    target = item.get(relation_fields[1]) if len(relation_fields) > 1 else None
                    rel_type = item.get(relation_fields[2]) if len(relation_fields) > 2 else 'related_to'
                    
                    if source and target:
                        source_id = self._generate_id(str(source))
                        target_id = self._generate_id(str(target))
                        
                        if source_id in self.extracted_entities and target_id in self.extracted_entities:
                            rel = Relationship(
                                id=f"{source_id}_{rel_type}_{target_id}",
                                source_id=source_id,
                                target_id=target_id,
                                relation_type=rel_type
                            )
                            relationships.append(rel)
        
        return entities, relationships
    
    def _generate_id(self, name: str) -> str:
        """Generate a consistent ID from a name."""
        normalized = re.sub(r'\s+', '_', name.lower().strip())
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"{normalized}_{hash_suffix}"


class GraphBuilder:
    """Builds knowledge graphs from various data sources."""
    
    def __init__(self, name: str = "knowledge_graph"):
        self.graph = KnowledgeGraph(name=name)
        self.extractor = EntityExtractor()
    
    def add_text(self, text: str, source: str = "") -> 'GraphBuilder':
        """Add text content to the graph."""
        entities, relationships = self.extractor.extract_from_text(text, source)
        
        for entity in entities:
            self.graph.add_entity(entity)
        
        for rel in relationships:
            self.graph.add_relationship(rel)
        
        return self
    
    def add_pdf(self, pdf_path: str) -> 'GraphBuilder':
        """Add PDF content to the graph."""
        entities, relationships = self.extractor.extract_from_pdf(pdf_path)
        
        for entity in entities:
            self.graph.add_entity(entity)
        
        for rel in relationships:
            self.graph.add_relationship(rel)
        
        return self
    
    def add_json(self, json_path: str, **kwargs) -> 'GraphBuilder':
        """Add JSON content to the graph."""
        entities, relationships = self.extractor.extract_from_json(json_path, **kwargs)
        
        for entity in entities:
            self.graph.add_entity(entity)
        
        for rel in relationships:
            self.graph.add_relationship(rel)
        
        return self
    
    def add_directory(self, directory: str, 
                      extensions: List[str] = ['.txt', '.md', '.json']) -> 'GraphBuilder':
        """Add all files in a directory with specified extensions."""
        dir_path = Path(directory)
        
        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                try:
                    if ext == '.pdf':
                        self.add_pdf(str(file_path))
                    elif ext == '.json':
                        self.add_json(str(file_path))
                    else:
                        text = file_path.read_text(encoding='utf-8', errors='ignore')
                        self.add_text(text, source=str(file_path))
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return self
    
    def build(self) -> KnowledgeGraph:
        """Return the constructed knowledge graph."""
        return self.graph
    
    def merge_graphs(self, other_graph: KnowledgeGraph) -> 'GraphBuilder':
        """Merge another graph into this one."""
        for entity in other_graph.entities.values():
            self.graph.add_entity(entity)
        
        for rel in other_graph.relationships.values():
            self.graph.add_relationship(rel)
        
        return self


def create_market_knowledge_graph(seed_data_path: Optional[str] = None) -> KnowledgeGraph:
    """
    Create a knowledge graph for financial/crypto markets.
    
    Optionally loads seed data from a directory containing:
    - PDFs: Whitepapers, research reports
    - JSON: Market data, token information
    - Text files: News articles, analysis
    """
    builder = GraphBuilder(name="market_knowledge")
    
    if seed_data_path:
        builder.add_directory(seed_data_path)
    
    return builder.build()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Build a graph from text
    sample_text = """
    Ethereum was founded by Vitalik Buterin. Ethereum competes with Solana and Bitcoin.
    Andreessen Horowitz invested in Ethereum. Coinbase partnered with Ethereum Foundation.
    Vitalik Buterin works at Ethereum Foundation.
    """
    
    builder = GraphBuilder(name="crypto_ecosystem")
    graph = builder.add_text(sample_text).build()
    
    print(f"Entities: {len(graph.entities)}")
    print(f"Relationships: {len(graph.relationships)}")
    
    for entity in graph.entities.values():
        print(f"  - {entity.name} ({entity.entity_type})")
    
    for rel in graph.relationships.values():
        source = graph.entities.get(rel.source_id)
        target = graph.entities.get(rel.target_id)
        if source and target:
            print(f"  - {source.name} --[{rel.relation_type}]--> {target.name}")
    
    # Export to JSON
    json_output = graph.export_json("/tmp/knowledge_graph.json")
    print(f"\nExported to JSON (length: {len(json_output)} chars)")
    
    # Query example
    people = graph.query_entities(entity_type='PERSON')
    print(f"\nPeople in graph: {[e.name for e in people]}")
    
    # Path finding
    if len(graph.entities) >= 2:
        entity_ids = list(graph.entities.keys())
        path = graph.find_path(entity_ids[0], entity_ids[-1])
        if path:
            print(f"\nPath found between {graph.entities[entity_ids[0]].name} and {graph.entities[entity_ids[-1]].name}")
