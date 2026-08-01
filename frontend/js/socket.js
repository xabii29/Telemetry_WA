export function connectTelemetry(bus, url) {
  const socket = new WebSocket(url);
  socket.addEventListener("message", ({ data }) => bus.publish(JSON.parse(data)));
  socket.addEventListener("close", () => bus.publish({ name: "connection_lost", payload: {} }));
  socket.addEventListener("open", () => bus.publish({ name: "connection_restored", payload: {} }));
  return socket;
}
