"use client";

import { useSessionStore } from "@/stores/sessionStore";
import ChatSelectBtn from "./_components/chat-select-btn";
import CreateSessionBtn from "./_components/create-session-btn";
import ChatSection from "./_components/chat-section";
import SideMenu from "./_components/side-menu";

export default function Home() {
  const { currentSessions } = useSessionStore();
  //grid grid-cols-[1fr_4fr]
  return (
    <div className="h-screen flex overflow-hidden">
      {/* Side Menu of the app */}
      <SideMenu />
      {/* Main chat view */}
      <ChatSection />
    </div>
  );
}
