import CreateSessionBtn from "./create-session-btn";
import { useSessionStore } from "@/stores/sessionStore";
import ChatSelectBtn from "./chat-select-btn";
import { Button } from "@/components/ui/button";
import { SidebarCloseIcon, Volume2, VolumeOff } from "lucide-react";
import { useState } from "react";
import { useChatStore } from "@/stores/chatStore";

import AssistantVoiceVisualizer from "./assistant-voice-visualizer";

const SideMenu = () => {
  const { currentSessions } = useSessionStore();
  const { toggleSpeech, enableSpeech } = useChatStore();
  const [toggleSidebar, setToggleSidebar] = useState(true);

  if (!toggleSidebar)
    return (
      <Button
        variant="secondary"
        className="absolute top-0 left-0 m-2 z-50"
        onClick={() => setToggleSidebar(true)}
      >
        <SidebarCloseIcon />
      </Button>
    );

  return (
    <div className="border-r-2 border-zinc-500 p-4 relative w-75 flex flex-col h-full">
      <div className="absolute top-0 right-0 m-2 flex gap-2">
        <Button variant="secondary" onClick={toggleSpeech}>
          {enableSpeech ? <Volume2 /> : <VolumeOff />}
        </Button>
        <Button variant="secondary" onClick={() => setToggleSidebar(false)}>
          <SidebarCloseIcon />
        </Button>
      </div>

      <h1 className="font-bold text-xl">N.I.N.A AI Agent</h1>
      <p className="mb-4">Browse chat sessions</p>

      <CreateSessionBtn />

      <div className="flex-1">
        {currentSessions.map((session) => (
          <ChatSelectBtn session={session} key={session.id} />
        ))}
      </div>

      <div className="mt-auto border-t-2 pt-4">
        <AssistantVoiceVisualizer />
      </div>
    </div>
  );
};

export default SideMenu;
