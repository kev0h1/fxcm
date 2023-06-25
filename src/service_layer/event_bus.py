import abc


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

    def __init__(self):
        self.handlers = {}

    async def publish(self, event):
        """Publish an event to the event bus

        Args:
            event (_type_): _description_
        """
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(event)

    def subscribe(self, event_type, handler):
        """Subscribe to an event -
        do not make async"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
