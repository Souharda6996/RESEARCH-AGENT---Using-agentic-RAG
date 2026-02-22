"""
Literature Review Agent
Formulates search queries, retrieves relevant papers, and filters by relevance.
"""
import json
import re
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

MOCK_PAPERS = [
    {
        "id": "paper_001",
        "title": "Attention Is All You Need",
        "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."],
        "year": 2017,
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "venue": "NeurIPS 2017",
        "citations": 95000,
        "relevance_score": 0.97,
        "url": "https://arxiv.org/abs/1706.03762"
    },
    {
        "id": "paper_002",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Devlin, J.", "Chang, M.", "Lee, K.", "Toutanova, K."],
        "year": 2019,
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers.",
        "venue": "NAACL 2019",
        "citations": 73000,
        "relevance_score": 0.94,
        "url": "https://arxiv.org/abs/1810.04805"
    },
    {
        "id": "paper_003",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": ["Lewis, P.", "Perez, E.", "Piktus, A."],
        "year": 2020,
        "abstract": "Large pre-trained language models store knowledge in their parameters and can answer questions based on this knowledge. However, their ability to access and precisely manipulate knowledge is limited.",
        "venue": "NeurIPS 2020",
        "citations": 18000,
        "relevance_score": 0.99,
        "url": "https://arxiv.org/abs/2005.11401"
    },
    {
        "id": "paper_004",
        "title": "GPT-4 Technical Report",
        "authors": ["OpenAI"],
        "year": 2023,
        "abstract": "We report the development of GPT-4, a large-scale, multimodal model which can accept image and text inputs and produce text outputs.",
        "venue": "arXiv 2023",
        "citations": 12000,
        "relevance_score": 0.88,
        "url": "https://arxiv.org/abs/2303.08774"
    },
    {
        "id": "paper_005",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": ["Wei, J.", "Wang, X.", "Schuurmans, D."],
        "year": 2022,
        "abstract": "We explore how generating a chain of thought—a series of intermediate reasoning steps—significantly improves the ability of large language models to perform complex reasoning.",
        "venue": "NeurIPS 2022",
        "citations": 9500,
        "relevance_score": 0.85,
        "url": "https://arxiv.org/abs/2201.11903"
    }
]


class LiteratureReviewAgent:
    """
    Agent responsible for formulating search queries, retrieving relevant papers,
    and filtering by relevance score. Implements UC-1: Distributed Literature Triage.
    """

    def __init__(self):
        self.name = "LiteratureReviewAgent"
        self.description = "Formulate search queries, retrieve relevant papers, filter by relevance"
        self.status = "idle"
        self.filter_acceptance_rate = []  # Tracks per-peer filter acceptance for UC-1

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution entry point."""
        action = params.get("action", "")
        self.status = "active"

        try:
            if action == "formulate_search_query":
                result = await self.formulate_search_query(params)
            elif action == "retrieve_papers":
                result = await self.retrieve_papers(params)
            elif action == "filter_papers":
                result = await self.filter_papers(params)
            elif action == "analyze_paper":
                result = await self.analyze_paper(params)
            elif action == "synthesize_findings":
                result = await self.synthesize_findings(params)
            elif action == "get_status":
                result = {"status": self.status, "agent": self.name}
            else:
                result = {"error": f"Unknown action: {action}", "status": "error"}

            self.status = "idle"
            return result

        except Exception as e:
            self.status = "error"
            logger.error(f"LiteratureReviewAgent error: {e}")
            return {"error": str(e), "status": "error"}

    async def formulate_search_query(self, params: Dict) -> Dict:
        """Expand a research topic into structured search queries."""
        topic = params.get("topic", "")
        research_goals = params.get("research_goals", [])

        await asyncio.sleep(0.3)  # Simulate processing

        # Generate structured queries
        queries = [
            f"{topic} survey",
            f"{topic} state of the art",
            f"{topic} deep learning approaches",
        ]
        if research_goals:
            for goal in research_goals[:2]:
                queries.append(f"{topic} {goal}")

        return {
            "status": "success",
            "agent": self.name,
            "action": "formulate_search_query",
            "queries": queries,
            "topic": topic,
            "expanded_terms": self._expand_terms(topic),
            "message": f"Generated {len(queries)} structured search queries for topic: {topic}"
        }

    async def retrieve_papers(self, params: Dict) -> Dict:
        """Retrieve relevant papers based on search queries."""
        queries = params.get("queries", [])
        max_results = params.get("max_results", 20)
        topic = params.get("topic", "")

        await asyncio.sleep(0.5)  # Simulate retrieval

        # Filter mock papers by relevance to the query
        papers = MOCK_PAPERS.copy()

        return {
            "status": "success",
            "agent": self.name,
            "action": "retrieve_papers",
            "papers_found": len(papers),
            "papers": papers[:max_results],
            "queries_used": queries,
            "message": f"Retrieved {len(papers)} papers from literature database"
        }

    async def filter_papers(self, params: Dict) -> Dict:
        """Filter papers by relevance threshold."""
        papers = params.get("papers", MOCK_PAPERS)
        threshold = params.get("relevance_threshold", 0.80)
        peer_id = params.get("peer_id", "default")

        await asyncio.sleep(0.2)

        filtered = [p for p in papers if p.get("relevance_score", 0) >= threshold]
        acceptance_rate = len(filtered) / len(papers) if papers else 0

        # Track peer filter acceptance rate for UC-1 large-scale signal
        self.filter_acceptance_rate.append({
            "peer_id": peer_id,
            "rate": acceptance_rate,
            "threshold": threshold
        })

        return {
            "status": "success",
            "agent": self.name,
            "action": "filter_papers",
            "total_papers": len(papers),
            "filtered_papers": len(filtered),
            "acceptance_rate": round(acceptance_rate, 3),
            "papers": filtered,
            "message": f"Filtered to {len(filtered)} papers (acceptance rate: {acceptance_rate:.1%})"
        }

    async def analyze_paper(self, params: Dict) -> Dict:
        """Analyze a single paper for key contributions and relevance."""
        paper = params.get("paper", {})
        topic = params.get("topic", "")

        await asyncio.sleep(0.3)

        title = paper.get("title", "Unknown")
        abstract = paper.get("abstract", "")

        return {
            "status": "success",
            "agent": self.name,
            "action": "analyze_paper",
            "paper_title": title,
            "key_contributions": [
                "Introduces novel methodology for the field",
                "Empirically validates on benchmark datasets",
                "Sets new state-of-the-art performance"
            ],
            "relevance_to_topic": 0.92,
            "recommended_for_inclusion": True,
            "message": f"Analyzed paper: {title}"
        }

    async def synthesize_findings(self, params: Dict) -> Dict:
        """Synthesize findings from multiple papers."""
        papers = params.get("papers", [])
        topic = params.get("topic", "")

        await asyncio.sleep(0.5)

        return {
            "status": "success",
            "agent": self.name,
            "action": "synthesize_findings",
            "papers_synthesized": len(papers) or len(MOCK_PAPERS),
            "key_themes": [
                "Transformer architectures dominate the field",
                "Pre-training + fine-tuning is the dominant paradigm",
                "Scale (model size, data) continues to drive improvements",
                "Retrieval-augmented approaches show strong performance"
            ],
            "research_gaps": [
                "Interpretability of large models remains challenging",
                "Efficiency for edge deployment is an open problem"
            ],
            "message": f"Synthesized findings from {len(papers) or len(MOCK_PAPERS)} papers on {topic}"
        }

    def _expand_terms(self, topic: str) -> List[str]:
        """Expand a topic into related search terms."""
        base_terms = topic.lower().split()
        expansions = []
        term_map = {
            "ai": ["artificial intelligence", "machine learning", "deep learning"],
            "nlp": ["natural language processing", "text processing", "language models"],
            "rag": ["retrieval augmented generation", "knowledge retrieval", "document QA"],
            "transformer": ["attention mechanism", "BERT", "GPT", "encoder decoder"],
        }
        for term in base_terms:
            if term in term_map:
                expansions.extend(term_map[term])
        return expansions or [f"{topic} methods", f"{topic} applications"]
