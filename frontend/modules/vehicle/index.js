export function mountVehicleModule(bus, element) {
  return bus.subscribe("packet", ({ payload }) => {
    const vehicle = payload.packet.vehicle;
    element.textContent = vehicle ? `Auto #${vehicle.ordinal}` : "Esperando vehículo";
  });
}
