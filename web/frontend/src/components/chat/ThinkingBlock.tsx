"use client";

import { useState } from "react";
import * as Collapsible from "@radix-ui/react-collapsible";
import { ChevronDown, ChevronRight, Brain } from "lucide-react";
import type { ThinkingBlock as ThinkingBlockType } from "@/lib/types";

export default function ThinkingBlock({ block }: { block: ThinkingBlockType }) {
  const [open, setOpen] = useState(!block.collapsed);

  return (
    <Collapsible.Root open={open} onOpenChange={setOpen} className="my-1">
      <Collapsible.Trigger className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors cursor-pointer select-none">
        <Brain size={12} />
        <span>Thinking</span>
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
      </Collapsible.Trigger>
      <Collapsible.Content>
        <div className="mt-1 pl-3 border-l-2 border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400 whitespace-pre-wrap font-mono leading-relaxed max-h-40 overflow-y-auto">
          {block.content}
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
