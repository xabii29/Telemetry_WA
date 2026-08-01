"""In-process event delivery.  The API layer is one subscriber, not the owner."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable


EventHandler = Callable[["TelemetryEvent"], None]


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    name: str
    payload: dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, name: str, handler: EventHandler) -> Callable[[], None]:
        self._handlers[name].append(handler)

        def unsubscribe() -> None:
            if handler in self._handlers[name]:
                self._handlers[name].remove(handler)

        return unsubscribe

    def publish(self, event: TelemetryEvent) -> None:
        for handler in tuple(self._handlers[event.name]):
            handler(event)
