from abc import ABC, abstractmethod
from fastapi import Request, Response


class WhatsAppProvider(ABC):
    """Common interface every WhatsApp provider must implement."""

    @abstractmethod
    async def send_message(self, to: str, body: str) -> dict:
        """Send a text message to a phone number."""
        ...

    @abstractmethod
    async def parse_incoming(self, request: Request) -> list[tuple[str, str]]:
        """Parse an inbound webhook payload.
        Returns a list of (sender_phone, message_text) tuples.
        Silently drops status updates, reactions, etc.
        """
        ...

    @abstractmethod
    async def handle_verification(self, request: Request) -> Response:
        """Handle the provider's webhook verification handshake (GET)."""
        ...
