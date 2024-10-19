"""
libpttea.websocket_client
~~~~~~~~~~~~

This module provides the WebSocket client for connecting to PTT.
"""

import asyncio
import logging

import websockets.asyncio.client


logger = logging.getLogger("websocket_client")


class WebSocketClient:

    def __init__(self, url="wss://ws.ptt.cc/bbs/", origin="https://term.ptt.cc") -> None:

        self.url = url
        self.origin = origin

        self.receive_queue = asyncio.Queue()
        self.send_queue = asyncio.Queue()

        self.connection: websockets.asyncio.client.ClientConnection = None
        self.connected = asyncio.Event()

        self.handler_tasks = []

    async def __receive_handler(self) -> None:
        """Handler to receive messages from the WebSocket connection."""

        try:
            async for message in self.connection:
                self.receive_queue.put_nowait(message)

                if logger.level <= logging.DEBUG:
                    logger.debug(f"receive >>{message.decode("utf-8", errors="ignore")}<<\n")

        except websockets.ConnectionClosed as e:
            logger.info(f"WebSocket ConnectionClosed: {e}")

            self.connected.clear()
            # ! raise

    async def __send_handler(self) -> None:
        """Handler to send messages to the WebSocket connection."""

        if (self.connection is not None) and self.connected.is_set():
            while True:
                message = await self.send_queue.get()
                await self.connection.send(message)
                logger.debug(f"Sent: {message}")

        else:
            logger.error("Cannot send message, WebSocket is not connected")

    async def connect(self) -> None:
        """Create connection."""

        self.connection = await websockets.asyncio.client.connect(self.url, origin=self.origin)
        self.connected.set()
        logger.info("Connected")

        self.handler_tasks.append(asyncio.create_task(self.__receive_handler()))
        self.handler_tasks.append(asyncio.create_task(self.__send_handler()))

    def send(self, message: str) -> None:
        """Send messages to the WebSocket connection."""

        self.send_queue.put_nowait(message)

    async def close(self) -> None:
        """Close the WebSocket connection."""

        if self.connection:
            await self.connection.close()

            for task in self.handler_tasks:
                task.cancel()

            # wait for all tasks to cancel
            for task in self.handler_tasks:
                try:
                    await task
                except asyncio.CancelledError:
                    logger.debug(f"task canceled , {task}")

            self.connected.clear()
            logger.info("Connection closed manually")

        else:
            raise RuntimeError("WebSocket is not connected")
