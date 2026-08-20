"use client";

import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useSessionStore } from "@/stores/sessionStore";
import { useChatStore } from "@/stores/chatStore";
import { useEffect, useState } from "react";
import ChatSelectBtn from "./_components/chat-select-btn";
import CreateSessionBtn from "./_components/create-session-btn";

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
    <div className="grid grid-cols-[1fr_4fr] h-screen">
      {/* Side Menu of the app */}
      <div className="border-r-2 border-black p-4">
        <h1 className="font-bold text-xl">N.I.N.A AI Agent</h1>
        <p>Browse chat sessions</p>

        <CreateSessionBtn />

        <div className="flex flex-col">
          {currentSessions.map((session) => (
            <ChatSelectBtn session={session} key={session.id} />
          ))}
        </div>
      </div>
      {/* Main chat view */}
      <div className=" relative">
        <div className="p-4">
          {currentSessionId && <p>{currentSessionTitle}</p>}
        </div>
        {messages.map((message, index) => (
          <div
            key={index}
            className={`p-4 ${message.role === "user" ? "bg-blue-500" : "bg-gray-600"} rounded-lg`}
          >
            <p>{message.content}</p>
          </div>
        ))}
        <div className="flex bg-zinc-800 absolute bottom-2 mx-5 left-0 right-0 gap-2 px-2 py-1 rounded-3xl">
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
              }
            }}
          >
            <Send />
          </Button>
        </div>
      </div>
    </div>
  );
}
