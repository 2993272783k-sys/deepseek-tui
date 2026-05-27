from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input
from textual.message import Message


class InputBar(Widget):
    """Bottom input bar."""

    class Submitted(Message):
        def __init__(self, text: str):
            super().__init__()
            self.text = text

    def compose(self):
        self._input = Input(placeholder="输入消息后回车发送...")
        yield self._input

    def on_mount(self):
        self._input.focus()

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        if text:
            self.post_message(self.Submitted(text))
            self._input.clear()

    def set_loading(self, loading: bool):
        self._input.disabled = loading
        if not loading:
            self._input.focus()
