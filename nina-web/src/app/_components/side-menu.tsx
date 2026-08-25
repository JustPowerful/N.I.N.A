import CreateSessionBtn from "./create-session-btn";
import { useSessionStore } from "@/stores/sessionStore";
import ChatSelectBtn from "./chat-select-btn";
import { Button } from "@/components/ui/button";
import { SidebarCloseIcon } from "lucide-react";
import { useState } from "react";

const SideMenu = () => {
  const { currentSessions } = useSessionStore();
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
    <div className="border-r-2 border-zinc-500 p-4 relative w-75">
      <Button
        variant="secondary"
        className="absolute top-0 right-0 m-2"
        onClick={() => setToggleSidebar(false)}
      >
        <SidebarCloseIcon />
      </Button>
      <h1 className="font-bold text-xl">N.I.N.A AI Agent</h1>
      <p className="mb-4">Browse chat sessions</p>

      <CreateSessionBtn />

      <div>
        {currentSessions.map((session) => (
          <ChatSelectBtn session={session} key={session.id} />
        ))}
      </div>
    </div>
  );
};

export default SideMenu;
