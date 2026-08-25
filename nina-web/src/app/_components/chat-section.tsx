import React, { useEffect } from "react";
import ChatInput from "./chat-input";
import { MessageCircleIcon } from "lucide-react";
import { useSessionStore } from "@/stores/sessionStore";
import { useChatStore } from "@/stores/chatStore";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SseEventTracker from "./sse-event-tracker";

const ChatContainer = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="relative flex min-h-0 flex-col overflow-hidden flex-1">
      {children}
    </div>
  );
};

const ChatSection = () => {
  const { fetchSessions, currentSessionId, currentSessionTitle } =
    useSessionStore();

  const { messages, fetchMessages, isLoading, sendMessage } = useChatStore();

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions, fetchSessions]);

  useEffect(() => {
    if (currentSessionId) {
      fetchMessages(currentSessionId);
    }
  }, [currentSessionId, fetchMessages]);

  if (!currentSessionId) {
    return (
      <ChatContainer>
        <div className="h-full flex flex-col gap-4 justify-center items-center">
          <h1 className="text-3xl">Ready when you are.</h1>
          <ChatInput createSessionMode />
        </div>
      </ChatContainer>
    );
  }

  return (
    <ChatContainer>
      {/* Sessin title section */}
      <div className=" m-4 p-4 rounded-md flex gap-2 items-center bg-gray-800/80 text-white absolute top-0 left-0 right-0 z-10 backdrop-blur-md">
        <MessageCircleIcon />
        {currentSessionId && <p>{currentSessionTitle}</p>}
      </div>
      {/* Scrollable message area */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 pb-24 relative pt-20">
        {/* The block containing chat messages */}
        <div className="flex flex-col gap-3 py-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`max-w-[80%] rounded-lg p-2 ${message.role === "user" ? "ml-auto bg-blue-500 text-white" : "text-white"}`}
            >
              <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
            </div>
          ))}
          <SseEventTracker />
        </div>
      </div>
      <ChatInput />
    </ChatContainer>
  );
};

export default ChatSection;
