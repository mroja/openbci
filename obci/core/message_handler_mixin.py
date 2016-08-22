
import asyncio
import types
from typing import Optional, Callable, Union

from obci.core.messages import Message

# TODO: this should be union of types.CoroutineType with proper parameters and Callable
# TODO: wait for proper coroutines support in typing module
HandlerType = Union[Callable[[Message], Optional[Message]], Callable[[Message], types.CoroutineType]]


class MessageHandlerMixin:

    def __init__(self) -> None:
        """
        Implements common message handling interface used by Peer and Broker classes.
        """
        self._message_handlers = {}
        super().__init__()

    def register_message_handler(self,
                                 msg_type: str,
                                 handler: HandlerType) -> None:
        """
        Register `handler` function to be called when message with `msg_type` arrives.

        Args:
            msg_type: Message type string.
            handler: Function called when new message arrives.
        """
        self._message_handlers[msg_type] = handler

    def unregister_message_handler(self, msg_type: str) -> None:
        """
        Unregister previously registered message handler.

        Args:
            msg_type: Message type string.
        """
        del self._message_handlers[msg_type]

    async def handle_message(self, msg: Message) -> Optional[Message]:
        """
        Called by message dispatching loop when new message arrives.

        Args:
            msg: message to handle

        Returns:
            value returned by handler

        Raises:
            KeyError: when handler for `msg.type` is not registered
        """
        response = self._message_handlers[msg.type](msg)
        if asyncio.iscoroutine(response):
            return await response
        else:
            return response
