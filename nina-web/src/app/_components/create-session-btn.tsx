import { Button } from "@/components/ui/button";
import React, { useState } from "react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Input } from "@/components/ui/input";

import { useSessionStore } from "@/stores/sessionStore";

const CreateSessionBtn = () => {
  const [toggleCreate, setToggleCreate] = useState(false);
  const [sessionTitle, setSessionTitle] = useState("");
  const { createSession } = useSessionStore();
  return (
    <React.Fragment>
      <Button className="w-full mb-2" onClick={() => setToggleCreate(true)}>
        Create New Session
      </Button>

      <Dialog open={toggleCreate} onOpenChange={setToggleCreate}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Session</DialogTitle>
            <DialogDescription>
              Please enter a title for your new session. This will help you
              identify it later.
            </DialogDescription>
          </DialogHeader>
          <Input
            placeholder="Session Title"
            value={sessionTitle}
            onChange={(e) => setSessionTitle(e.target.value)}
          />
          <div className="flex gap-2">
            <Button
              onClick={() => setToggleCreate(false)}
              className="flex-1"
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              className="flex-1"
              onClick={() => {
                createSession(sessionTitle).then(() => {
                  setToggleCreate(false);
                  setSessionTitle("");
                });
              }}
            >
              Create Session
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </React.Fragment>
  );
};

export default CreateSessionBtn;
