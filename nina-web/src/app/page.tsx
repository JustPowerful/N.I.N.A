"use client";

import { useSessionStore } from "@/stores/sessionStore";
import ChatSelectBtn from "./_components/chat-select-btn";
import CreateSessionBtn from "./_components/create-session-btn";
import ChatSection from "./_components/chat-section";

export default function Home() {
  const { currentSessions } = useSessionStore();
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
      <ChatSection />
    </div>
  );
}
