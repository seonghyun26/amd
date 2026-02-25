"use client";

import { useSessionStore } from "@/store/sessionStore";
import { Activity } from "lucide-react";

export default function SimulationStatus() {
  const simProgress = useSessionStore((s) => s.simProgress);

  if (!simProgress) {
    return (
      <div className="p-4 text-center text-gray-400 dark:text-gray-600">
        <Activity size={24} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">No active simulation</p>
      </div>
    );
  }

  const pct = simProgress.totalSteps > 0
    ? Math.min(100, (simProgress.step / simProgress.totalSteps) * 100)
    : 0;
  const timeNs = simProgress.timePs / 1000;

  const eta = simProgress.nsPerDay > 0
    ? ((simProgress.totalSteps - simProgress.step) * 0.002 / 1000 / simProgress.nsPerDay * 24)
    : null;

  return (
    <div className="p-4 space-y-4">
      <h3 className="text-sm font-semibold flex items-center gap-2">
        <Activity size={14} className="text-green-500" />
        Simulation Running
      </h3>

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{simProgress.step.toLocaleString()} steps</span>
          <span>{pct.toFixed(1)}%</span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
          <p className="text-xs text-gray-400">Time</p>
          <p className="text-sm font-mono font-medium">{timeNs.toFixed(3)} ns</p>
        </div>
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2">
          <p className="text-xs text-gray-400">Performance</p>
          <p className="text-sm font-mono font-medium">{simProgress.nsPerDay.toFixed(2)} ns/day</p>
        </div>
        {eta !== null && (
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-2 col-span-2">
            <p className="text-xs text-gray-400">ETA</p>
            <p className="text-sm font-mono font-medium">
              {eta < 1 ? `${(eta * 60).toFixed(0)} min` : `${eta.toFixed(1)} hr`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
