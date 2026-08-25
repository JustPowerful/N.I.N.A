import React, { useEffect, useRef, useState } from "react";
import { useChatStore } from "@/stores/chatStore";
import { Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSessionStore } from "@/stores/sessionStore";

const ChatInput = ({ createSessionMode }: { createSessionMode?: boolean }) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const [chatInput, setChatInput] = useState("");

  const { currentSessionId, createSession, setCurrentSession } =
    useSessionStore();
  const { isLoading, sendMessage } = useChatStore();

  const resizeTextarea = () => {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    const computedStyles = window.getComputedStyle(textarea);
    const lineHeight = Number.parseFloat(computedStyles.lineHeight || "24");
    const maxHeight = lineHeight * 5;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    textarea.style.overflowY =
      textarea.scrollHeight > maxHeight ? "auto" : "hidden";
  };

  const handleCreateSession = async () => {
    if (createSessionMode && chatInput.trim() !== "") {
      const newSessionId = await createSession("New Session");
      if (!newSessionId) {
        return console.error("Failed to create a new session.");
      }

      // send the message to the new session
      await sendMessage(newSessionId, chatInput);

      // set the new session as the current session
      setCurrentSession(newSessionId, "New Session");

      // clear the input field
      setChatInput("");
      resizeTextarea();
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput || !currentSessionId || isLoading) {
      return;
    }

    const message = chatInput;
    setChatInput("");
    resizeTextarea();

    await sendMessage(currentSessionId, message);
  };

  useEffect(() => {
    resizeTextarea();
  }, [chatInput]);

  return (
    <div
      className={
        !createSessionMode
          ? "absolute bottom-2 left-0 right-0 mx-5 flex gap-2 rounded-3xl bg-zinc-800 px-2 py-1"
          : "flex gap-2 rounded-3xl bg-zinc-800 px-2 py-1 w-full max-w-xl"
      }
    >
      <textarea
        ref={textareaRef}
        rows={1}
        className="flex-1 pt-2 pl-2 border-none outline-none text-white resize-none overflow-y-hidden leading-6 bg-transparent"
        placeholder="write your prompt here..."
        value={chatInput}
        onChange={(e) => {
          setChatInput(e.target.value);
          resizeTextarea();
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            void handleSendMessage();
          }
        }}
      />
      <Button
        className="rounded-full w-10 h-10 p-0 flex items-center justify-center"
        onClick={() => {
          if (createSessionMode) {
            void handleCreateSession();
          } else {
            void handleSendMessage();
          }
        }}
      >
        {isLoading ? <Loader2 className="animate-spin" /> : <Send />}
      </Button>
    </div>
  );
};

export default ChatInput;
