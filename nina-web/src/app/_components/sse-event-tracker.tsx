import api from "@/lib/api/axios-instance";
import axios from "axios";
import { useEffect, useState } from "react";

type AgentEventState =
  | "agent.started"
  | "agent.tool_started"
  | "agent.tool_executed"
  | "agent.tool_failed"
  | "agent.completed";

const SseEventTracker = ({ sessionId }: { sessionId: string }) => {
  const [event, setEvent] = useState<{
    name: AgentEventState;
    data: {
      tool: string;
      call_id: string;
      arguments: {
        [key: string]: any;
      };
    };
  } | null>(null);

  useEffect(() => {
    console.log("Initializing SSE connection for session:", sessionId);
    const controller = new AbortController();
    const connectToSse = async () => {
      try {
        const response = await api.get(`/chat/events/${sessionId}`, {
          signal: controller.signal,
          responseType: "stream",
          adapter: "fetch",
        });

        const stream = response.data as ReadableStream<Uint8Array>;
        const reader = stream.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          const events = chunk
            .split("\n\n")
            .filter((event) => event.trim() !== "");
          /**
             * event format is like this:
             * 
             * event: agent.tool_started
                data: {"tool": "save_knowledge", "call_id": "call-3b3a2fc0-b577-4cf9-86b8-8bb1ce608bd0", "arguments": {"content": "Ahmed is a backend engineer specialized in AI Automation and management systems."}}
             */
          for (const event of events) {
            if (event.startsWith("event: ")) {
              //   extract event name
              const eventName = event
                .split("\n")[0]
                .replace("event: ", "")
                .trim()
                .replace(/[^a-zA-Z0-9._-]/g, "") as AgentEventState;
              const eventData = JSON.parse(
                event.split("\n").slice(1).join("\n").replace("data: ", ""),
              );
              setEvent({ name: eventName, data: eventData });
              console.log("Received SSE event:", eventName, eventData);
            }
          }
        }
      } catch (error) {
        if (!axios.isCancel(error)) {
          console.error("Error connecting to SSE:", error);
        }
      }
    };
    if (sessionId) {
      connectToSse();
    }
  }, [sessionId]);
  return (
    <div className="sticky w-fit bottom-px left-1/2 -translate-x-1/2 z-10">
      <ul className="space-y-2">
        {event ? (
          <li className="bg-gray-800/80 backdrop-blur-3xl p-2 rounded-2xl flex items-center gap-2">
            {event.name === "agent.tool_started" && (
              <div className="h-3 w-3 bg-green-400 rounded-full animate-caret-blink"></div>
            )}
            {event.name === "agent.tool_executed" && (
              <div className="h-3 w-3 bg-orange-400 rounded-full"></div>
            )}
            {event.name === "agent.tool_failed" && (
              <div className="h-3 w-3 bg-red-400 rounded-full"></div>
            )}
            <p className="text-sm text-gray-400">
              {event.name === "agent.tool_started" &&
                "Running tool: " + event.data.tool}
              {event.name === "agent.tool_executed" &&
                "Tool executed: " + event.data.tool}
              {event.name === "agent.tool_failed" &&
                "Tool failed: " + event.data.tool}
            </p>
          </li>
        ) : (
          <li className="text-gray-500">No events yet...</li>
        )}
      </ul>
    </div>
  );
};

export default SseEventTracker;
