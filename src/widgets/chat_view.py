from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from .message import MessageWidget


class ChatView(Widget):
    """Scrollable chat area."""

    def compose(self):
        self._scroll = VerticalScroll(id="chat-scroll")
        yield self._scroll

    async def on_mount(self):
        msg = MessageWidget("assistant", "Hello! I'm DeepSeek assistant. How can I help?")
        await self._scroll.mount(msg)
        self._scroll.scroll_end(animate=False)

    async def add_message(self, role: str, content: str = "") -> MessageWidget:
        msg = MessageWidget(role, content)
        await self._scroll.mount(msg)
        if content:
            self._scroll.scroll_end(animate=False)
        return msg
