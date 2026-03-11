"use client";

import { useCallback, useEffect, useState } from "react";
import { getRamachandranData } from "@/lib/api";
import { RefreshCw } from "lucide-react";

import dynamic from "next/dynamic";
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

// Session-scoped cache — avoids redundant API calls when the card remounts
const ramaCache = new Map<string, { phi: number[]; psi: number[] }>();

interface Props {
  sessionId: string;
  height?: number;
}

export default function RamachandranPlot({ sessionId, height = 260 }: Props) {
  const [data, setData] = useState<{ phi: number[]; psi: number[] } | null>(
    () => ramaCache.get(sessionId) ?? null
  );
  const [loading, setLoading] = useState(!ramaCache.has(sessionId));

  const load = useCallback((force = false) => {
    if (!force && ramaCache.has(sessionId)) {
      setData(ramaCache.get(sessionId)!);
      return;
    }
    setLoading(true);
    getRamachandranData(sessionId, force)
      .then((r) => {
        if (r.available) {
          ramaCache.set(sessionId, r.data);
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
        <p>Ramachandran Plot</p>
        <p className="mt-1">Run a simulation to generate trajectory data</p>
        <button onClick={() => load(true)} className="mt-2 text-blue-500 hover:underline flex items-center gap-1 mx-auto">
          <RefreshCw size={11} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between px-2 pt-2">
        <p className="text-xs font-medium">Ramachandran Plot</p>
        <button onClick={() => load(true)} className="text-gray-400 hover:text-gray-600">
          <RefreshCw size={12} className={loading ? "animate-spin" : ""} />
        </button>
      </div>
      <Plot
        data={[
          {
            type: "histogram2dcontour",
            x: data.phi,
            y: data.psi,
            colorscale: "Blues",
            reversescale: true,
            showscale: false,
            ncontours: 20,
            contours: { coloring: "fill" },
          } as Plotly.Data,
        ]}
        layout={{
          xaxis: { title: { text: "φ (rad)", font: { size: 9 } } as any, range: [-Math.PI, Math.PI], zeroline: false, tickfont: { size: 8 } },
          yaxis: { title: { text: "ψ (rad)", font: { size: 9 } } as any, range: [-Math.PI, Math.PI], zeroline: false, tickfont: { size: 8 } },
          margin: { t: 10, l: 50, r: 20, b: 40 },
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
