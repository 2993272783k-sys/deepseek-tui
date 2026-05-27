from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input
from textual.keys import Keys
from textual.binding import Binding
from textual.message import Message


class InputBar(Widget):
    """Bottom input bar with text input."""

    DEFAULT_CSS = """
    InputBar {
        height: 3;
        padding: 0 1;
        dock: bottom;
    }

    InputBar Input {
        width: 100%;
    }
    """

    class Submitted(Message):
        def __init__(self, text: str):
            super().__init__()
            self.text = text

    def compose(self):
        self._input = Input(placeholder="输入消息（Ctrl+C 发送，Ctrl+Q 退出）...")
        yield self._input

    def on_mount(self):
        self._input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        if text:
            self.post_message(self.Submitted(text))
            self._input.clear()
        event.stop()

    def set_loading(self, loading: bool):
        self._input.disabled = loading
