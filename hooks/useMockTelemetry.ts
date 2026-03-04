import { useEffect, useState } from "react";

export default function useMockTelemetry() {
  const [logs, setLogs] = useState<string[]>([
    "[00:00:01] INGEST: PM_Kisan_Docs.pdf",
    "[00:00:02] CHUNK: divided into 42 vectors",
  ]);

  const [chartData, setChartData] = useState(() => [
    { name: "Lottery", value: 45 },
    { name: "KYC Fraud", value: 30 },
    { name: "Job Scam", value: 25 },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const t = now.toLocaleTimeString();
      const entry = `[${t}] INGEST: sample_doc_${Math.floor(Math.random() * 100)}.pdf`;
      setLogs((s) => [...s.slice(-80), entry]);

      // mutate chart data slightly
      setChartData((data) => data.map((d) => ({ ...d, value: Math.max(5, Math.min(95, d.value + (Math.random() - 0.5) * 6)) })));
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return { logs, chartData } as const;
}
