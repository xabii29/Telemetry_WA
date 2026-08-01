"""Async UDP acquisition with a bounded boundary and no UI knowledge."""
from __future__ import annotations

import asyncio
from collections.abc import Callable


class DatagramReceiver(asyncio.DatagramProtocol):
    def __init__(self, on_datagram: Callable[[bytes], None]) -> None:
        self._on_datagram = on_datagram

    def datagram_received(self, data: bytes, _address: object) -> None:
        self._on_datagram(data)


async def listen(host: str, port: int, on_datagram: Callable[[bytes], None]) -> asyncio.BaseTransport:
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: DatagramReceiver(on_datagram), local_addr=(host, port)
    )
    return transport
