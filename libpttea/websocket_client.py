"""
libpttea.websocket_client
~~~~~~~~~~~~

This module provides the WebSocket client for connecting to PTT.
"""

import asyncio
import logging

from websockets.asyncio.client import connect
import websockets.asyncio.client

logger = logging.getLogger("websocket_client")


class WebSocketClient:

    def __init__(self, url="wss://ws.ptt.cc/bbs/", origin="https://term.ptt.cc") -> None:
        self.url = url
        self.origin = origin
        self.ws_queue = asyncio.Queue()
        self.connected = asyncio.Event()
        self.ws_connection: websockets.asyncio.client.ClientConnection | None = None

        self.send_queue = asyncio.Queue()
        self.handlers_tasks = []

    async def connect(self) -> None:
        """Connect to PTT."""

        self.ws_connection = await connect(self.url, origin=self.origin)
        self.connected.set()
        logger.info("Connection opened")

        self.handlers_tasks.append(asyncio.create_task(self.listen()))
        self.handlers_tasks.append(asyncio.create_task(self.sender()))
        # asyncio.gather( *self.handlers )
        

    async def listen(self) -> None:
        """Listen for messages from the WebSocket connection."""
        try:
            async for message in self.ws_connection:
                self.ws_queue.put_nowait(message)
                logger.debug(f"receive >>({message.decode("utf-8", errors="ignore")})\n")

        except websockets.ConnectionClosed as e:
            logger.info(f"WebSocket closed: {e}")
            self.connected.clear()

    async def sender(self) -> None:
        """Send a message through the WebSocket connection."""
        if self.ws_connection and self.connected.is_set():

            while True:
                message = await self.send_queue.get()
                await self.ws_connection.send(message)
                logger.debug(f"Sent: {message}")
            
        else:
            logger.error("Cannot send message, WebSocket is not connected")


    def send(self, message: str) -> None:
        """Send a message through the WebSocket connection."""
        self.send_queue.put_nowait(message)
        

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.ws_connection:
            await self.ws_connection.close()
            # ---

            for t in self.handlers_tasks:
                t.cancel()


            for t in self.handlers_tasks:
                try:
                    await t

                except asyncio.CancelledError:
                    pass
                    # print("canceled")


            logger.info("Connection closed manually")
            self.connected.clear()

    