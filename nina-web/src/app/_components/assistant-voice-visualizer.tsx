"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowDownToLine, Move, Maximize2 } from "lucide-react";
import { VoiceOrb, useAudioAnalyser } from "react-ai-voice-visualizer";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/stores/chatStore";

const AssistantVoiceVisualizer = () => {
  const { assistantAudio, clearAssistantAudio, isLoading } = useChatStore();
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isFloating, setIsFloating] = useState(false);
  const [position, setPosition] = useState({
    x: 0,
    y: 0,
  });
  const dragState = useRef<{
    dragging: boolean;
    offsetX: number;
    offsetY: number;
  }>({ dragging: false, offsetX: 0, offsetY: 0 });

  const floatingStyle = useMemo(
    () => ({
      left: `${position.x}px`,
      top: `${position.y}px`,
    }),
    [position.x, position.y],
  );

  const startFloating = () => {
    const width = 320;
    const height = 380;
    setPosition({
      x: Math.max(16, window.innerWidth - width - 32),
      y: Math.max(16, window.innerHeight - height - 32),
    });
    setIsFloating(true);
  };

  const dockBack = () => {
    setIsFloating(false);
    dragState.current.dragging = false;
  };

  // Create an audio element and connect it to an AudioContext for analysis
  useEffect(() => {
    if (!assistantAudio) return;

    // create audio element
    const audio = new Audio(`data:audio/wav;base64,${assistantAudio}`);
    audio.crossOrigin = "anonymous";

    // create audio context and connect
    const ctx = new (
      window.AudioContext || (window as any).webkitAudioContext
    )();
    const src = ctx.createMediaElementSource(audio);
    const dest = ctx.createMediaStreamDestination();
    src.connect(dest);
    src.connect(ctx.destination);

    // expose the MediaStream for useAudioAnalyser
    const mstream = dest.stream;
    setStream(mstream);

    audio.play().catch(() => {
      // resume context on interaction
      ctx
        .resume()
        .then(() => audio.play())
        .catch(() => {});
    });

    const onEnded = () => {
      clearAssistantAudio();
      try {
        ctx.close();
      } catch (e) {}
      setStream(null);
    };

    audio.addEventListener("ended", onEnded);

    return () => {
      audio.pause();
      audio.removeEventListener("ended", onEnded);
      try {
        ctx.close();
      } catch (e) {}
      setStream(null);
    };
  }, [assistantAudio, clearAssistantAudio]);

  useEffect(() => {
    if (!isFloating) return;

    const onPointerMove = (event: PointerEvent) => {
      if (!dragState.current.dragging) return;

      setPosition({
        x: event.clientX - dragState.current.offsetX,
        y: event.clientY - dragState.current.offsetY,
      });
    };

    const onPointerUp = () => {
      dragState.current.dragging = false;
    };

    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);

    return () => {
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
    };
  }, [isFloating]);

  const { frequencyData, volume } = useAudioAnalyser(stream, {
    fftSize: 512,
    smoothingTimeConstant: 0.8,
  });

  const state = isLoading ? "thinking" : assistantAudio ? "speaking" : "idle";

  const visualizer = (
    <div className="flex items-center justify-center py-4">
      <VoiceOrb
        noiseSpeed={2}
        audioData={frequencyData}
        volume={volume}
        state={state}
        size={140}
        primaryColor="#06B6D4"
        secondaryColor="#8B5CF6"
      />
    </div>
  );

  if (isFloating) {
    return (
      <div
        className="fixed z-100 w-[320px] rounded-2xl border border-white bg-black text-white shadow-2xl"
        style={floatingStyle}
      >
        <div
          className="flex items-center justify-between border-b border-white/30 px-3 py-2 text-sm"
          onPointerDown={(event) => {
            dragState.current.dragging = true;
            dragState.current.offsetX = event.clientX - position.x;
            dragState.current.offsetY = event.clientY - position.y;
          }}
        >
          <div className="flex items-center gap-2 select-none">
            <Move className="h-4 w-4" />
            <span>Assistant Voice</span>
          </div>
          <Button
            size="sm"
            variant="secondary"
            className="bg-white text-black hover:bg-zinc-200"
            onClick={dockBack}
          >
            <ArrowDownToLine className="h-4 w-4" />
          </Button>
        </div>
        {visualizer}
      </div>
    );
  }

  return (
    <div className="border-t border-zinc-700 pt-4">
      <div className="mb-3 flex items-center justify-between text-xs text-zinc-400">
        <span>Assistant voice</span>
        <Button
          size="sm"
          variant="secondary"
          onClick={startFloating}
          className="h-7 bg-zinc-900 text-white hover:bg-zinc-800"
        >
          <Maximize2 className="h-4 w-4" />
        </Button>
      </div>
      {visualizer}
    </div>
  );
};

export default AssistantVoiceVisualizer;
