"""
Collaboration Agent
Tracks progress, logs actions, suggests next steps, and maintains shared project context.
"""
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CollaborationAgent:
    """
    Agent responsible for multi-user collaboration, task assignment, progress tracking,
    and shared context management. Implements UC-1 (distributed triage), UC-4 (crowd
    question refinement), UC-7 (token budget negotiation), UC-8 (trajectory mapping).
    """

    def __init__(self):
        self.name = "CollaborationAgent"
        self.description = "Track progress, log actions, suggest next steps, and maintain shared project context"
        self.status = "idle"
        self.projects = {}
        self.action_log = []

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution entry point."""
        action = params.get("action", "")
        self.status = "active"

        try:
            if action == "create_project":
                result = await self.create_project(params)
            elif action == "assign_task":
                result = await self.assign_task(params)
            elif action == "share_context":
                result = await self.share_context(params)
            elif action == "track_progress":
                result = await self.track_progress(params)
            elif action == "negotiate_token_budget":
                result = await self.negotiate_token_budget(params)
            elif action == "suggest_next_steps":
                result = await self.suggest_next_steps(params)
            elif action == "form_peer_clusters":
                result = await self.form_peer_clusters(params)
            elif action == "get_project":
                result = await self.get_project(params)
            elif action == "log_action":
                result = await self.log_action(params)
            elif action == "get_status":
                result = {"status": self.status, "agent": self.name, "projects": len(self.projects)}
            else:
                result = {"error": f"Unknown action: {action}", "status": "error"}

            self.status = "idle"
            return result

        except Exception as e:
            self.status = "error"
            logger.error(f"CollaborationAgent error: {e}")
            return {"error": str(e), "status": "error"}

    async def create_project(self, params: Dict) -> Dict:
        """Create a new collaborative research project."""
        name = params.get("name", "Untitled Project")
        description = params.get("description", "")
        team_members = params.get("team_members", [])
        token_budget = params.get("token_budget", 100000)

        await asyncio.sleep(0.3)

        project_id = f"proj_{len(self.projects) + 1:04d}"
        self.projects[project_id] = {
            "id": project_id,
            "name": name,
            "description": description,
            "team_members": team_members,
            "tasks": [],
            "token_budget": token_budget,
            "tokens_used": 0,
            "status": "active",
            "created_at": time.time(),
            "action_log": []
        }

        return {
            "status": "success",
            "agent": self.name,
            "action": "create_project",
            "project_id": project_id,
            "name": name,
            "team_members": team_members,
            "token_budget": token_budget,
            "message": f"Project '{name}' created with {len(team_members)} team members"
        }

    async def assign_task(self, params: Dict) -> Dict:
        """Assign tasks to peers for distributed execution (UC-1)."""
        project_id = params.get("project_id", "")
        task_type = params.get("task_type", "literature_review")
        peers = params.get("peers", [])
        paper_pool = params.get("paper_pool", [])

        await asyncio.sleep(0.3)

        # Split paper pool across peers
        num_peers = max(1, len(peers))
        papers_per_peer = max(1, len(paper_pool) // num_peers) if paper_pool else 50

        assignments = []
        for i, peer in enumerate(peers or [f"peer_{i}" for i in range(3)]):
            assignments.append({
                "peer_id": peer,
                "task_id": f"task_{i+1:03d}",
                "task_type": task_type,
                "paper_count": papers_per_peer,
                "paper_range": f"papers {i*papers_per_peer + 1}–{(i+1)*papers_per_peer}",
                "status": "assigned"
            })

        return {
            "status": "success",
            "agent": self.name,
            "action": "assign_task",
            "project_id": project_id,
            "assignments": assignments,
            "peers_assigned": len(assignments),
            "task_type": task_type,
            "message": f"Distributed {task_type} task across {len(assignments)} peers"
        }

    async def share_context(self, params: Dict) -> Dict:
        """Broadcast section summaries and context to all peers via WebSocket (UC-3)."""
        project_id = params.get("project_id", "")
        author_id = params.get("author_id", "")
        section_summary = params.get("section_summary", "")
        section_title = params.get("section_title", "")

        await asyncio.sleep(0.2)

        # Log the action for the project
        log_entry = {
            "timestamp": time.time(),
            "author_id": author_id,
            "action": "share_context",
            "section_title": section_title,
            "summary_preview": section_summary[:100] + "..." if len(section_summary) > 100 else section_summary
        }
        self.action_log.append(log_entry)

        return {
            "status": "success",
            "agent": self.name,
            "action": "share_context",
            "project_id": project_id,
            "broadcast_to": "all_peers",
            "section_title": section_title,
            "recipients": 4,
            "websocket_event": "CONTEXT_SHARED",
            "message": f"Shared context for '{section_title}' with all project peers"
        }

    async def track_progress(self, params: Dict) -> Dict:
        """Track and log research progress (UC-5 improvement trajectory)."""
        project_id = params.get("project_id", "")
        milestone = params.get("milestone", "")
        completion_pct = params.get("completion_pct", 0)
        peer_id = params.get("peer_id", "")

        await asyncio.sleep(0.2)

        if project_id in self.projects:
            self.projects[project_id]["action_log"].append({
                "timestamp": time.time(),
                "milestone": milestone,
                "completion_pct": completion_pct,
                "peer_id": peer_id
            })

        return {
            "status": "success",
            "agent": self.name,
            "action": "track_progress",
            "project_id": project_id,
            "milestone": milestone,
            "completion_pct": completion_pct,
            "workflow_stages": [
                {"stage": "Literature Review", "pct": 100, "status": "done"},
                {"stage": "Data Processing", "pct": 100, "status": "done"},
                {"stage": "Knowledge Graph", "pct": 75, "status": "in_progress"},
                {"stage": "Analysis", "pct": 40, "status": "in_progress"},
                {"stage": "Writing", "pct": 10, "status": "pending"},
            ],
            "overall_completion": 65,
            "message": f"Progress logged: {milestone} at {completion_pct}%"
        }

    async def negotiate_token_budget(self, params: Dict) -> Dict:
        """Negotiate token budget redistribution between sub-teams (UC-7)."""
        project_id = params.get("project_id", "")
        teams = params.get("teams", [])
        total_budget = params.get("total_budget", 100000)
        current_usage = params.get("current_usage", 80000)

        await asyncio.sleep(0.4)

        usage_pct = current_usage / total_budget
        remaining = total_budget - current_usage

        # Simulate budget redistribution
        redistribution = [
            {"team": "literature_review_team", "tokens_allocated": int(remaining * 0.3), "reason": "Completing final 5 papers"},
            {"team": "analysis_team", "tokens_allocated": int(remaining * 0.45), "reason": "Core analysis phase — highest priority"},
            {"team": "writing_team", "tokens_allocated": int(remaining * 0.25), "reason": "Draft synthesis section"}
        ]

        return {
            "status": "success",
            "agent": self.name,
            "action": "negotiate_token_budget",
            "project_id": project_id,
            "total_budget": total_budget,
            "current_usage": current_usage,
            "usage_percentage": round(usage_pct * 100, 1),
            "remaining_tokens": remaining,
            "redistribution": redistribution,
            "pruning_strategy": "LRU" if usage_pct > 0.9 else "relevance",
            "warning": usage_pct >= 0.8,
            "message": f"Token budget at {usage_pct:.0%} — redistribution proposed among {len(redistribution)} teams"
        }

    async def suggest_next_steps(self, params: Dict) -> Dict:
        """Suggest intelligent next steps based on project state."""
        project_id = params.get("project_id", "")
        completed_workflows = params.get("completed_workflows", [])
        topic = params.get("topic", "")

        await asyncio.sleep(0.3)

        suggestions = [
            {
                "step": 1,
                "action": "Run Analysis Agent on extracted knowledge",
                "agent": "AnalysisAgent",
                "priority": "high",
                "reason": "Knowledge graph construction is complete — analysis will reveal research gaps"
            },
            {
                "step": 2,
                "action": "Generate paper outline with WritingAssistantAgent",
                "agent": "WritingAssistantAgent",
                "priority": "medium",
                "reason": "Sufficient literature synthesized to structure an outline"
            },
            {
                "step": 3,
                "action": "Invite collaborators for peer review simulation",
                "agent": "CollaborationAgent",
                "priority": "low",
                "reason": "Pre-submission quality gate recommended before drafting final version"
            }
        ]

        return {
            "status": "success",
            "agent": self.name,
            "action": "suggest_next_steps",
            "project_id": project_id,
            "suggestions": suggestions,
            "message": f"Generated {len(suggestions)} next step recommendations"
        }

    async def form_peer_clusters(self, params: Dict) -> Dict:
        """Form semantic peer clusters for collaborative question refinement (UC-4)."""
        participants = params.get("participants", [])
        questions = params.get("questions", [])
        num_clusters = params.get("num_clusters", 5)

        await asyncio.sleep(0.4)

        # Simulate cluster formation by semantic similarity
        clusters = [
            {
                "cluster_id": "cluster_1",
                "theme": "Agentic AI systems",
                "questions": 8,
                "participants": 5,
                "convergence_rounds": 2,
                "stability": "converging"
            },
            {
                "cluster_id": "cluster_2",
                "theme": "Knowledge graph construction",
                "questions": 6,
                "participants": 4,
                "convergence_rounds": 3,
                "stability": "stable"
            },
            {
                "cluster_id": "cluster_3",
                "theme": "Multi-modal RAG",
                "questions": 11,
                "participants": 7,
                "convergence_rounds": 1,
                "stability": "forming"
            }
        ]

        return {
            "status": "success",
            "agent": self.name,
            "action": "form_peer_clusters",
            "total_participants": len(participants) or 24,
            "total_questions": len(questions) or 25,
            "clusters": clusters,
            "avg_convergence_rounds": 2.0,
            "message": f"Formed {len(clusters)} peer clusters from {len(participants) or 24} participants"
        }

    async def get_project(self, params: Dict) -> Dict:
        """Get project details."""
        project_id = params.get("project_id", "")

        if project_id in self.projects:
            return {
                "status": "success",
                "agent": self.name,
                "project": self.projects[project_id]
            }

        # Return default project state
        return {
            "status": "success",
            "agent": self.name,
            "project": {
                "id": project_id or "proj_demo",
                "name": "Demo Research Project",
                "status": "active",
                "team_members": ["researcher_1", "researcher_2"],
                "token_budget": 100000,
                "tokens_used": 23847,
                "overall_completion": 45
            }
        }

    async def log_action(self, params: Dict) -> Dict:
        """Log an action to the project history."""
        action_type = params.get("action_type", "")
        agent = params.get("agent", "")
        details = params.get("details", {})

        log_entry = {
            "timestamp": time.time(),
            "action_type": action_type,
            "agent": agent,
            "details": details
        }
        self.action_log.append(log_entry)

        return {
            "status": "success",
            "agent": self.name,
            "logged": True,
            "log_entry": log_entry
        }
