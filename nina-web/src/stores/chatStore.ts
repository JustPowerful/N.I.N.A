import { create } from "zustand";
import api from "@/lib/api/axios-instance";

export type Message = {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

type MessageStore = {
  // UI state
  isLoading: boolean;
  isError: boolean;
  message: string | null;

  messages: Message[];
  fetchMessages: (sessionId: string) => Promise<void>;

  sendMessage: (sessionId: string, content: string) => Promise<void>;
};

export const useChatStore = create<MessageStore>((set) => ({
  isLoading: false,
  isError: false,
  message: null,

  messages: [],
  fetchMessages: async (sessionId: string) => {
    try {
      set({ isLoading: true, isError: false, message: null });
      const response = await api.get<{ response: string; messages: Message[] }>(
        `/chat/getmessages/${sessionId}`,
      );
      set({
        messages: response.data.messages,
        message: response.data.response,
      });
    } catch (err) {
      set({
        isError: true,
        message: "Failed to fetch messages",
      });
    } finally {
      set({ isLoading: false });
    }
  },
  sendMessage: async (sessionId: string, content: string) => {
    try {
      set({
        isLoading: true,
        isError: false,
        message: null,
      });
      set((state) => ({
        messages: [
          ...state.messages,
          {
            role: "user",
            content: content,
            timestamp: new Date().toISOString(),
          },
        ],
      }));
      const response = await api.post<{ response: string }>("/chat/send", {
        session_id: sessionId,
        message: content,
      });
      const chatResponse = response.data.response;
      set((state) => ({
        messages: [
          ...state.messages,
          {
            role: "assistant",
            content: chatResponse,
            timestamp: new Date().toISOString(),
          },
        ],
        message: response.data.response,
      }));
    } catch (error) {
      set({
        isError: true,
        message: "Failed to send message",
      });
    } finally {
      set({ isLoading: false });
    }
  },
}));
