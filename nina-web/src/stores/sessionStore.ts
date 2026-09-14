import api from "@/lib/api/axios-instance";
import { create } from "zustand";

export type Session = {
  id: string;
  title: string;
};

type SessionStore = {
  // sessions list
  currentSessions: Session[];
  fetchSessions: () => Promise<void>;
  // Display states for the session UI
  isLoading: boolean;
  isError: boolean;
  message: string | null;
  // Current session states
  currentSessionId: string | null;
  currentSessionTitle: string | null;
  setCurrentSession: (sessionId: string, currentSessionTitle: string) => void;
  deleteSession: (sessionId: string) => Promise<void>;
  createSession: (sessionTitle: string) => Promise<string | undefined>;
};

export const useSessionStore = create<SessionStore>((set) => ({
  isLoading: false,
  isError: false,
  message: null,
  currentSessions: [],
  fetchSessions: async () => {
    try {
      set({ isLoading: true, isError: false, message: null });
      // Simulate an API call
      const response = await api.get<{
        response: string;
        sessions: Session[];
      }>("/session/all");
      set({
        currentSessions: response.data.sessions,
        message: response.data.response,
      });
    } catch (error) {
      set({
        isError: true,
        message: "Failed to fetch sessions",
        isLoading: false,
      });
    } finally {
      set({ isLoading: false });
    }
  },
  currentSessionId: null,
  currentSessionTitle: null,
  setCurrentSession: (sessionId: string, currentSessionTitle: string) => {
    set({ currentSessionId: sessionId, currentSessionTitle });
  },
  deleteSession: async (sessionId: string) => {
    try {
      set({ isLoading: true, isError: false, message: null });
      const response = await api.delete<{ response: string }>(
        `/session/delete/${sessionId}`,
      );
      set((state) => ({
        message: response.data.response,
        currentSessions: state.currentSessions.filter(
          (session) => session.id !== sessionId,
        ),
      }));
    } catch (error) {
      set({
        isError: true,
        message: "Failed to delete session",
        isLoading: false,
      });
    } finally {
      set({ isLoading: false });
    }
  },
  createSession: async (sessionTitle: string) => {
    try {
      set({ isLoading: true, isError: false, message: null });
      const response = await api.post<{ response: string; session_id: string }>(
        "/session/create",
        { title: sessionTitle },
      );
      set((state) => ({
        message: response.data.response,
        currentSessions: [
          { id: response.data.session_id, title: sessionTitle },
          ...state.currentSessions,
        ],
      }));
      return response.data.session_id;
    } catch (error) {
      set({
        isError: true,
        message: "Failed to create session",
        isLoading: false,
      });
    } finally {
      set({ isLoading: false });
    }
  },
}));
