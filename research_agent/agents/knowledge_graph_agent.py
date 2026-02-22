"""
Knowledge Graph Agent
Identifies entities and relationships from paper chunks, builds/updates a knowledge graph.
"""
import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

SAMPLE_ENTITIES = [
    {"id": "e001", "type": "concept", "name": "Transformer", "frequency": 45},
    {"id": "e002", "type": "concept", "name": "Attention Mechanism", "frequency": 38},
    {"id": "e003", "type": "method", "name": "Self-Attention", "frequency": 32},
    {"id": "e004", "type": "concept", "name": "Retrieval Augmented Generation", "frequency": 28},
    {"id": "e005", "type": "metric", "name": "BLEU Score", "frequency": 22},
    {"id": "e006", "type": "dataset", "name": "SQuAD", "frequency": 18},
    {"id": "e007", "type": "model", "name": "BERT", "frequency": 41},
    {"id": "e008", "type": "model", "name": "GPT-4", "frequency": 29},
    {"id": "e009", "type": "concept", "name": "Dense Retrieval", "frequency": 24},
    {"id": "e010", "type": "concept", "name": "Vector Embeddings", "frequency": 35},
]

SAMPLE_RELATIONS = [
    {"from": "e001", "to": "e002", "relation": "uses", "weight": 0.95},
    {"from": "e002", "to": "e003", "relation": "is_type_of", "weight": 0.98},
    {"from": "e004", "to": "e009", "relation": "depends_on", "weight": 0.87},
    {"from": "e009", "to": "e010", "relation": "uses", "weight": 0.92},
    {"from": "e007", "to": "e001", "relation": "based_on", "weight": 0.99},
    {"from": "e008", "to": "e001", "relation": "based_on", "weight": 0.99},
    {"from": "e004", "to": "e007", "relation": "leverages", "weight": 0.75},
]


class KnowledgeGraphAgent:
    """
    Agent that identifies entities and relationships from paper chunks,
    builds and updates a knowledge graph stored in Qdrant vector database.
    Implements UC-2: Cross-Institutional Knowledge Graph Federation.
    """

    def __init__(self):
        self.name = "KnowledgeGraphAgent"
        self.description = "Identify entities and relationships from paper chunks, build/update a knowledge graph"
        self.status = "idle"
        self.graphs = {}  # project_id -> graph data
        self.entity_overlap_ratio = 0.0  # UC-2 large-scale signal

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution entry point."""
        action = params.get("action", "")
        self.status = "active"

        try:
            if action == "initialize_graph":
                result = await self.initialize_graph(params)
            elif action == "extract_knowledge":
                result = await self.extract_knowledge(params)
            elif action == "query_graph":
                result = await self.query_graph(params)
            elif action == "merge_graphs":
                result = await self.merge_graphs(params)
            elif action == "get_entities":
                result = await self.get_entities(params)
            elif action == "get_relations":
                result = await self.get_relations(params)
            elif action == "build_semantic_graph":
                result = await self.build_semantic_graph(params)
            elif action == "get_status":
                result = {"status": self.status, "agent": self.name, "graphs": len(self.graphs)}
            else:
                result = {"error": f"Unknown action: {action}", "status": "error"}

            self.status = "idle"
            return result

        except Exception as e:
            self.status = "error"
            logger.error(f"KnowledgeGraphAgent error: {e}")
            return {"error": str(e), "status": "error"}

    async def initialize_graph(self, params: Dict) -> Dict:
        """Initialize a new knowledge graph for a project."""
        project_name = params.get("project_name", "unnamed_project")
        project_id = params.get("project_id", f"proj_{len(self.graphs) + 1}")

        await asyncio.sleep(0.3)

        graph_id = f"graph_{project_id}"
        self.graphs[graph_id] = {
            "project_name": project_name,
            "entities": [],
            "relations": [],
            "created_at": "2025-01-01T00:00:00Z",
            "node_count": 0,
            "edge_count": 0
        }

        return {
            "status": "success",
            "agent": self.name,
            "action": "initialize_graph",
            "graph_id": graph_id,
            "project_name": project_name,
            "collection": f"qdrant_{graph_id}",
            "message": f"Initialized knowledge graph for project: {project_name}"
        }

    async def extract_knowledge(self, params: Dict) -> Dict:
        """Extract entity-relation triples from document chunks."""
        chunks = params.get("chunks", [])
        doc_id = params.get("doc_id", "unknown")
        graph_id = params.get("graph_id", "default")

        await asyncio.sleep(0.5)

        # Return sample extracted entities and relations
        entities = SAMPLE_ENTITIES[:7]
        relations = SAMPLE_RELATIONS[:5]

        # Update graph if it exists
        if graph_id in self.graphs:
            self.graphs[graph_id]["entities"].extend(entities)
            self.graphs[graph_id]["relations"].extend(relations)
            self.graphs[graph_id]["node_count"] = len(entities)
            self.graphs[graph_id]["edge_count"] = len(relations)

        return {
            "status": "success",
            "agent": self.name,
            "action": "extract_knowledge",
            "doc_id": doc_id,
            "entities_extracted": len(entities),
            "relations_extracted": len(relations),
            "entities": entities,
            "relations": relations,
            "message": f"Extracted {len(entities)} entities and {len(relations)} relations from document"
        }

    async def query_graph(self, params: Dict) -> Dict:
        """Semantic search over the knowledge graph."""
        query = params.get("query", "")
        graph_id = params.get("graph_id", "default")
        top_k = params.get("top_k", 5)
        cross_institutional = params.get("cross_institutional", False)

        await asyncio.sleep(0.4)

        # Return relevant entities based on query
        relevant_entities = SAMPLE_ENTITIES[:top_k]
        relevant_relations = SAMPLE_RELATIONS[:3]

        # UC-2: Track entity overlap ratio for cross-institutional queries
        if cross_institutional:
            self.entity_overlap_ratio = 0.67  # Simulated overlap

        return {
            "status": "success",
            "agent": self.name,
            "action": "query_graph",
            "query": query,
            "results": relevant_entities,
            "related_concepts": relevant_relations,
            "entity_overlap_ratio": self.entity_overlap_ratio if cross_institutional else None,
            "message": f"Found {len(relevant_entities)} relevant nodes for query: '{query}'"
        }

    async def merge_graphs(self, params: Dict) -> Dict:
        """Merge multiple knowledge graphs (for federated knowledge, UC-2)."""
        source_graph_ids = params.get("source_graph_ids", [])
        target_graph_id = params.get("target_graph_id", "merged_graph")

        await asyncio.sleep(0.6)

        # Simulate merge with overlap detection
        all_entities = SAMPLE_ENTITIES.copy()
        all_relations = SAMPLE_RELATIONS.copy()
        overlap_count = 4  # Simulated overlapping entities

        self.entity_overlap_ratio = overlap_count / len(all_entities) if all_entities else 0

        return {
            "status": "success",
            "agent": self.name,
            "action": "merge_graphs",
            "sources_merged": len(source_graph_ids),
            "target_graph_id": target_graph_id,
            "total_entities": len(all_entities),
            "total_relations": len(all_relations),
            "overlap_count": overlap_count,
            "entity_overlap_ratio": round(self.entity_overlap_ratio, 3),
            "contradictions_found": 2,
            "message": f"Merged {len(source_graph_ids)} knowledge graphs, overlap ratio: {self.entity_overlap_ratio:.1%}"
        }

    async def get_entities(self, params: Dict) -> Dict:
        """Get all entities in a graph."""
        graph_id = params.get("graph_id", "default")
        return {
            "status": "success",
            "agent": self.name,
            "entities": SAMPLE_ENTITIES,
            "count": len(SAMPLE_ENTITIES)
        }

    async def get_relations(self, params: Dict) -> Dict:
        """Get all relations in a graph."""
        graph_id = params.get("graph_id", "default")
        return {
            "status": "success",
            "agent": self.name,
            "relations": SAMPLE_RELATIONS,
            "count": len(SAMPLE_RELATIONS)
        }

    async def build_semantic_graph(self, params: Dict) -> Dict:
        """Build a semantic graph from Word2Vec embeddings (for cross-institutional alignment, UC-2)."""
        documents = params.get("documents", [])
        await asyncio.sleep(0.5)

        return {
            "status": "success",
            "agent": self.name,
            "action": "build_semantic_graph",
            "nodes": len(SAMPLE_ENTITIES),
            "edges": len(SAMPLE_RELATIONS),
            "embedding_model": "word2vec-research-v1",
            "alignment_score": 0.84,
            "message": "Semantic graph built using Word2Vec embeddings for cross-institutional alignment"
        }
