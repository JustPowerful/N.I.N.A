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

  assistantAudio: string | null;
  clearAssistantAudio: () => void;

  // for enabling or disabling the ability for the assistant to speak with the user
  enableSpeech: boolean;
  toggleSpeech: () => void;

  messages: Message[];
  fetchMessages: (sessionId: string) => Promise<void>;

  sendMessage: (sessionId: string, content: string) => Promise<void>;
};

export const useChatStore = create<MessageStore>((set, get) => ({
  isLoading: false,
  isError: false,
  message: null,
  assistantAudio: null,
  clearAssistantAudio: () => set({ assistantAudio: null }),

  enableSpeech: true,
  toggleSpeech: () => set((state) => ({ enableSpeech: !state.enableSpeech })),

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
        assistantAudio: null,
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
      // push the user message to the messages array before sending it to the server
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
      // send the message to the server to process and get the assistant's response
      // get the enableSpeech state
      const response = await api.post<{
        response: string;
        audio: string | null;
      }>("/chat/send", {
        session_id: sessionId,
        message: content,
        generated_audio: get().enableSpeech,
      });
      const chatResponse = response.data.response; // text response from the assistant
      const audioResponse = response.data.audio; // base64 audio response from the assistant
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
        assistantAudio: audioResponse,
      }));
      // play the audio response if it exists
      // audio playback is handled by the visualizer component
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
