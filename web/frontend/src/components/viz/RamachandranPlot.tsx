"use client";

import { useCallback, useEffect, useState } from "react";
import { getFes } from "@/lib/api";
import { RefreshCw } from "lucide-react";

import dynamic from "next/dynamic";
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// Session-scoped FES cache — avoids redundant API calls when the card remounts
const fesCache = new Map<string, { x: number[]; y: number[]; z: number[][] }>();

interface Props {
  sessionId: string;
  height?: number;
}

export default function RamachandranPlot({ sessionId, height = 260 }: Props) {
  const [data, setData] = useState<{ x: number[]; y: number[]; z: number[][] } | null>(
    () => fesCache.get(sessionId) ?? null
  );
  const [loading, setLoading] = useState(!fesCache.has(sessionId));

  const load = useCallback((force = false) => {
    if (!force && fesCache.has(sessionId)) {
      setData(fesCache.get(sessionId)!);
      return;
    }
    setLoading(true);
    getFes(sessionId)
      .then((r) => {
        if (r.available) {
          fesCache.set(sessionId, r.data);
          setData(r.data);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [sessionId]);

  useEffect(() => { load(); }, [load]);

  if (!data) {
    return (
      <div className="p-3 text-center text-xs text-gray-400">
        <p>Ramachandran FES</p>
        <p className="mt-1">Run <code className="font-mono">analyze_hills</code> to generate</p>
        <button onClick={() => load(true)} className="mt-2 text-blue-500 hover:underline flex items-center gap-1 mx-auto">
          <RefreshCw size={11} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between px-2 pt-2">
        <p className="text-xs font-medium">Ramachandran FES</p>
        <button onClick={() => load(true)} className="text-gray-400 hover:text-gray-600">
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
        </button>
      </div>
      <Plot
        data={[
          {
            type: "heatmap",
            x: data.x,
            y: data.y,
            z: data.z,
            colorscale: "RdBu",
            reversescale: true,
            colorbar: { title: "kJ/mol" as any, titleside: "right", thickness: 12 },
          } as Plotly.Data,
        ]}
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        layout={{
          xaxis: { title: "φ (rad)" as any, zeroline: false },
          yaxis: { title: "ψ (rad)" as any, zeroline: false },
          margin: { t: 10, l: 50, r: 60, b: 40 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          height,
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: "100%" }}
      />
    </div>
  );
}
