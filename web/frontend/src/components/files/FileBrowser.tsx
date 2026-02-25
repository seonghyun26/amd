"use client";

import { useCallback, useEffect, useState } from "react";
import { FileText, RefreshCw } from "lucide-react";
import { downloadUrl, listFiles } from "@/lib/api";

interface Props {
  sessionId: string;
  refreshTrigger?: number;
}

const EXT_ICONS: Record<string, string> = {
  pdb: "🧬",
  gro: "🧬",
  top: "📋",
  itp: "📋",
  tpr: "🔵",
  mdp: "⚙️",
  dat: "📊",
  xvg: "📈",
  edr: "📦",
  log: "📝",
  cpt: "💾",
  xtc: "🎞️",
  trr: "🎞️",
};

function fileIcon(filename: string) {
  const ext = filename.split(".").pop()?.toLowerCase() ?? "";
  return EXT_ICONS[ext] ?? "📄";
}

function basename(path: string) {
  return path.split("/").pop() ?? path;
}

export default function FileBrowser({ sessionId, refreshTrigger }: Props) {
  const [files, setFiles] = useState<string[]>([]);
  const [workDir, setWorkDir] = useState("");
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(() => {
    setLoading(true);
    listFiles(sessionId)
      .then(({ files, work_dir }) => {
        setFiles(files);
        setWorkDir(work_dir);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [sessionId]);

  useEffect(() => { refresh(); }, [refresh, refreshTrigger]);

  return (
    <div className="p-2 space-y-1">
      <div className="flex items-center justify-between py-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Files</span>
        <button
          onClick={refresh}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
          title="Refresh"
        >
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {workDir && (
        <p className="text-xs text-gray-400 font-mono truncate" title={workDir}>{workDir}</p>
      )}

      <div className="space-y-0.5 max-h-72 overflow-y-auto">
        {files.length === 0 ? (
          <p className="text-xs text-gray-400 py-2">No files yet</p>
        ) : (
          files.map((f) => (
            <a
              key={f}
              href={downloadUrl(sessionId, f)}
              download={basename(f)}
              className="flex items-center gap-1.5 px-1 py-0.5 rounded hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer"
            >
              <span className="text-sm leading-none">{fileIcon(f)}</span>
              <span className="text-xs text-gray-700 dark:text-gray-300 truncate" title={f}>
                {basename(f)}
              </span>
            </a>
          ))
        )}
      </div>
    </div>
  );
}
