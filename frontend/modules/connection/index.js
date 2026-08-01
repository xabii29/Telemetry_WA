export function mountConnectionModule(bus, element) {
  const unsubscribeLost = bus.subscribe("connection_lost", () => { element.textContent = "Sin conexión"; });
  const unsubscribeRestored = bus.subscribe("connection_restored", () => { element.textContent = "Conectado"; });
  return () => {
    unsubscribeLost();
    unsubscribeRestored();
  };
}
