// Minimal WebSocket client stub. Replace URL and implement reconnection/authorization as needed.
export function createTelemetrySocket(url: string) {
  const ws = new WebSocket(url);

  ws.onopen = () => console.log("ws open", url);
  ws.onclose = () => console.log("ws closed");
  ws.onerror = (e) => console.error("ws error", e);

  return ws;
}
