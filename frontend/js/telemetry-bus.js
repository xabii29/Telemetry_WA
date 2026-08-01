export class TelemetryBus {
  #listeners = new Map();

  subscribe(eventName, listener) {
    const listeners = this.#listeners.get(eventName) ?? new Set();
    listeners.add(listener);
    this.#listeners.set(eventName, listeners);
    return () => listeners.delete(listener);
  }

  publish(event) {
    for (const listener of this.#listeners.get(event.name) ?? []) listener(event);
  }
}
