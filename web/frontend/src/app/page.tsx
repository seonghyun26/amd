"use client";

import { useEffect, useState } from "react";
import { createSession, getConfigOptions } from "@/lib/api";
import type { ConfigOptions } from "@/lib/types";
import { useSessionStore } from "@/store/sessionStore";

// ── Session view (full chat layout) ──────────────────────────────────

import * as Tabs from "@radix-ui/react-tabs";
import { ArrowLeft, Settings, Activity, BarChart2 } from "lucide-react";
import ChatWindow from "@/components/chat/ChatWindow";
import ChatInput from "@/components/chat/ChatInput";
import FileBrowser from "@/components/files/FileBrowser";
import FileUpload from "@/components/files/FileUpload";
import ConfigBuilder from "@/components/config/ConfigBuilder";
import SimulationStatus from "@/components/status/SimulationStatus";
import RamachandranPlot from "@/components/viz/RamachandranPlot";
import EnergyPlot from "@/components/viz/EnergyPlot";
import ColvarPlot from "@/components/viz/ColvarPlot";

function SessionView({
  sessionId,
  onNewSession,
}: {
  sessionId: string;
  onNewSession: () => void;
}) {
  const [fileRefresh, setFileRefresh] = useState(0);

  return (
    <div className="flex h-screen overflow-hidden bg-white dark:bg-gray-950">
      {/* Left sidebar — Files */}
      <aside className="w-56 flex-shrink-0 border-r border-gray-200 dark:border-gray-800 flex flex-col overflow-hidden">
        <div className="p-2 border-b border-gray-200 dark:border-gray-800 flex items-center gap-2">
          <button
            onClick={onNewSession}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors"
            title="New session"
          >
            <ArrowLeft size={14} />
          </button>
          <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">Session</span>
          <span className="text-xs font-mono text-gray-400 truncate" title={sessionId}>
            {sessionId.slice(0, 8)}…
          </span>
        </div>

        <div className="flex-1 overflow-y-auto">
          <FileBrowser sessionId={sessionId} refreshTrigger={fileRefresh} />
        </div>

        <div className="p-2 border-t border-gray-200 dark:border-gray-800">
          <FileUpload sessionId={sessionId} onUploaded={() => setFileRefresh((n) => n + 1)} />
        </div>
      </aside>

      {/* Center — Chat */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatWindow />
        <ChatInput sessionId={sessionId} />
      </main>

      {/* Right panel — Config / Status / Plots */}
      <aside className="w-72 flex-shrink-0 border-l border-gray-200 dark:border-gray-800 flex flex-col overflow-hidden">
        <Tabs.Root defaultValue="config" className="flex flex-col flex-1 overflow-hidden">
          <Tabs.List className="flex border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
            {[
              { value: "config", icon: <Settings size={13} />, label: "Config" },
              { value: "status", icon: <Activity size={13} />, label: "Status" },
              { value: "plots", icon: <BarChart2 size={13} />, label: "Plots" },
            ].map(({ value, icon, label }) => (
              <Tabs.Trigger
                key={value}
                value={value}
                className="flex-1 flex items-center justify-center gap-1.5 text-xs py-2.5 text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 data-[state=active]:text-blue-600 dark:data-[state=active]:text-blue-400 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 dark:data-[state=active]:border-blue-400 transition-colors -mb-px"
              >
                {icon}
                {label}
              </Tabs.Trigger>
            ))}
          </Tabs.List>

          <div className="flex-1 overflow-y-auto">
            <Tabs.Content value="config">
              <ConfigBuilder sessionId={sessionId} />
            </Tabs.Content>
            <Tabs.Content value="status">
              <SimulationStatus />
            </Tabs.Content>
            <Tabs.Content value="plots" className="space-y-2 pb-4">
              <EnergyPlot sessionId={sessionId} />
              <ColvarPlot sessionId={sessionId} />
              <RamachandranPlot sessionId={sessionId} />
            </Tabs.Content>
          </div>
        </Tabs.Root>
      </aside>
    </div>
  );
}

// ── New session form ───────────────────────────────────────────────────

function NewSessionForm({ onCreated }: { onCreated: (id: string) => void }) {
  const [options, setOptions] = useState<ConfigOptions>({
    methods: ["metadynamics"],
    systems: ["protein"],
    gromacs: ["default"],
    plumed_cvs: ["default"],
  });
  const [form, setForm] = useState({
    method: "metadynamics",
    system: "protein",
    gromacs: "default",
    plumed_cvs: "default",
    workDir: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setForm((f) => ({
      ...f,
      workDir: `outputs/session-${Date.now()}`,
    }));
    getConfigOptions()
      .then((opts) => {
        setOptions(opts);
        setForm((f) => ({
          ...f,
          method: opts.methods[0] ?? f.method,
          system: opts.systems[0] ?? f.system,
          gromacs: opts.gromacs[0] ?? f.gromacs,
          plumed_cvs: opts.plumed_cvs[0] ?? f.plumed_cvs,
        }));
      })
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { session_id } = await createSession({
        method: form.method,
        system: form.system,
        gromacs: form.gromacs,
        plumed_cvs: form.plumed_cvs,
        workDir: form.workDir,
      });
      onCreated(session_id);
    } catch (err) {
      setError(String(err));
      setLoading(false);
    }
  };

  const SelectField = ({
    label,
    value,
    opts,
    onChange,
  }: {
    label: string;
    value: string;
    opts: string[];
    onChange: (v: string) => void;
  }) => (
    <div>
      <label className="block text-sm font-medium mb-1">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border rounded-lg px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {opts.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-950 p-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">MD Simulation Agent</h1>
          <p className="mt-2 text-gray-500 dark:text-gray-400">Claude Opus 4.6 · GROMACS · PLUMED</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 bg-white dark:bg-gray-900 rounded-2xl shadow p-6 border border-gray-200 dark:border-gray-800"
        >
          <SelectField
            label="Sampling Method"
            value={form.method}
            opts={options.methods}
            onChange={(v) => setForm({ ...form, method: v })}
          />
          <SelectField
            label="System"
            value={form.system}
            opts={options.systems}
            onChange={(v) => setForm({ ...form, system: v })}
          />
          <SelectField
            label="GROMACS Preset"
            value={form.gromacs}
            opts={options.gromacs}
            onChange={(v) => setForm({ ...form, gromacs: v })}
          />
          <SelectField
            label="Collective Variables"
            value={form.plumed_cvs}
            opts={options.plumed_cvs}
            onChange={(v) => setForm({ ...form, plumed_cvs: v })}
          />
          <div>
            <label className="block text-sm font-medium mb-1">Output Directory</label>
            <input
              type="text"
              value={form.workDir}
              onChange={(e) => setForm({ ...form, workDir: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm rounded bg-red-50 dark:bg-red-950 p-2">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            {loading ? "Starting session…" : "Start Session"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Root component ─────────────────────────────────────────────────────

const STORAGE_KEY = "mda-session";

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const { setSession, clearMessages } = useSessionStore();

  // Restore session from localStorage on first render (client-only)
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      setSessionId(saved);
      setSession(saved, { method: "", system: "", gromacs: "", plumed_cvs: "", workDir: "" });
    }
  }, [setSession]);

  const handleCreated = (id: string) => {
    localStorage.setItem(STORAGE_KEY, id);
    setSession(id, { method: "", system: "", gromacs: "", plumed_cvs: "", workDir: "" });
    setSessionId(id);
  };

  const handleNewSession = () => {
    localStorage.removeItem(STORAGE_KEY);
    clearMessages();
    setSessionId(null);
  };

  if (!sessionId) {
    return <NewSessionForm onCreated={handleCreated} />;
  }

  return <SessionView sessionId={sessionId} onNewSession={handleNewSession} />;
}
