import { TelemetryBus } from "./telemetry-bus.js";
import { connectTelemetry } from "./socket.js";
import { mountConnectionModule } from "../modules/connection/index.js";
import { mountVehicleModule } from "../modules/vehicle/index.js";

const bus = new TelemetryBus();
mountConnectionModule(bus, document.querySelector("#connection"));
mountVehicleModule(bus, document.querySelector("#vehicle"));
connectTelemetry(bus, `ws://${location.host}/ws`);
