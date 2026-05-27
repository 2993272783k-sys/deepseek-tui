from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from .message import MessageWidget


class ChatView(Widget):
    """Scrollable chat message container."""

    def compose(self):
        self._scroll = VerticalScroll(id="chat-scroll")
        yield self._scroll

    async def on_mount(self):
        await self._add_welcome()

    async def _add_welcome(self):
        msg = MessageWidget("assistant", "Hello! I'm DeepSeek assistant. How can I help you?")
        await self._scroll.mount(msg)
        self._scroll.scroll_end(animate=False)

    async def add_user_message(self, content: str):
        msg = MessageWidget("user", content)
        await self._scroll.mount(msg)
        self._scroll.scroll_end(animate=False)
        return msg

    async def add_assistant_message(self) -> MessageWidget:
        self._current_msg = MessageWidget("assistant")
        await self._scroll.mount(self._current_msg)
        self._scroll.scroll_end(animate=False)
        return self._current_msg
