"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    BookOpen, Database, Network, BarChart2, PenTool, Users,
    ChevronRight, Zap, GitBranch, Info, Activity
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Node config ──────────────────────────────────────────────────────────────
interface Node {
    id: string;
    label: string;
    sublabel: string;
    x: number;
    y: number;
    color: string;
    glow: string;
    icon: React.ElementType;
    agent?: string;
    tooltip: string;
    details: string[];
}

interface Edge {
    from: string;
    to: string;
    label?: string;
}

const NODES: Node[] = [
    {
        id: "input",
        label: "Research Query",
        sublabel: "User Input",
        x: 340, y: 24,
        color: "#6366f1",
        glow: "rgba(99,102,241,0.35)",
        icon: GitBranch,
        tooltip: "The user's complex research question enters the pipeline",
        details: [
            "Natural language query",
            "Semantic intent detection",
            "Research context extraction"
        ]
    },
    {
        id: "literature",
        label: "Literature Review",
        sublabel: "LiteratureReviewAgent",
        x: 100, y: 150,
        color: "#22d3ee",
        glow: "rgba(34,211,238,0.35)",
        icon: BookOpen,
        agent: "LiteratureReviewAgent",
        tooltip: "Searches and filters academic literature",
        details: [
            "Query expansion & formulation",
            "Dense + BM25 retrieval",
            "Relevance filtering (threshold 0.85)",
            "Paper analysis & synthesis"
        ]
    },
    {
        id: "data",
        label: "Data Processing",
        sublabel: "DataProcessingAgent",
        x: 340, y: 190,
        color: "#a78bfa",
        glow: "rgba(167,139,250,0.35)",
        icon: Database,
        agent: "DataProcessingAgent",
        tooltip: "Ingests, extracts, and chunks document content",
        details: [
            "PDF/DOCX text extraction",
            "512-token semantic chunking",
            "64-token overlap for context",
            "BM25 + vector indices"
        ]
    },
    {
        id: "kg",
        label: "Knowledge Graph",
        sublabel: "KnowledgeGraphAgent",
        x: 580, y: 150,
        color: "#34d399",
        glow: "rgba(52,211,153,0.35)",
        icon: Network,
        agent: "KnowledgeGraphAgent",
        tooltip: "Builds and queries an entity-relation knowledge graph",
        details: [
            "Named entity recognition",
            "Relation extraction",
            "Qdrant vector storage",
            "Semantic graph queries",
            "Cross-institutional federation (UC-2)"
        ]
    },
    {
        id: "analysis",
        label: "Analysis",
        sublabel: "AnalysisAgent",
        x: 180, y: 320,
        color: "#f59e0b",
        glow: "rgba(245,158,11,0.35)",
        icon: BarChart2,
        agent: "AnalysisAgent",
        tooltip: "Statistical analysis, trend detection, and conflict resolution",
        details: [
            "Publication trend analysis",
            "Statistical significance tests",
            "Conflict detection (UC-3)",
            "Research gap identification",
            "Citation network analysis (UC-6)"
        ]
    },
    {
        id: "writing",
        label: "Writing Assistant",
        sublabel: "WritingAssistantAgent",
        x: 500, y: 320,
        color: "#f472b6",
        glow: "rgba(244,114,182,0.35)",
        icon: PenTool,
        agent: "WritingAssistantAgent",
        tooltip: "Synthesizes findings and generates cited answers",
        details: [
            "Literature synthesis",
            "Outline generation",
            "Section drafting",
            "Abstract writing",
            "Conflict reconciliation (UC-3)"
        ]
    },
    {
        id: "collab",
        label: "Collaboration",
        sublabel: "CollaborationAgent",
        x: 340, y: 440,
        color: "#6366f1",
        glow: "rgba(99,102,241,0.35)",
        icon: Users,
        agent: "CollaborationAgent",
        tooltip: "Manages multi-user collaboration, token budgets, and context",
        details: [
            "Task assignment (UC-1)",
            "Token budget negotiation (UC-7)",
            "Shared context broadcast",
            "Progress tracking (UC-5)",
            "Research trajectory reports (UC-8)"
        ]
    },
    {
        id: "output",
        label: "Research Answer",
        sublabel: "Cited Response",
        x: 340, y: 560,
        color: "#22d3ee",
        glow: "rgba(34,211,238,0.35)",
        icon: Zap,
        tooltip: "Final answer with citations, sources, and confidence scores",
        details: [
            "Markdown-formatted answer",
            "Academic citations",
            "Source relevance scores",
            "Confidence estimation",
            "Agent pipeline trace"
        ]
    }
];

const EDGES: Edge[] = [
    { from: "input", to: "literature", label: "search" },
    { from: "input", to: "data", label: "ingest" },
    { from: "input", to: "kg", label: "context" },
    { from: "literature", to: "analysis" },
    { from: "data", to: "kg" },
    { from: "kg", to: "writing" },
    { from: "analysis", to: "writing" },
    { from: "literature", to: "collab" },
    { from: "writing", to: "collab" },
    { from: "collab", to: "output" },
];

const SVG_W = 680;
const SVG_H = 630;
const NODE_W = 130;
const NODE_H = 52;

function getCenter(node: Node) {
    return { x: node.x + NODE_W / 2, y: node.y + NODE_H / 2 };
}

// ─── Main Page ─────────────────────────────────────────────────────────────────
export default function WorkflowPage() {
    const [hovered, setHovered] = useState<string | null>(null);
    const [agentStatuses, setAgentStatuses] = useState<Record<string, string>>({});
    const [apiConnected, setApiConnected] = useState(false);

    // Poll agent statuses
    useEffect(() => {
        const fetchStatuses = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/health`);
                if (res.ok) {
                    const data = await res.json();
                    setAgentStatuses(data.agents || {});
                    setApiConnected(true);
                }
            } catch {
                setApiConnected(false);
            }
        };
        fetchStatuses();
        const interval = setInterval(fetchStatuses, 5000);
        return () => clearInterval(interval);
    }, []);

    const hoveredNode = hovered ? NODES.find((n) => n.id === hovered) : null;

    return (
        <div className="min-h-full" style={{ background: "var(--bg-primary)" }}>
            <div className="max-w-6xl mx-auto px-6 py-12">

                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-semibold mb-4"
                        style={{ background: "rgba(99,102,241,0.12)", color: "#a78bfa" }}>
                        <Activity className="w-4 h-4" />
                        6-Agent Pipeline
                    </div>
                    <h1 className="text-3xl font-bold mb-3" style={{ fontFamily: "var(--font-poppins)", color: "var(--text-primary)" }}>
                        Agentic RAG Workflow
                    </h1>
                    <p className="text-base max-w-xl mx-auto" style={{ color: "var(--text-secondary)" }}>
                        Hover over any agent node to see its role in the pipeline. The 6 specialized agents cooperate to deliver accurate, cited research answers.
                    </p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* SVG diagram */}
                    <div className="lg:col-span-2">
                        <div className="glass rounded-2xl p-6 border" style={{ borderColor: "var(--border-card)" }}>
                            <svg
                                viewBox={`0 0 ${SVG_W} ${SVG_H}`}
                                className="w-full"
                                style={{ maxHeight: 520 }}
                            >
                                <defs>
                                    <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                                        <path d="M0,0 L0,6 L8,3 Z" fill="rgba(255,255,255,0.2)" />
                                    </marker>
                                    {NODES.map((node) => (
                                        <filter key={`glow-${node.id}`} id={`glow-${node.id}`}>
                                            <feGaussianBlur stdDeviation="6" result="coloredBlur" />
                                            <feMerge>
                                                <feMergeNode in="coloredBlur" />
                                                <feMergeNode in="SourceGraphic" />
                                            </feMerge>
                                        </filter>
                                    ))}
                                </defs>

                                {/* Edges */}
                                {EDGES.map((edge, i) => {
                                    const fromNode = NODES.find((n) => n.id === edge.from)!;
                                    const toNode = NODES.find((n) => n.id === edge.to)!;
                                    const from = getCenter(fromNode);
                                    const to = getCenter(toNode);
                                    const isActive = hovered === edge.from || hovered === edge.to;
                                    return (
                                        <g key={i}>
                                            <line
                                                x1={from.x} y1={from.y} x2={to.x} y2={to.y}
                                                stroke={isActive ? fromNode.color : "rgba(255,255,255,0.12)"}
                                                strokeWidth={isActive ? 2 : 1.5}
                                                strokeDasharray={isActive ? "none" : "4 3"}
                                                markerEnd="url(#arrow)"
                                                style={{ transition: "stroke 0.2s, stroke-width 0.2s" }}
                                            />
                                        </g>
                                    );
                                })}

                                {/* Nodes */}
                                {NODES.map((node) => {
                                    const Icon = node.icon;
                                    const isHov = hovered === node.id;
                                    const agentStatus = node.agent ? agentStatuses[node.agent] : null;
                                    return (
                                        <g
                                            key={node.id}
                                            transform={`translate(${node.x}, ${node.y})`}
                                            onMouseEnter={() => setHovered(node.id)}
                                            onMouseLeave={() => setHovered(null)}
                                            style={{ cursor: "pointer" }}
                                        >
                                            {/* Glow */}
                                            {isHov && (
                                                <rect
                                                    x={-6} y={-6}
                                                    width={NODE_W + 12}
                                                    height={NODE_H + 12}
                                                    rx={14}
                                                    fill={node.glow}
                                                    opacity={0.5}
                                                    filter={`url(#glow-${node.id})`}
                                                />
                                            )}
                                            {/* Rect */}
                                            <rect
                                                width={NODE_W}
                                                height={NODE_H}
                                                rx={10}
                                                fill={isHov ? `${node.color}22` : "rgba(15,18,30,0.85)"}
                                                stroke={isHov ? node.color : "rgba(255,255,255,0.1)"}
                                                strokeWidth={isHov ? 1.5 : 1}
                                                style={{ transition: "all 0.2s" }}
                                            />
                                            {/* Icon */}
                                            <foreignObject x={10} y={10} width={22} height={22}>
                                                <div className="w-full h-full flex items-center justify-center">
                                                    <div
                                                        className="w-7 h-7 rounded-md flex items-center justify-center"
                                                        style={{ background: `${node.color}25` }}
                                                    >
                                                        {/* Icon rendered via CSS class */}
                                                    </div>
                                                </div>
                                            </foreignObject>
                                            {/* Label */}
                                            <text
                                                x={NODE_W / 2}
                                                y={22}
                                                textAnchor="middle"
                                                fontSize={11}
                                                fontWeight="600"
                                                fill={isHov ? node.color : "#e8eaf6"}
                                            >
                                                {node.label}
                                            </text>
                                            <text
                                                x={NODE_W / 2}
                                                y={37}
                                                textAnchor="middle"
                                                fontSize={9}
                                                fill="rgba(200,210,230,0.5)"
                                            >
                                                {node.sublabel}
                                            </text>
                                            {/* Status dot */}
                                            {agentStatus && (
                                                <circle
                                                    cx={NODE_W - 8}
                                                    cy={8}
                                                    r={4}
                                                    fill={agentStatus === "idle" ? "#34d399" : agentStatus === "active" ? "#f59e0b" : "#f87171"}
                                                />
                                            )}
                                        </g>
                                    );
                                })}
                            </svg>
                        </div>
                    </div>

                    {/* Info panel */}
                    <div className="space-y-4">

                        {/* API status */}
                        <div
                            className="glass rounded-xl px-4 py-3 border flex items-center gap-3"
                            style={{ borderColor: apiConnected ? "rgba(52,211,153,0.3)" : "var(--border-card)" }}
                        >
                            <div
                                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                                style={{ background: apiConnected ? "#34d399" : "#64748b" }}
                            />
                            <div>
                                <p className="text-xs font-semibold" style={{ color: apiConnected ? "#34d399" : "var(--text-secondary)" }}>
                                    {apiConnected ? "Backend Connected" : "Backend Offline"}
                                </p>
                                <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                                    {apiConnected ? "localhost:8000 — all agents active" : "Run: python run_research_agent.py"}
                                </p>
                            </div>
                        </div>

                        {/* Hovered node details */}
                        <AnimatePresence mode="wait">
                            {hoveredNode ? (
                                <motion.div
                                    key={hoveredNode.id}
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -8 }}
                                    className="glass rounded-xl p-4 border"
                                    style={{ borderColor: hoveredNode.color + "40" }}
                                >
                                    <div className="flex items-center gap-2.5 mb-3">
                                        <div
                                            className="w-8 h-8 rounded-lg flex items-center justify-center"
                                            style={{ background: hoveredNode.color + "22" }}
                                        >
                                            <hoveredNode.icon className="w-4 h-4" style={{ color: hoveredNode.color }} />
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                                                {hoveredNode.label}
                                            </p>
                                            <p className="text-xs" style={{ color: hoveredNode.color }}>
                                                {hoveredNode.sublabel}
                                            </p>
                                        </div>
                                    </div>
                                    <p className="text-xs mb-3" style={{ color: "var(--text-secondary)" }}>
                                        {hoveredNode.tooltip}
                                    </p>
                                    <div className="space-y-1.5">
                                        {hoveredNode.details.map((detail, i) => (
                                            <div key={i} className="flex items-start gap-2">
                                                <ChevronRight
                                                    className="w-3 h-3 mt-0.5 flex-shrink-0"
                                                    style={{ color: hoveredNode.color }}
                                                />
                                                <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                                                    {detail}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="glass rounded-xl p-4 border text-center"
                                    style={{ borderColor: "var(--border-card)" }}
                                >
                                    <Info className="w-8 h-8 mx-auto mb-2 opacity-20" style={{ color: "var(--text-secondary)" }} />
                                    <p className="text-sm" style={{ color: "var(--text-secondary)", opacity: 0.6 }}>
                                        Hover over a node to see agent details
                                    </p>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Agent roster */}
                        <div className="glass rounded-xl p-4 border" style={{ borderColor: "var(--border-card)" }}>
                            <p className="text-xs font-semibold uppercase tracking-wider opacity-60 mb-3">
                                Agent Roster
                            </p>
                            <div className="space-y-2">
                                {NODES.filter((n) => n.agent).map((node) => {
                                    const Icon = node.icon;
                                    const status = node.agent ? agentStatuses[node.agent] : null;
                                    return (
                                        <div
                                            key={node.id}
                                            className="flex items-center gap-2.5 cursor-pointer transition-colors rounded-lg px-2 py-1.5"
                                            style={{ background: hovered === node.id ? `${node.color}10` : "transparent" }}
                                            onMouseEnter={() => setHovered(node.id)}
                                            onMouseLeave={() => setHovered(null)}
                                        >
                                            <div
                                                className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0"
                                                style={{ background: node.color + "20" }}
                                            >
                                                <Icon className="w-3.5 h-3.5" style={{ color: node.color }} />
                                            </div>
                                            <span className="text-xs flex-1 truncate" style={{ color: "var(--text-secondary)" }}>
                                                {node.agent!.replace("Agent", "")}
                                            </span>
                                            <div
                                                className="w-1.5 h-1.5 rounded-full"
                                                style={{
                                                    background: status === "active" ? "#f59e0b"
                                                        : apiConnected ? "#34d399"
                                                            : "#64748b"
                                                }}
                                            />
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
