import { create } from "zustand";
import type {
  ChatMessage,
  MessageBlock,
  SimProgress,
  SessionConfig,
  SSEEvent,
  ToolCallBlock,
} from "@/lib/types";

interface SessionState {
  sessionId: string | null;
  config: SessionConfig | null;
  messages: ChatMessage[];
  simProgress: SimProgress | null;
  isStreaming: boolean;

  // Actions
  setSession: (id: string, config: SessionConfig) => void;
  addUserMessage: (text: string) => void;
  appendSSEEvent: (event: SSEEvent) => void;
  updateProgress: (progress: SimProgress) => void;
  clearMessages: () => void;
}

function newAssistantMessage(): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role: "assistant",
    blocks: [],
    timestamp: Date.now(),
  };
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  config: null,
  messages: [],
  simProgress: null,
  isStreaming: false,

  setSession: (id, config) =>
    set({ sessionId: id, config, messages: [], simProgress: null }),

  addUserMessage: (text) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          role: "user",
          blocks: [{ kind: "text", content: text }],
          timestamp: Date.now(),
        },
      ],
      isStreaming: true,
    })),

  appendSSEEvent: (event) =>
    set((state) => {
      const messages = [...state.messages];

      // Ensure there is an assistant message at the end
      const ensureAssistant = (): ChatMessage => {
        const last = messages[messages.length - 1];
        if (last && last.role === "assistant") return last;
        const msg = newAssistantMessage();
        messages.push(msg);
        return msg;
      };

      switch (event.type) {
        case "text_delta": {
          const msg = ensureAssistant();
          const idx = messages.indexOf(msg);
          const blocks = [...msg.blocks];
          const lastBlock = blocks[blocks.length - 1];
          if (lastBlock && lastBlock.kind === "text") {
            blocks[blocks.length - 1] = {
              kind: "text",
              content: lastBlock.content + event.text,
            };
          } else {
            blocks.push({ kind: "text", content: event.text });
          }
          messages[idx] = { ...msg, blocks };
          return { messages, isStreaming: true };
        }

        case "thinking": {
          const msg = ensureAssistant();
          const idx = messages.indexOf(msg);
          const blocks = [
            ...msg.blocks,
            { kind: "thinking" as const, content: event.thinking, collapsed: true },
          ];
          messages[idx] = { ...msg, blocks };
          return { messages };
        }

        case "tool_start": {
          const msg = ensureAssistant();
          const idx = messages.indexOf(msg);
          const toolBlock: ToolCallBlock = {
            kind: "tool_call",
            tool_use_id: event.tool_use_id,
            tool_name: event.tool_name,
            input: event.tool_input,
            status: "pending",
          };
          messages[idx] = { ...msg, blocks: [...msg.blocks, toolBlock] };
          return { messages };
        }

        case "tool_result": {
          // Find the pending tool block by id across all messages and update it
          const updated: ChatMessage[] = messages.map((m) => ({
            ...m,
            blocks: m.blocks.map((b): MessageBlock => {
              if (b.kind === "tool_call" && b.tool_use_id === event.tool_use_id) {
                return { ...b, result: event.result, status: "done" };
              }
              return b;
            }),
          }));
          return { messages: updated };
        }

        case "sim_progress":
          return {
            simProgress: {
              step: event.step,
              totalSteps: event.total_steps,
              nsPerDay: event.ns_per_day,
              timePs: event.time_ps,
              lastUpdated: Date.now(),
            },
          };

        case "agent_done":
          return { isStreaming: false };

        case "error":
          return { isStreaming: false };

        default:
          return {};
      }
    }),

  updateProgress: (progress) => set({ simProgress: progress }),
  clearMessages: () => set({ messages: [] }),
}));
