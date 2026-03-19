"""
GraphRAG - Graph Retrieval-Augmented Generation for Swimming Pauls

Structured knowledge extraction from documents with semantic search capabilities.
Builds traversable knowledge graphs with LLM-powered entity/relationship extraction.

Features:
- Extract structured entities and relationships from PDF, TXT, MD files
- Build traversable knowledge graphs with NetworkX
- Semantic search across documents using embeddings
- Query interface: "what do we know about X?"
- Integration with Paul's World knowledge system
- Persistent storage with vector search

Author: Howard (H.O.W.A.R.D)
"""

import os
import re
import json
import hashlib
import asyncio
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from datetime import datetime
from enum import Enum
import warnings

# Optional dependencies with fallbacks
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    warnings.warn("PyPDF2 not installed. PDF support disabled.")

try:
    import networkx as nx
    NETWORKX_SUPPORT = True
except ImportError:
    NETWORKX_SUPPORT = False
    warnings.warn("NetworkX not installed. Graph algorithms disabled.")

try:
    import numpy as np
    NUMPY_SUPPORT = True
except ImportError:
    NUMPY_SUPPORT = False
    warnings.warn("NumPy not installed. Vector operations will be slow.")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_SUPPORT = True
except ImportError:
    EMBEDDING_SUPPORT = False
    warnings.warn("sentence-transformers not installed. Semantic search disabled.")

# Try to import LLM client from existing codebase
try:
    from llm_client import LLMClient
    LLM_SUPPORT = True
except ImportError:
    LLM_SUPPORT = False

# Import existing knowledge graph structures
try:
    from knowledge_graph import (
        Entity as KGEntity,
        Relationship as KGRelationship,
        KnowledgeGraph,
        EntityExtractor,
        GraphBuilder
    )
    KG_SUPPORT = True
except ImportError:
    KG_SUPPORT = False
    warnings.warn("knowledge_graph.py not found. Using standalone GraphRAG.")


# ============================================================================
# DATA MODELS
# ============================================================================

class EntityType(Enum):
    """Types of entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    CONCEPT = "concept"
    PRODUCT = "product"
    EVENT = "event"
    MARKET = "market"
    CURRENCY = "currency"
    PROTOCOL = "protocol"
    INDUSTRY = "industry"
    CUSTOM = "custom"


class RelationType(Enum):
    """Types of relationships between entities."""
    FOUNDED_BY = "founded_by"
    WORKS_AT = "works_at"
    INVESTED_IN = "invested_in"
    ACQUIRED = "acquired"
    PARTNERED_WITH = "partnered_with"
    COMPETES_WITH = "competes_with"
    BUILT_ON = "built_on"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    CREATED = "created"
    INFLUENCES = "influences"
    RELATED_TO = "related_to"
    CUSTOM = "custom"


@dataclass
class GraphEntity:
    """
    Enhanced entity with GraphRAG-specific attributes.
    """
    id: str
    name: str
    entity_type: str
    description: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    aliases: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)  # Document sources
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, GraphEntity):
            return self.id == other.id
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'entity_type': self.entity_type,
            'description': self.description,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'aliases': self.aliases,
            'source_refs': self.source_refs,
            'embedding': self.embedding,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphEntity':
        """Create from dictionary."""
        entity = cls(
            id=data['id'],
            name=data['name'],
            entity_type=data['entity_type'],
            description=data.get('description', ''),
            confidence=data.get('confidence', 1.0),
            metadata=data.get('metadata', {}),
            aliases=data.get('aliases', []),
            source_refs=data.get('source_refs', []),
            embedding=data.get('embedding')
        )
        if 'created_at' in data:
            entity.created_at = datetime.fromisoformat(data['created_at'])
        return entity


@dataclass
class GraphRelationship:
    """
    Enhanced relationship with GraphRAG-specific attributes.
    """
    id: str
    source_id: str
    target_id: str
    relation_type: str
    description: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    source_refs: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, GraphRelationship):
            return self.id == other.id
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.relation_type,
            'relation_type': self.relation_type,
            'description': self.description,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'evidence': self.evidence,
            'source_refs': self.source_refs,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphRelationship':
        """Create from dictionary."""
        rel = cls(
            id=data['id'],
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type'],
            description=data.get('description', ''),
            confidence=data.get('confidence', 1.0),
            metadata=data.get('metadata', {}),
            evidence=data.get('evidence', []),
            source_refs=data.get('source_refs', [])
        )
        if data.get('timestamp'):
            rel.timestamp = datetime.fromisoformat(data['timestamp'])
        return rel


@dataclass
class DocumentChunk:
    """A chunk of text from a document with metadata."""
    id: str
    text: str
    source_doc: str
    chunk_index: int
    embedding: Optional[List[float]] = None
    entities_mentioned: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'text': self.text,
            'source_doc': self.source_doc,
            'chunk_index': self.chunk_index,
            'embedding': self.embedding,
            'entities_mentioned': self.entities_mentioned,
            'metadata': self.metadata
        }


@dataclass
class SearchResult:
    """Result from a semantic search query."""
    entity: Optional[GraphEntity]
    relationship: Optional[GraphRelationship]
    chunk: Optional[DocumentChunk]
    score: float
    context: str
    path: Optional[List[GraphRelationship]] = None


# ============================================================================
# DOCUMENT PROCESSORS
# ============================================================================

class DocumentProcessor:
    """Process various document formats into text chunks."""
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: Union[str, Path]) -> List[DocumentChunk]:
        """Process a file based on its extension."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        ext = path.suffix.lower()
        
        if ext == '.pdf':
            return self._process_pdf(path)
        elif ext in ['.txt', '.md', '.markdown']:
            return self._process_text(path)
        elif ext == '.json':
            return self._process_json(path)
        elif ext in ['.py', '.js', '.ts', '.sol']:
            return self._process_code(path)
        else:
            # Try to read as text
            try:
                return self._process_text(path)
            except:
                raise ValueError(f"Unsupported file format: {ext}")
    
    def _process_pdf(self, path: Path) -> List[DocumentChunk]:
        """Extract text from PDF and chunk it."""
        if not PDF_SUPPORT:
            raise ImportError("PyPDF2 required for PDF processing")
        
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        return self._chunk_text(text, str(path))
    
    def _process_text(self, path: Path) -> List[DocumentChunk]:
        """Read text file and chunk it."""
        text = path.read_text(encoding='utf-8', errors='ignore')
        return self._chunk_text(text, str(path))
    
    def _process_json(self, path: Path) -> List[DocumentChunk]:
        """Process JSON file, extracting text content."""
        with open(path) as f:
            data = json.load(f)
        
        # Convert JSON to text representation
        text = json.dumps(data, indent=2)
        return self._chunk_text(text, str(path), metadata={'format': 'json'})
    
    def _process_code(self, path: Path) -> List[DocumentChunk]:
        """Process code files with special handling."""
        text = path.read_text(encoding='utf-8', errors='ignore')
        
        # Add code-specific metadata
        ext = path.suffix[1:]  # Remove the dot
        metadata = {
            'format': 'code',
            'language': ext,
            'file_type': 'source_code'
        }
        
        return self._chunk_text(text, str(path), metadata=metadata)
    
    def _chunk_text(self, text: str, source: str, metadata: Optional[Dict] = None) -> List[DocumentChunk]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at a sentence or paragraph boundary
            if end < len(text):
                # Look for sentence boundary
                for i in range(min(100, end - start)):
                    char_idx = end - i - 1
                    if char_idx >= 0 and text[char_idx] in '.!?\n':
                        end = char_idx + 1
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = hashlib.md5(f"{source}:{chunk_index}".encode()).hexdigest()[:16]
                chunks.append(DocumentChunk(
                    id=chunk_id,
                    text=chunk_text,
                    source_doc=source,
                    chunk_index=chunk_index,
                    metadata=metadata or {}
                ))
            
            start = end
            if start < len(text):
                start = max(start - self.chunk_overlap, 0)
            chunk_index += 1
        
        return chunks


# ============================================================================
# LLM-POWERED EXTRACTION
# ============================================================================

class LLMEntityExtractor:
    """Use LLM to extract entities and relationships from text."""
    
    EXTRACTION_PROMPT = """Extract entities and relationships from the following text.

Text:
{text}

Extract the following:
1. **Entities**: People, organizations, locations, technologies, concepts, products, events
2. **Relationships**: How entities are connected (founded_by, works_at, invested_in, etc.)

Respond in this exact JSON format:
```json
{
  "entities": [
    {
      "name": "Entity Name",
      "type": "person|organization|location|technology|concept|product|event|market",
      "description": "Brief description",
      "aliases": ["alternative names"]
    }
  ],
  "relationships": [
    {
      "source": "Entity Name",
      "target": "Entity Name",
      "type": "relationship_type",
      "description": "Brief description of relationship"
    }
  ]
}
```

Rules:
- Only extract entities and relationships explicitly mentioned in the text
- Use consistent naming for the same entity
- Include confidence scores (0.0-1.0) based on how clearly the relationship is stated
- Focus on financial, technological, and market-related entities when relevant"""
    
    def __init__(self, llm_client: Optional[Any] = None, provider: str = "ollama", model: str = "llama3"):
        self.llm_client = llm_client
        self.provider = provider
        self.model = model
        
        if not llm_client and LLM_SUPPORT:
            try:
                self.llm_client = LLMClient(provider=provider, model=model)
            except:
                pass
    
    async def extract_from_text(self, text: str, source_ref: str = "") -> Tuple[List[GraphEntity], List[GraphRelationship]]:
        """Extract entities and relationships using LLM."""
        if not self.llm_client:
            raise ValueError("LLM client not available")
        
        # Truncate text if too long
        max_length = 4000
        truncated_text = text[:max_length] if len(text) > max_length else text
        
        prompt = self.EXTRACTION_PROMPT.format(text=truncated_text)
        
        try:
            # Generate extraction
            response = await self._call_llm(prompt)
            
            # Parse JSON response
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            data = json.loads(response)
            
            entities = []
            relationships = []
            
            # Create entities
            entity_map = {}
            for e_data in data.get('entities', []):
                entity = self._create_entity(e_data, source_ref)
                entities.append(entity)
                entity_map[entity.name.lower()] = entity.id
            
            # Create relationships
            for r_data in data.get('relationships', []):
                source_name = r_data.get('source', '').lower()
                target_name = r_data.get('target', '').lower()
                
                if source_name in entity_map and target_name in entity_map:
                    rel = self._create_relationship(
                        r_data, 
                        entity_map[source_name],
                        entity_map[target_name],
                        source_ref
                    )
                    relationships.append(rel)
            
            return entities, relationships
            
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            return [], []
    
    async def extract_from_chunks(self, chunks: List[DocumentChunk]) -> Tuple[List[GraphEntity], List[GraphRelationship]]:
        """Extract from multiple document chunks."""
        all_entities = []
        all_relationships = []
        
        for chunk in chunks:
            entities, relationships = await self.extract_from_text(
                chunk.text, 
                source_ref=chunk.source_doc
            )
            
            # Add chunk reference to entities
            for entity in entities:
                entity.source_refs.append(f"{chunk.source_doc}#chunk{chunk.chunk_index}")
            
            all_entities.extend(entities)
            all_relationships.extend(relationships)
        
        # Deduplicate entities
        entity_map = {}
        for entity in all_entities:
            if entity.id in entity_map:
                # Merge
                existing = entity_map[entity.id]
                existing.aliases = list(set(existing.aliases + entity.aliases))
                existing.source_refs = list(set(existing.source_refs + entity.source_refs))
            else:
                entity_map[entity.id] = entity
        
        return list(entity_map.values()), all_relationships
    
    def _create_entity(self, data: Dict, source_ref: str) -> GraphEntity:
        """Create a GraphEntity from extraction data."""
        name = data.get('name', '')
        entity_id = self._generate_id(name)
        
        return GraphEntity(
            id=entity_id,
            name=name,
            entity_type=data.get('type', 'concept'),
            description=data.get('description', ''),
            confidence=data.get('confidence', 0.8),
            aliases=data.get('aliases', []),
            source_refs=[source_ref] if source_ref else [],
            metadata={'extraction_method': 'llm'}
        )
    
    def _create_relationship(self, data: Dict, source_id: str, target_id: str, source_ref: str) -> GraphRelationship:
        """Create a GraphRelationship from extraction data."""
        rel_id = f"{source_id}_{data.get('type', 'related_to')}_{target_id}"
        
        return GraphRelationship(
            id=hashlib.md5(rel_id.encode()).hexdigest()[:16],
            source_id=source_id,
            target_id=target_id,
            relation_type=data.get('type', 'related_to'),
            description=data.get('description', ''),
            confidence=data.get('confidence', 0.7),
            evidence=[data.get('description', '')],
            source_refs=[source_ref] if source_ref else [],
            timestamp=datetime.now()
        )
    
    def _generate_id(self, name: str) -> str:
        """Generate a consistent ID from a name."""
        normalized = re.sub(r'\s+', '_', name.lower().strip())
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"{normalized}_{hash_suffix}"
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the prompt."""
        if hasattr(self.llm_client, 'generate'):
            return await self.llm_client.generate(prompt)
        elif hasattr(self.llm_client, 'generate_response'):
            return await self.llm_client.generate_response(
                persona_name="GraphRAG Extractor",
                persona_description="You are an expert at extracting structured information from text.",
                question=prompt,
                context="",
                memory=""
            )
        else:
            raise ValueError("LLM client doesn't have expected methods")


# ============================================================================
# HYBRID EXTRACTOR (LLM + Pattern Matching)
# ============================================================================

class HybridEntityExtractor:
    """Combines LLM extraction with pattern-based extraction as fallback."""
    
    # Enhanced patterns for crypto/finance domain
    ENTITY_PATTERNS = {
        'person': [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?) [A-Z][a-z]+\b',
            r'\bCEO \w+\b', r'\bFounder \w+\b', r'\bCTO \w+\b',
        ],
        'organization': [
            r'\b[A-Z][a-z]* (?:Inc\.?|Corp\.?|LLC|Ltd\.?|Company|Technologies?|Labs?)\b',
            r'\b(?:The )?[A-Z][a-zA-Z]+ (?:Group|Fund|Capital|Ventures|Partners|Foundation)\b',
            r'\b[A-Z]{2,}(?:\s+[A-Z][a-z]+)*\b',
        ],
        'location': [
            r'\b(?:New York|San Francisco|Los Angeles|Chicago|Boston|Austin|Seattle|Miami)\b',
            r'\b(?:Silicon Valley|Wall Street|Bay Area|Cayman Islands|Singapore|Dubai|Zug)\b',
        ],
        'technology': [
            r'\b(?:AI|ML|Blockchain|Crypto|Web3|DeFi|NFT|Smart Contract|DAO)\b',
            r'\b(?:Ethereum|Bitcoin|Solana|Polygon|Base|Arbitrum|Optimism|Avalanche)\b',
            r'\b(?:React|Node\.js|Python|Rust|Go|TypeScript|Solidity|Move)\b',
        ],
        'protocol': [
            r'\b(?:Uniswap|Aave|Compound|MakerDAO|Curve|Convex|Yearn|Lido|Rocket Pool)\b',
            r'\b(?:OpenSea|Blur|Magic Eden|Tensor)\b',
        ],
        'currency': [
            r'\b(?:BTC|ETH|SOL|USDC|USDT|DAI|BNB|AVAX|MATIC)\b',
            r'\$[\d,]+(?:\.\d{2})?(?:[MBK])?\b',
        ],
        'market': [
            r'\b(?:Bull|Bear|Bullish|Bearish|Long|Short|Longs|Shorts)\b',
            r'\b(?:Support|Resistance|Breakout|Pullback|Rally|Correction|Accumulation)\b',
        ]
    }
    
    RELATIONSHIP_PATTERNS = {
        'founded_by': [
            r'(\w+\s+\w+) founded (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) was founded by (\w+\s+\w+)',
        ],
        'works_at': [
            r'(\w+\s+\w+) (?:works?|employed) at (\w+(?:\s+\w+)*)',
            r'(\w+\s+\w+) (?:joined|hired by) (\w+(?:\s+\w+)*)',
            r'(\w+\s+\w+), CEO of (\w+(?:\s+\w+)*)',
        ],
        'invested_in': [
            r'(\w+(?:\s+\w+)*) invested in (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) led (?:the )?(?:round|investment) in (\w+(?:\s+\w+)*)',
        ],
        'acquired': [
            r'(\w+(?:\s+\w+)*) acquired (\w+(?:\s+\w+)*)',
            r'acquisition of (\w+(?:\s+\w+)*) by (\w+(?:\s+\w+)*)',
        ],
        'partnered_with': [
            r'(\w+(?:\s+\w+)*) partnered with (\w+(?:\s+\w+)*)',
            r'partnership between (\w+(?:\s+\w+)*) and (\w+(?:\s+\w+)*)',
        ],
        'competes_with': [
            r'(\w+(?:\s+\w+)*) competes with (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) vs\.? (\w+(?:\s+\w+)*)',
        ],
        'built_on': [
            r'(\w+(?:\s+\w+)*) built on (\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) deployed on (\w+(?:\s+\w+)*)',
        ],
    }
    
    def __init__(self, use_llm: bool = True, llm_provider: str = "ollama", llm_model: str = "llama3"):
        self.use_llm = use_llm and LLM_SUPPORT
        self.llm_extractor = None
        
        if self.use_llm:
            try:
                self.llm_extractor = LLMEntityExtractor(provider=llm_provider, model=llm_model)
            except Exception as e:
                print(f"Could not initialize LLM extractor: {e}")
                self.use_llm = False
    
    async def extract(self, text: str, source_ref: str = "") -> Tuple[List[GraphEntity], List[GraphRelationship]]:
        """Extract entities and relationships using best available method."""
        
        # Try LLM first if available
        if self.use_llm and self.llm_extractor:
            try:
                entities, relationships = await self.llm_extractor.extract_from_text(text, source_ref)
                if entities:
                    return entities, relationships
            except Exception as e:
                print(f"LLM extraction failed, falling back to patterns: {e}")
        
        # Fall back to pattern-based extraction
        return self._extract_patterns(text, source_ref)
    
    async def extract_from_chunks(self, chunks: List[DocumentChunk]) -> Tuple[List[GraphEntity], List[GraphRelationship]]:
        """Extract from multiple chunks."""
        all_entities = {}
        all_relationships = []
        
        for chunk in chunks:
            entities, relationships = await self.extract(chunk.text, chunk.source_doc)
            
            for entity in entities:
                entity.source_refs.append(f"{chunk.source_doc}#chunk{chunk.chunk_index}")
                if entity.id in all_entities:
                    # Merge
                    existing = all_entities[entity.id]
                    existing.aliases = list(set(existing.aliases + entity.aliases))
                    existing.source_refs = list(set(existing.source_refs + entity.source_refs))
                else:
                    all_entities[entity.id] = entity
            
            all_relationships.extend(relationships)
        
        return list(all_entities.values()), all_relationships
    
    def _extract_patterns(self, text: str, source_ref: str) -> Tuple[List[GraphEntity], List[GraphRelationship]]:
        """Pattern-based extraction as fallback."""
        entities = []
        entity_map = {}
        
        # Extract entities
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    name = match.group(0)
                    entity_id = self._generate_id(name)
                    
                    if entity_id not in entity_map:
                        entity = GraphEntity(
                            id=entity_id,
                            name=name,
                            entity_type=entity_type,
                            confidence=0.6,
                            source_refs=[source_ref] if source_ref else [],
                            metadata={'extraction_method': 'pattern'}
                        )
                        entity_map[entity_id] = entity
                        entities.append(entity)
        
        # Extract relationships
        relationships = []
        for rel_type, patterns in self.RELATIONSHIP_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.groups()) >= 2:
                        source_name = match.group(1)
                        target_name = match.group(2)
                        
                        source_id = self._generate_id(source_name)
                        target_id = self._generate_id(target_name)
                        
                        if source_id in entity_map and target_id in entity_map:
                            rel = GraphRelationship(
                                id=f"{source_id}_{rel_type}_{target_id}",
                                source_id=source_id,
                                target_id=target_id,
                                relation_type=rel_type,
                                evidence=[match.group(0)],
                                source_refs=[source_ref] if source_ref else [],
                                timestamp=datetime.now(),
                                metadata={'extraction_method': 'pattern'}
                            )
                            relationships.append(rel)
        
        return entities, relationships
    
    def _generate_id(self, name: str) -> str:
        """Generate a consistent ID from a name."""
        normalized = re.sub(r'\s+', '_', name.lower().strip())
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:6]
        return f"{normalized}_{hash_suffix}"


# ============================================================================
# EMBEDDING MANAGER
# ============================================================================

class EmbeddingManager:
    """Manage embeddings for semantic search."""
    
    DEFAULT_MODEL = "all-MiniLM-L6-v2"
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or self.DEFAULT_MODEL
        self.model = None
        self.embedding_cache: Dict[str, List[float]] = {}
        
        if EMBEDDING_SUPPORT:
            try:
                self.model = SentenceTransformer(self.model_name)
                print(f"✅ Loaded embedding model: {self.model_name}")
            except Exception as e:
                print(f"⚠️ Could not load embedding model: {e}")
    
    def is_available(self) -> bool:
        """Check if embeddings are available."""
        return self.model is not None
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if not self.model:
            raise ValueError("Embedding model not available")
        
        # Check cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_list=True)
        self.embedding_cache[cache_key] = embedding
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self.model:
            raise ValueError("Embedding model not available")
        
        return self.model.encode(texts, convert_to_list=True)
    
    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if NUMPY_SUPPORT:
            a_vec = np.array(a)
            b_vec = np.array(b)
            return np.dot(a_vec, b_vec) / (np.linalg.norm(a_vec) * np.linalg.norm(b_vec))
        else:
            # Pure Python implementation
            dot = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(x * x for x in b) ** 0.5
            return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
    
    def search_similar(self, query: str, candidates: List[Tuple[str, List[float]]], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for most similar items to query."""
        query_embedding = self.embed_text(query)
        
        scores = []
        for item_id, embedding in candidates:
            similarity = self.cosine_similarity(query_embedding, embedding)
            scores.append((item_id, similarity))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# ============================================================================
# MAIN GRAPHRAG CLASS
# ============================================================================

class GraphRAG:
    """
    Graph Retrieval-Augmented Generation system for Swimming Pauls.
    
    Provides structured knowledge extraction and semantic search over documents.
    Integrates with Paul's World knowledge system.
    """
    
    def __init__(
        self,
        storage_path: str = "data/graphrag",
        use_llm: bool = True,
        llm_provider: str = "ollama",
        llm_model: str = "llama3",
        embedding_model: Optional[str] = None
    ):
        """
        Initialize GraphRAG.
        
        Args:
            storage_path: Path for persistent storage
            use_llm: Whether to use LLM for extraction
            llm_provider: LLM provider (ollama, openai, anthropic)
            llm_model: Model name
            embedding_model: Sentence transformer model name
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.document_processor = DocumentProcessor()
        self.extractor = HybridEntityExtractor(
            use_llm=use_llm,
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        self.embedding_manager = EmbeddingManager(embedding_model)
        
        # Data storage
        self.entities: Dict[str, GraphEntity] = {}
        self.relationships: Dict[str, GraphRelationship] = {}
        self.chunks: Dict[str, DocumentChunk] = {}
        self.processed_files: Set[str] = set()
        
        # NetworkX graph for traversal
        self._graph = None
        if NETWORKX_SUPPORT:
            self._graph = nx.DiGraph()
        
        # Load existing data
        self._load()
    
    # ========================================================================
    # INGESTION
    # ========================================================================
    
    async def ingest_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Ingest a document file into the knowledge graph.
        
        Supports: PDF, TXT, MD, JSON, and code files
        """
        path = Path(file_path)
        
        if str(path) in self.processed_files:
            return {'status': 'already_processed', 'file': str(path)}
        
        print(f"📄 Processing: {path.name}")
        
        try:
            # Process document into chunks
            chunks = self.document_processor.process_file(path)
            print(f"   → {len(chunks)} chunks")
            
            # Extract entities and relationships
            entities, relationships = await self.extractor.extract_from_chunks(chunks)
            print(f"   → {len(entities)} entities, {len(relationships)} relationships")
            
            # Generate embeddings if available
            if self.embedding_manager.is_available():
                await self._generate_embeddings(chunks, entities)
            
            # Store everything
            for chunk in chunks:
                self.chunks[chunk.id] = chunk
            
            for entity in entities:
                self._add_entity(entity)
            
            for rel in relationships:
                self._add_relationship(rel)
            
            self.processed_files.add(str(path))
            
            # Rebuild graph
            self._rebuild_graph()
            
            # Save to disk
            self._save()
            
            return {
                'status': 'success',
                'file': str(path),
                'chunks': len(chunks),
                'entities': len(entities),
                'relationships': len(relationships)
            }
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return {'status': 'error', 'file': str(path), 'error': str(e)}
    
    async def ingest_directory(
        self,
        directory: Union[str, Path],
        extensions: List[str] = ['.pdf', '.txt', '.md', '.markdown']
    ) -> List[Dict[str, Any]]:
        """Ingest all files in a directory."""
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        results = []
        
        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                result = await self.ingest_file(file_path)
                results.append(result)
        
        return results
    
    async def ingest_text(self, text: str, source: str = "user_input") -> Dict[str, Any]:
        """Ingest raw text."""
        chunks = self.document_processor._chunk_text(text, source)
        
        entities, relationships = await self.extractor.extract_from_chunks(chunks)
        
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
        
        for entity in entities:
            self._add_entity(entity)
        
        for rel in relationships:
            self._add_relationship(rel)
        
        self._rebuild_graph()
        self._save()
        
        return {
            'status': 'success',
            'source': source,
            'chunks': len(chunks),
            'entities': len(entities),
            'relationships': len(relationships)
        }
    
    async def _generate_embeddings(self, chunks: List[DocumentChunk], entities: List[GraphEntity]):
        """Generate embeddings for chunks and entities."""
        # Embed chunks
        chunk_texts = [chunk.text for chunk in chunks]
        chunk_embeddings = self.embedding_manager.embed_batch(chunk_texts)
        for chunk, embedding in zip(chunks, chunk_embeddings):
            chunk.embedding = embedding
        
        # Embed entities
        entity_texts = [f"{e.name}: {e.description}" for e in entities]
        if entity_texts:
            entity_embeddings = self.embedding_manager.embed_batch(entity_texts)
            for entity, embedding in zip(entities, entity_embeddings):
                entity.embedding = embedding
    
    def _add_entity(self, entity: GraphEntity):
        """Add or merge entity."""
        if entity.id in self.entities:
            # Merge with existing
            existing = self.entities[entity.id]
            existing.aliases = list(set(existing.aliases + entity.aliases))
            existing.source_refs = list(set(existing.source_refs + entity.source_refs))
            existing.confidence = max(existing.confidence, entity.confidence)
            existing.metadata.update(entity.metadata)
        else:
            self.entities[entity.id] = entity
    
    def _add_relationship(self, rel: GraphRelationship):
        """Add or merge relationship."""
        if rel.id in self.relationships:
            # Merge with existing
            existing = self.relationships[rel.id]
            existing.confidence = max(existing.confidence, rel.confidence)
            existing.evidence = list(set(existing.evidence + rel.evidence))
            existing.source_refs = list(set(existing.source_refs + rel.source_refs))
        else:
            self.relationships[rel.id] = rel
    
    def _rebuild_graph(self):
        """Rebuild NetworkX graph."""
        if not self._graph:
            return
        
        self._graph.clear()
        
        # Add nodes
        for entity in self.entities.values():
            self._graph.add_node(
                entity.id,
                name=entity.name,
                type=entity.entity_type,
                confidence=entity.confidence
            )
        
        # Add edges
        for rel in self.relationships.values():
            if rel.source_id in self.entities and rel.target_id in self.entities:
                self._graph.add_edge(
                    rel.source_id,
                    rel.target_id,
                    type=rel.relation_type,
                    confidence=rel.confidence,
                    id=rel.id
                )
    
    # ========================================================================
    # QUERY INTERFACE
    # ========================================================================
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the knowledge graph: "What do we know about X?"
        
        Returns relevant entities, relationships, and document chunks.
        """
        results = {
            'question': question,
            'entities': [],
            'relationships': [],
            'chunks': [],
            'paths': [],
            'summary': ''
        }
        
        # Search for relevant entities
        entity_results = self._search_entities(question, top_k)
        results['entities'] = [self._entity_to_dict(e) for e, _ in entity_results]
        
        # Find related relationships
        for entity, score in entity_results:
            outgoing, incoming = self._get_entity_relationships(entity.id)
            for rel in outgoing[:3]:
                results['relationships'].append(self._relationship_to_dict(rel))
            for rel in incoming[:3]:
                results['relationships'].append(self._relationship_to_dict(rel))
        
        # Search chunks
        chunk_results = self._search_chunks(question, top_k)
        results['chunks'] = [{'text': c.text[:300], 'source': c.source_doc, 'score': s} 
                            for c, s in chunk_results]
        
        # Find paths between top entities
        if len(entity_results) >= 2:
            entity_ids = [e.id for e, _ in entity_results[:3]]
            for i in range(len(entity_ids)):
                for j in range(i + 1, len(entity_ids)):
                    path = self.find_path(entity_ids[i], entity_ids[j])
                    if path:
                        results['paths'].append({
                            'from': self.entities[entity_ids[i]].name,
                            'to': self.entities[entity_ids[j]].name,
                            'path': [self._relationship_to_dict(r) for r in path]
                        })
        
        # Generate summary
        results['summary'] = self._generate_summary(results, question)
        
        return results
    
    def _search_entities(self, query: str, top_k: int = 5) -> List[Tuple[GraphEntity, float]]:
        """Search for entities matching the query."""
        results = []
        query_lower = query.lower()
        
        # Exact and fuzzy matching
        for entity in self.entities.values():
            score = 0.0
            
            # Exact name match
            if query_lower in entity.name.lower():
                score += 1.0
            
            # Alias match
            for alias in entity.aliases:
                if query_lower in alias.lower():
                    score += 0.8
            
            # Semantic search if embeddings available
            if self.embedding_manager.is_available() and entity.embedding:
                query_embedding = self.embedding_manager.embed_text(query)
                semantic_score = self.embedding_manager.cosine_similarity(
                    query_embedding, entity.embedding
                )
                score = max(score, semantic_score)
            
            if score > 0:
                results.append((entity, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _search_chunks(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """Search for relevant document chunks."""
        results = []
        
        if self.embedding_manager.is_available():
            # Semantic search
            query_embedding = self.embedding_manager.embed_text(query)
            
            for chunk in self.chunks.values():
                if chunk.embedding:
                    score = self.embedding_manager.cosine_similarity(
                        query_embedding, chunk.embedding
                    )
                    if score > 0.5:
                        results.append((chunk, score))
        else:
            # Keyword search fallback
            query_lower = query.lower()
            for chunk in self.chunks.values():
                if query_lower in chunk.text.lower():
                    score = chunk.text.lower().count(query_lower) / len(chunk.text.split())
                    results.append((chunk, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _get_entity_relationships(self, entity_id: str) -> Tuple[List[GraphRelationship], List[GraphRelationship]]:
        """Get all relationships for an entity."""
        outgoing = [r for r in self.relationships.values() if r.source_id == entity_id]
        incoming = [r for r in self.relationships.values() if r.target_id == entity_id]
        return outgoing, incoming
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[GraphRelationship]]:
        """Find a path between two entities."""
        if not NETWORKX_SUPPORT or not self._graph:
            return self._bfs_path(source_id, target_id, max_depth)
        
        try:
            node_path = nx.shortest_path(self._graph, source_id, target_id)
            
            # Convert to relationships
            rel_path = []
            for i in range(len(node_path) - 1):
                for rel in self.relationships.values():
                    if rel.source_id == node_path[i] and rel.target_id == node_path[i + 1]:
                        rel_path.append(rel)
                        break
            
            return rel_path
        except nx.NetworkXNoPath:
            return None
    
    def _bfs_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[GraphRelationship]]:
        """BFS pathfinding without NetworkX."""
        if source_id not in self.entities or target_id not in self.entities:
            return None
        
        visited = {source_id}
        queue = [(source_id, [])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target_id:
                return path
            
            if len(path) >= max_depth:
                continue
            
            outgoing, incoming = self._get_entity_relationships(current)
            
            for rel in outgoing + incoming:
                next_id = rel.target_id if rel.source_id == current else rel.source_id
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [rel]))
        
        return None
    
    def _generate_summary(self, results: Dict, question: str) -> str:
        """Generate a natural language summary of results."""
        parts = []
        
        if results['entities']:
            entity_names = [e['name'] for e in results['entities'][:3]]
            parts.append(f"Found information about: {', '.join(entity_names)}.")
        
        if results['relationships']:
            parts.append(f"Discovered {len(results['relationships'])} connections.")
        
        if results['paths']:
            parts.append(f"Found {len(results['paths'])} relationship paths.")
        
        if results['chunks']:
            sources = list(set(c['source'] for c in results['chunks']))
            parts.append(f"Sources: {', '.join(sources[:3])}")
        
        return " ".join(parts) if parts else "No relevant information found."
    
    def get_neighbors(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all entities connected to the given entity."""
        if entity_id not in self.entities:
            return []
        
        outgoing, incoming = self._get_entity_relationships(entity_id)
        neighbors = []
        
        for rel in outgoing:
            if rel.target_id in self.entities:
                target = self.entities[rel.target_id]
                neighbors.append({
                    'entity': self._entity_to_dict(target),
                    'relationship': self._relationship_to_dict(rel),
                    'direction': 'outgoing'
                })
        
        for rel in incoming:
            if rel.source_id in self.entities:
                source = self.entities[rel.source_id]
                neighbors.append({
                    'entity': self._entity_to_dict(source),
                    'relationship': self._relationship_to_dict(rel),
                    'direction': 'incoming'
                })
        
        return neighbors
    
    # ========================================================================
    # PERSISTENCE
    # ========================================================================
    
    def _save(self):
        """Save graph data to disk."""
        data = {
            'entities': {k: v.to_dict() for k, v in self.entities.items()},
            'relationships': {k: v.to_dict() for k, v in self.relationships.items()},
            'chunks': {k: v.to_dict() for k, v in self.chunks.items()},
            'processed_files': list(self.processed_files),
            'version': '1.0'
        }
        
        with open(self.storage_path / 'graph_data.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self):
        """Load graph data from disk."""
        data_file = self.storage_path / 'graph_data.json'
        
        if not data_file.exists():
            return
        
        try:
            with open(data_file) as f:
                data = json.load(f)
            
            # Load entities
            for k, v in data.get('entities', {}).items():
                self.entities[k] = GraphEntity.from_dict(v)
            
            # Load relationships
            for k, v in data.get('relationships', {}).items():
                self.relationships[k] = GraphRelationship.from_dict(v)
            
            # Load chunks
            for k, v in data.get('chunks', {}).items():
                chunk = DocumentChunk(
                    id=v['id'],
                    text=v['text'],
                    source_doc=v['source_doc'],
                    chunk_index=v['chunk_index'],
                    embedding=v.get('embedding'),
                    entities_mentioned=v.get('entities_mentioned', []),
                    metadata=v.get('metadata', {})
                )
                self.chunks[k] = chunk
            
            # Load processed files
            self.processed_files = set(data.get('processed_files', []))
            
            # Rebuild graph
            self._rebuild_graph()
            
            print(f"✅ Loaded GraphRAG: {len(self.entities)} entities, {len(self.relationships)} relationships")
            
        except Exception as e:
            print(f"⚠️ Could not load GraphRAG data: {e}")
    
    # ========================================================================
    # UTILITIES
    # ========================================================================
    
    def _entity_to_dict(self, entity: GraphEntity) -> Dict[str, Any]:
        """Convert entity to dict for output."""
        return {
            'id': entity.id,
            'name': entity.name,
            'type': entity.entity_type,
            'description': entity.description,
            'confidence': entity.confidence,
            'aliases': entity.aliases,
            'source_refs': entity.source_refs
        }
    
    def _relationship_to_dict(self, rel: GraphRelationship) -> Dict[str, Any]:
        """Convert relationship to dict for output."""
        source = self.entities.get(rel.source_id, {})
        target = self.entities.get(rel.target_id, {})
        
        return {
            'id': rel.id,
            'source': {'id': rel.source_id, 'name': getattr(source, 'name', 'Unknown')},
            'target': {'id': rel.target_id, 'name': getattr(target, 'name', 'Unknown')},
            'type': rel.relation_type,
            'description': rel.description,
            'confidence': rel.confidence
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        entity_types = defaultdict(int)
        for e in self.entities.values():
            entity_types[e.entity_type] += 1
        
        rel_types = defaultdict(int)
        for r in self.relationships.values():
            rel_types[r.relation_type] += 1
        
        return {
            'total_entities': len(self.entities),
            'total_relationships': len(self.relationships),
            'total_chunks': len(self.chunks),
            'processed_files': len(self.processed_files),
            'entity_types': dict(entity_types),
            'relationship_types': dict(rel_types),
            'embedding_available': self.embedding_manager.is_available()
        }
    
    def export_json(self, output_path: Optional[str] = None) -> str:
        """Export the entire graph to JSON."""
        data = {
            'stats': self.get_stats(),
            'entities': [self._entity_to_dict(e) for e in self.entities.values()],
            'relationships': [self._relationship_to_dict(r) for r in self.relationships.values()]
        }
        
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            Path(output_path).write_text(json_str)
        
        return json_str
    
    def to_networkx(self) -> Any:
        """Export to NetworkX graph for external analysis."""
        return self._graph
    
    def clear(self):
        """Clear all data."""
        self.entities.clear()
        self.relationships.clear()
        self.chunks.clear()
        self.processed_files.clear()
        if self._graph:
            self._graph.clear()
        self._save()


# ============================================================================
# PAUL'S WORLD INTEGRATION
# ============================================================================

class PaulWorldGraphRAG:
    """
    Integration layer between GraphRAG and Paul's World.
    
    Allows Pauls to query the knowledge graph as part of their
    research and prediction workflow.
    """
    
    def __init__(self, graphrag: Optional[GraphRAG] = None):
        self.graphrag = graphrag or GraphRAG()
    
    async def research_topic(self, topic: str, paul_name: str = "Researcher") -> Dict[str, Any]:
        """
        Research a topic using GraphRAG.
        Returns structured information for Paul to use.
        """
        results = self.graphrag.query(topic)
        
        # Format for Paul consumption
        research_summary = {
            'topic': topic,
            'researcher': paul_name,
            'timestamp': datetime.now().isoformat(),
            'summary': results['summary'],
            'key_entities': results['entities'][:5],
            'key_relationships': results['relationships'][:5],
            'sources': list(set(c['source'] for c in results['chunks']))[:5],
            'insights': self._generate_insights(results)
        }
        
        return research_summary
    
    def _generate_insights(self, results: Dict) -> List[str]:
        """Generate insights from query results."""
        insights = []
        
        # Entity-based insights
        for entity in results['entities'][:3]:
            if entity.get('type') in ['person', 'organization']:
                insights.append(f"{entity['name']} is a key {entity['type']} in this space.")
        
        # Relationship insights
        for rel in results['relationships'][:3]:
            source = rel['source'].get('name', 'Unknown')
            target = rel['target'].get('name', 'Unknown')
            rel_type = rel['type'].replace('_', ' ')
            insights.append(f"{source} {rel_type} {target}.")
        
        # Path insights
        for path in results['paths']:
            path_str = ' → '.join([
                r['source']['name'] + f" ({r['type']})"
                for r in path['path']
            ]) + f" → {path['to']}"
            insights.append(f"Connection path: {path_str}")
        
        return insights
    
    async def ingest_paul_knowledge(self, paul_name: str, knowledge_content: str, topic: str):
        """Ingest knowledge learned by a Paul."""
        source = f"paul:{paul_name}"
        return await self.graphrag.ingest_text(knowledge_content, source=source)
    
    def get_related_predictions(self, market_question: str) -> List[Dict]:
        """
        Find related entities and past predictions for a market.
        """
        results = self.graphrag.query(market_question)
        
        return {
            'market': market_question,
            'related_entities': results['entities'],
            'context_chunks': results['chunks'][:3],
            'insights': self._generate_insights(results)
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

async def main():
    """CLI for GraphRAG."""
    import sys
    
    graphrag = GraphRAG()
    
    if len(sys.argv) < 2:
        print("GraphRAG - Knowledge Graph for Swimming Pauls")
        print()
        print("Commands:")
        print("  ingest <file/dir>  - Ingest document(s)")
        print("  query <question>   - Query the knowledge graph")
        print("  stats              - Show graph statistics")
        print("  export [path]      - Export graph to JSON")
        print("  clear              - Clear all data")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "ingest":
        if len(sys.argv) < 3:
            print("Usage: graphrag ingest <file_or_directory>")
            sys.exit(1)
        
        path = sys.argv[2]
        
        if Path(path).is_file():
            result = await graphrag.ingest_file(path)
            print(json.dumps(result, indent=2))
        elif Path(path).is_dir():
            results = await graphrag.ingest_directory(path)
            for r in results:
                print(f"{r['file']}: {r.get('status', 'unknown')}")
        else:
            print(f"Path not found: {path}")
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("Usage: graphrag query 'your question'")
            sys.exit(1)
        
        question = " ".join(sys.argv[2:])
        results = graphrag.query(question)
        
        print(f"\n🔍 Query: {results['question']}")
        print(f"📋 Summary: {results['summary']}\n")
        
        if results['entities']:
            print("📌 Entities:")
            for e in results['entities'][:5]:
                print(f"  • {e['name']} ({e['type']}) - confidence: {e['confidence']:.2f}")
        
        if results['relationships']:
            print("\n🔗 Relationships:")
            for r in results['relationships'][:5]:
                print(f"  • {r['source']['name']} → {r['type']} → {r['target']['name']}")
        
        if results['paths']:
            print("\n🛤️  Paths:")
            for p in results['paths']:
                print(f"  {p['from']} ↔ {p['to']}")
    
    elif command == "stats":
        stats = graphrag.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif command == "export":
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        json_data = graphrag.export_json(output_path)
        if output_path:
            print(f"Exported to {output_path}")
        else:
            print(json_data)
    
    elif command == "clear":
        confirm = input("Are you sure? This will delete all graph data. (yes/no): ")
        if confirm.lower() == 'yes':
            graphrag.clear()
            print("Graph data cleared.")
        else:
            print("Cancelled.")
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
