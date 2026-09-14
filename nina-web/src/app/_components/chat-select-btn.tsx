import React, { useState } from "react";
import { type Session, useSessionStore } from "@/stores/sessionStore";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { Loader2, Trash } from "lucide-react";

/**
 * Utility function to cut the string to a certain limit and add ellipsis if it exceeds the limit.
 * @param str The string to be cut.
 * @param limit The limit of the string length.
 */
function cutString(str: string, limit: number): string {
  if (str.length > limit) {
    return str.substring(0, limit) + "...";
  }
  return str;
}

const ChatSelectBtn = ({ session }: { session: Session }) => {
  /**
   * This component is used in the session chat selection on the side menu.
   */
  const { setCurrentSession, deleteSession, isLoading } = useSessionStore();
  // Component state
  const [toggleDelete, setToggleDelete] = useState(false);
  return (
    <React.Fragment>
      <div className="flex">
        <Button
          className="flex-1"
          variant="ghost"
          onClick={() => {
            setCurrentSession(session.id, session.title);
          }}
        >
          {cutString(session.title, 20)}
        </Button>
        <Button
          variant="destructive"
          onClick={() => {
            setToggleDelete(true);
          }}
        >
          <Trash />
        </Button>
      </div>

      {/* Delete dialog */}
      <Dialog open={toggleDelete} onOpenChange={setToggleDelete}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              Are you sure you want to delete this session?
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              session and remove all associated data.
            </DialogDescription>
          </DialogHeader>
          <div className="flex gap-2">
            <Button
              className="flex-1"
              variant="secondary"
              onClick={() => setToggleDelete(false)}
            >
              Cancel
            </Button>

            <Button
              className="flex-1"
              variant="destructive"
              onClick={() => {
                deleteSession(session.id).then(() => {
                  setToggleDelete(false);
                });
              }}
            >
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                "Delete"
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </React.Fragment>
  );
};

export default ChatSelectBtn;
