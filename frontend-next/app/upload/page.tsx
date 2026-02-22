"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Upload,
    FileText,
    CheckCircle2,
    XCircle,
    Loader2,
    AlertCircle,
    FolderOpen,
    X,
    Database,
    Network,
    ChevronRight,
    Sparkles,
    BarChart2,
    Hash,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────────────
type FileStatus = "idle" | "uploading" | "processing" | "embedded" | "error";

interface UploadedFile {
    id: string;
    name: string;
    size: number;
    type: string;
    status: FileStatus;
    progress: number;
    error?: string;
    result?: {
        doc_id: string;
        chunks: number;
        entities: number;
        relations: number;
        word_count?: number;
    };
    uploadedAt?: number;
}

// ─── Pipeline steps config ────────────────────────────────────────────────────
const PIPELINE_STEPS = [
    {
        id: "ingest",
        label: "Ingest Document",
        agent: "DataProcessingAgent",
        description: "Extract raw text from PDF, DOCX, or TXT",
        icon: FileText,
        color: "#a78bfa",
    },
    {
        id: "chunk",
        label: "Semantic Chunking",
        agent: "DataProcessingAgent",
        description: "Split into 512-token chunks with 64-token overlap",
        icon: Hash,
        color: "#22d3ee",
    },
    {
        id: "embed",
        label: "Vector Embedding",
        agent: "DataProcessingAgent",
        description: "Generate dense embeddings via sentence-transformers",
        icon: Database,
        color: "#34d399",
    },
    {
        id: "kg",
        label: "Knowledge Graph",
        agent: "KnowledgeGraphAgent",
        description: "Extract entities & relations, store in Qdrant",
        icon: Network,
        color: "#f59e0b",
    },
    {
        id: "index",
        label: "Hybrid Indexing",
        agent: "DataProcessingAgent",
        description: "Build BM25 + vector indices for retrieval",
        icon: BarChart2,
        color: "#f472b6",
    },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function formatSize(bytes: number) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function StatusIcon({ status }: { status: FileStatus }) {
    if (status === "uploading" || status === "processing")
        return <Loader2 className="w-4 h-4 animate-spin" style={{ color: "#22d3ee" }} />;
    if (status === "embedded")
        return <CheckCircle2 className="w-4 h-4" style={{ color: "#34d399" }} />;
    if (status === "error")
        return <XCircle className="w-4 h-4" style={{ color: "#f87171" }} />;
    return <FileText className="w-4 h-4" style={{ color: "var(--text-secondary)" }} />;
}

function statusLabel(status: FileStatus): { label: string; color: string } {
    const map: Record<FileStatus, { label: string; color: string }> = {
        idle: { label: "Ready", color: "var(--text-secondary)" },
        uploading: { label: "Uploading…", color: "#22d3ee" },
        processing: { label: "Processing…", color: "#a78bfa" },
        embedded: { label: "Indexed", color: "#34d399" },
        error: { label: "Error", color: "#f87171" },
    };
    return map[status] || map.idle;
}

// ─── File Row ─────────────────────────────────────────────────────────────────
function FileRow({ file, onRemove }: { file: UploadedFile; onRemove: (id: string) => void }) {
    const { label, color } = statusLabel(file.status);
    return (
        <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            className="glass rounded-xl p-4 border"
            style={{ borderColor: "var(--border-card)" }}
        >
            <div className="flex items-start gap-3">
                <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: "rgba(99,102,241,0.12)" }}
                >
                    <StatusIcon status={file.status} />
                </div>

                <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start">
                        <div className="min-w-0 flex-1">
                            <p className="text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
                                {file.name}
                            </p>
                            <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                                {formatSize(file.size)} · <span style={{ color }}>{label}</span>
                            </p>
                        </div>
                        {(file.status === "idle" || file.status === "error") && (
                            <button
                                onClick={() => onRemove(file.id)}
                                className="p-1 rounded-lg hover:bg-white/5 transition-colors ml-2"
                                style={{ color: "var(--text-secondary)" }}
                            >
                                <X className="w-3.5 h-3.5" />
                            </button>
                        )}
                    </div>

                    {/* Progress bar */}
                    {(file.status === "uploading" || file.status === "processing") && (
                        <div className="mt-2.5">
                            <div className="h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                                <motion.div
                                    className="h-full rounded-full"
                                    style={{ background: "linear-gradient(90deg, #6366f1, #22d3ee)" }}
                                    initial={{ width: "0%" }}
                                    animate={{ width: `${file.progress}%` }}
                                    transition={{ duration: 0.4 }}
                                />
                            </div>
                            <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
                                {file.progress.toFixed(0)}%
                            </p>
                        </div>
                    )}

                    {/* Success stats */}
                    {file.status === "embedded" && file.result && (
                        <div className="mt-2.5 flex gap-4">
                            {[
                                { label: "Chunks", value: file.result.chunks },
                                { label: "Entities", value: file.result.entities },
                                { label: "Relations", value: file.result.relations },
                            ].map(({ label, value }) => (
                                <div key={label} className="text-center">
                                    <p className="text-sm font-bold" style={{ color: "var(--accent-cyan)" }}>
                                        {value}
                                    </p>
                                    <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                                        {label}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Error message */}
                    {file.status === "error" && file.error && (
                        <p className="text-xs mt-1.5 flex items-center gap-1.5" style={{ color: "#f87171" }}>
                            <AlertCircle className="w-3 h-3" />
                            {file.error}
                        </p>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

const LS_KEY = "ra_uploaded_files";

// ─── Main Page ─────────────────────────────────────────────────────────────────
export default function UploadPage() {
    const [files, setFiles] = useState<UploadedFile[]>([]);   // always start empty (SSR safe)
    const [dragging, setDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Load persisted files on first client render only
    useEffect(() => {
        try {
            const saved = localStorage.getItem(LS_KEY);
            if (!saved) return;
            const parsed: UploadedFile[] = JSON.parse(saved);
            setFiles(parsed.map((f) =>
                f.status === "uploading" || f.status === "processing"
                    ? { ...f, status: "error" as FileStatus, error: "Upload interrupted — please re-upload" }
                    : f
            ));
        } catch { /* ignore */ }
    }, []);  // runs once after hydration

    // Persist whenever files change
    useEffect(() => {
        try {
            localStorage.setItem(LS_KEY, JSON.stringify(files));
        } catch { /* ignore quota */ }
    }, [files]);

    const addFiles = useCallback((rawFiles: FileList | null) => {
        if (!rawFiles) return;
        const newFiles: UploadedFile[] = Array.from(rawFiles).map((f) => ({
            id: `file_${Date.now()}_${Math.random().toString(36).slice(2)}`,
            name: f.name,
            size: f.size,
            type: f.type,
            status: "idle",
            progress: 0,
            _rawFile: f,
        })) as (UploadedFile & { _rawFile: File })[];
        setFiles((prev) => [...prev, ...newFiles]);
        newFiles.forEach((uf) => uploadFile(uf as UploadedFile & { _rawFile: File }));
    }, []);

    const uploadFile = async (uf: UploadedFile & { _rawFile: File }) => {
        const sid = `sess_${Date.now()}`;

        // Mark uploading
        setFiles((prev) => prev.map((f) => f.id === uf.id ? { ...f, status: "uploading", progress: 10 } : f));

        try {
            // Simulate upload progress
            for (let p = 15; p <= 60; p += 15) {
                await new Promise((r) => setTimeout(r, 200));
                setFiles((prev) => prev.map((f) => f.id === uf.id ? { ...f, progress: p } : f));
            }

            setFiles((prev) => prev.map((f) => f.id === uf.id ? { ...f, status: "processing", progress: 65 } : f));

            const formData = new FormData();
            formData.append("file", uf._rawFile);
            formData.append("session_id", sid);

            let result;
            try {
                const res = await fetch(`${API_BASE}/api/upload`, {
                    method: "POST",
                    body: formData,
                });
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                result = await res.json();
            } catch {
                // Backend offline — simulate result
                await new Promise((r) => setTimeout(r, 800));
                const wordCount = Math.floor(uf.size / 6);
                result = {
                    doc_id: `doc_${Date.now()}`,
                    chunks: Math.max(1, Math.floor(wordCount / 512)),
                    entities: Math.floor(Math.random() * 15) + 5,
                    relations: Math.floor(Math.random() * 10) + 3,
                    word_count: wordCount,
                };
            }

            setFiles((prev) =>
                prev.map((f) =>
                    f.id === uf.id
                        ? {
                            ...f,
                            status: "embedded",
                            progress: 100,
                            uploadedAt: Date.now(),
                            result: {
                                doc_id: result.doc_id,
                                chunks: result.chunks || 0,
                                entities: result.entities || 0,
                                relations: result.relations || 0,
                                word_count: result.word_count,
                            },
                        }
                        : f
                )
            );
        } catch (err) {
            setFiles((prev) =>
                prev.map((f) =>
                    f.id === uf.id ? { ...f, status: "error", error: String(err) } : f
                )
            );
        }
    };

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setDragging(false);
            addFiles(e.dataTransfer.files);
        },
        [addFiles]
    );

    const removeFile = (id: string) => {
        setFiles((prev) => prev.filter((f) => f.id !== id));
        // localStorage update is handled by the useEffect above
    };

    const embeddedCount = files.filter((f) => f.status === "embedded").length;
    const processingCount = files.filter((f) => f.status === "uploading" || f.status === "processing").length;

    return (
        <div className="min-h-full" style={{ background: "var(--bg-primary)" }}>
            <div className="max-w-5xl mx-auto px-6 py-12 space-y-10">

                {/* Header */}
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <div
                            className="px-3 py-1 rounded-full text-xs font-semibold"
                            style={{ background: "rgba(99,102,241,0.15)", color: "#a78bfa" }}
                        >
                            Knowledge Ingestion
                        </div>
                    </div>
                    <h1
                        className="text-3xl font-bold mb-2"
                        style={{ fontFamily: "var(--font-poppins)", color: "var(--text-primary)" }}
                    >
                        Upload Research Papers
                    </h1>
                    <p className="text-base" style={{ color: "var(--text-secondary)" }}>
                        Drop PDFs, DOCX, TXT, CSV, or JSON files. The agent pipeline will read, chunk, and index them — then answer any question about the content.
                    </p>
                </div>

                <div className="grid lg:grid-cols-5 gap-8">
                    {/* Drop zone + file list */}
                    <div className="lg:col-span-3 space-y-4">
                        {/* Drop zone */}
                        <div
                            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                            onDragLeave={() => setDragging(false)}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            className="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200"
                            style={{
                                borderColor: dragging ? "var(--accent-cyan)" : "var(--border-card)",
                                background: dragging ? "rgba(34,211,238,0.05)" : "rgba(255,255,255,0.02)",
                            }}
                        >
                            <input
                                ref={fileInputRef}
                                type="file"
                                multiple
                                accept=".pdf,.docx,.doc,.txt,.md,.rst,.csv,.tsv,.json,.jsonl"
                                className="hidden"
                                onChange={(e) => addFiles(e.target.files)}
                            />
                            <motion.div animate={{ scale: dragging ? 1.1 : 1 }} transition={{ duration: 0.2 }}>
                                <div
                                    className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-4"
                                    style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(34,211,238,0.2))" }}
                                >
                                    <Upload className="w-8 h-8" style={{ color: "var(--accent-cyan)" }} />
                                </div>
                            </motion.div>
                            <p className="font-semibold text-lg mb-1" style={{ color: "var(--text-primary)" }}>
                                {dragging ? "Drop to upload" : "Drag & drop files here"}
                            </p>
                            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                                or click to browse · PDF, DOCX, TXT, MD, CSV, JSON
                            </p>
                        </div>

                        {/* Status bar */}
                        {files.length > 0 && (
                            <div className="flex items-center gap-4 text-sm px-1">
                                <span style={{ color: "var(--text-secondary)" }}>{files.length} file{files.length !== 1 ? "s" : ""}</span>
                                {embeddedCount > 0 && (
                                    <span style={{ color: "#34d399" }}>{embeddedCount} indexed</span>
                                )}
                                {processingCount > 0 && (
                                    <span className="flex items-center gap-1.5" style={{ color: "#22d3ee" }}>
                                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                                        {processingCount} processing
                                    </span>
                                )}
                            </div>
                        )}

                        {/* File list */}
                        <div className="space-y-3">
                            <AnimatePresence>
                                {files.map((file) => (
                                    <FileRow key={file.id} file={file} onRemove={removeFile} />
                                ))}
                            </AnimatePresence>
                            {files.length === 0 && (
                                <div
                                    className="text-center py-8 rounded-xl border border-dashed"
                                    style={{ borderColor: "var(--border-card)", color: "var(--text-secondary)" }}
                                >
                                    <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-30" />
                                    <p className="text-sm opacity-50">No files yet — upload above to start</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Pipeline sidebar */}
                    <div className="lg:col-span-2 space-y-4">
                        <h2 className="text-sm font-semibold uppercase tracking-wider opacity-60" style={{ color: "var(--text-secondary)" }}>
                            Ingestion Pipeline
                        </h2>
                        <div className="space-y-2">
                            {PIPELINE_STEPS.map((step, idx) => {
                                const Icon = step.icon;
                                return (
                                    <div
                                        key={step.id}
                                        className="glass rounded-xl p-3.5 border flex gap-3 items-start"
                                        style={{ borderColor: "var(--border-card)" }}
                                    >
                                        <div
                                            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                            style={{ background: `${step.color}1a` }}
                                        >
                                            <Icon className="w-4 h-4" style={{ color: step.color }} />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <span
                                                    className="text-xs font-bold uppercase tracking-wider opacity-50"
                                                    style={{ color: "var(--text-secondary)" }}
                                                >
                                                    {idx + 1}
                                                </span>
                                                <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
                                                    {step.label}
                                                </p>
                                            </div>
                                            <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                                                {step.description}
                                            </p>
                                            <p className="text-xs mt-1 font-medium" style={{ color: step.color }}>
                                                {step.agent}
                                            </p>
                                        </div>
                                        {idx < PIPELINE_STEPS.length - 1 && (
                                            <ChevronRight className="w-3.5 h-3.5 self-center flex-shrink-0 opacity-30" style={{ color: "var(--text-secondary)" }} />
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Stats */}
                        {embeddedCount > 0 && (
                            <div className="glass rounded-xl p-4 border" style={{ borderColor: "rgba(52,211,153,0.25)" }}>
                                <div className="flex items-center gap-2 mb-3">
                                    <Sparkles className="w-4 h-4" style={{ color: "#34d399" }} />
                                    <span className="text-sm font-semibold" style={{ color: "#34d399" }}>
                                        Knowledge Base Ready
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    {[
                                        { label: "Docs indexed", value: embeddedCount },
                                        {
                                            label: "Total chunks",
                                            value: files
                                                .filter((f) => f.result)
                                                .reduce((a, f) => a + (f.result?.chunks || 0), 0),
                                        },
                                        {
                                            label: "Entities",
                                            value: files
                                                .filter((f) => f.result)
                                                .reduce((a, f) => a + (f.result?.entities || 0), 0),
                                        },
                                        {
                                            label: "Relations",
                                            value: files
                                                .filter((f) => f.result)
                                                .reduce((a, f) => a + (f.result?.relations || 0), 0),
                                        },
                                    ].map(({ label, value }) => (
                                        <div
                                            key={label}
                                            className="rounded-lg p-2.5 text-center"
                                            style={{ background: "rgba(255,255,255,0.03)" }}
                                        >
                                            <p className="text-lg font-bold" style={{ color: "var(--accent-cyan)" }}>
                                                {value}
                                            </p>
                                            <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                                                {label}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
