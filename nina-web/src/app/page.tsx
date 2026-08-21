"use client";

import { Button } from "@/components/ui/button";
import { Loader2, Send } from "lucide-react";
import { useSessionStore } from "@/stores/sessionStore";
import { useChatStore } from "@/stores/chatStore";
import { useEffect, useState } from "react";
import ChatSelectBtn from "./_components/chat-select-btn";
import CreateSessionBtn from "./_components/create-session-btn";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SseEventTracker from "./_components/sse-event-tracker";

export default function Home() {
  const {
    currentSessions,
    fetchSessions,
    currentSessionId,
    currentSessionTitle,
  } = useSessionStore();

  const [chatInput, setChatInput] = useState("");
  const { messages, fetchMessages, isLoading, sendMessage } = useChatStore();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions, fetchSessions]);

  useEffect(() => {
    if (currentSessionId) {
      fetchMessages(currentSessionId);
    }
  }, [currentSessionId, fetchMessages]);

  return (
    <div className="grid h-screen grid-cols-[1fr_4fr] overflow-hidden">
      {/* Side Menu of the app */}
      <div className="border-r-2 border-black p-4">
        <h1 className="font-bold text-xl">N.I.N.A AI Agent</h1>
        <p>Browse chat sessions</p>

        <CreateSessionBtn />

        <div>
          {currentSessions.map((session) => (
            <ChatSelectBtn session={session} key={session.id} />
          ))}
        </div>
      </div>
      {/* Main chat view */}
      <div className="relative flex min-h-0 flex-col overflow-hidden">
        {/* Sessin title section */}
        <div className="p-4 h-16 flex items-center border-b-2 border-black">
          {currentSessionId && <p>{currentSessionTitle}</p>}
        </div>
        {/* Scrollable message area */}
        <div className="flex-1 min-h-0 overflow-y-auto px-5 pb-24 relative">
          {/* The block containing chat messages */}
          <div className="flex flex-col gap-3 py-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`max-w-[80%] rounded-lg p-4 ${message.role === "user" ? "ml-auto bg-blue-500 text-white" : "bg-gray-600 text-white"}`}
              >
                <Markdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </Markdown>
              </div>
            ))}
            <SseEventTracker sessionId={currentSessionId || ""} />
          </div>
        </div>
        <div className="absolute bottom-2 left-0 right-0 mx-5 flex gap-2 rounded-3xl bg-zinc-800 px-2 py-1">
          <input
            className="flex-1 bg-transparent border-none outline-none text-white"
            placeholder="write your prompt here..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
          />
          <Button
            variant="secondary"
            className="rounded-full w-10 h-10 p-0 flex items-center justify-center"
            onClick={() => {
              if (chatInput && currentSessionId) {
                sendMessage(currentSessionId, chatInput).then(() => {
                  setChatInput("");
                });
                setChatInput("");
              }
            }}
          >
            {isLoading ? <Loader2 className="animate-spin" /> : <Send />}
          </Button>
        </div>
      </div>
    </div>
  );
}
