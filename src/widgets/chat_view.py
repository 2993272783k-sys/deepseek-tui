from textual.widgets import Static
from textual.widget import Widget
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from .message import MessageWidget


class ChatView(Widget):
    """Scrollable chat message container."""

    DEFAULT_CSS = """
    ChatView {
        height: 1fr;
    }

    #chat-scroll {
        height: 100%;
        overflow-y: auto;
        padding: 0 1;
    }
    """

    def compose(self):
        self._scroll = VerticalScroll(id="chat-scroll")
        yield self._scroll

    async def add_user_message(self, content: str):
        msg = MessageWidget("user", content)
        await self._scroll.mount(msg)
        self._scroll.scroll_end(animate=False)

    async def add_assistant_message(self) -> MessageWidget:
        msg = MessageWidget("assistant")
        await self._scroll.mount(msg)
        self._scroll.scroll_end(animate=False)
        return msg

    async def add_welcome_message(self):
        msg = MessageWidget("assistant", "")
        msg._content = "你好！我是 DeepSeek 编程助手，有什么需要帮忙的吗？"
        msg._render()
        await self._scroll.mount(msg)
