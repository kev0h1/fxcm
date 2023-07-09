import abc
import asyncio

from src.logger import get_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_layer.uow import MongoUnitOfWork


logger = get_logger(__name__)


class EventBus(abc.ABC):
    @abc.abstractmethod
    def publish(self, event):
        pass

    @abc.abstractmethod
    def subscribe(self, event_type, handler):
        pass


class TradingEventBus(EventBus):
    """Unified event bus for trading events

    Args:
        EventBus (_type_): _description_
    """

    class StopEvent:
        """Unique class used as a sentinel to stop the event loop."""

    def __init__(self, uow: "MongoUnitOfWork"):
        self.handlers = {}
        self.queue = asyncio.Queue()
        self.running = False
        self.uow = uow

    async def publish(self, event):
        """Publish an event to the event bus

        Args:
            event (_type_): _description_
        """
        await self.queue.put(event)

    def subscribe(self, event_type, handler):
        """Subscribe to an event -
        do not make async"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def start(self):
        """Starts the event loop."""
        if self.running:
            return

        logger.info("Event loop for event bus started")
        self.running = True
        while True:
            event = await self.queue.get()
            if isinstance(event, self.StopEvent):
                break

            event_type = type(event)

            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    async with self.uow:
                        await handler(event, self.uow)

        self.running = False

    async def stop(self):
        """Stops the event loop by putting a StopEvent in the queue."""
        await self.queue.put(self.StopEvent())
