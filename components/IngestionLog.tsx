import React, { useRef, useEffect } from "react";

export default function IngestionLog({ logs }: { logs: string[] }) {
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="rounded-lg bg-slate-900 p-4 border border-white/5 h-96 overflow-auto font-mono text-sm">
      <h3 className="font-semibold mb-3">Ingestion Log</h3>
      <div className="space-y-2">
        {logs.map((l, i) => (
          <div key={i} className="text-slate-300">{l}</div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
