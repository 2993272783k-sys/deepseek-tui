from textual.widgets import Static
from textual.app import ComposeResult
from rich.text import Text
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.console import Group
from textual.reactive import reactive


class MessageWidget(Static):
    """A single chat message (user or assistant)."""

    def __init__(self, role: str, content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self._content = content
        self._tool_items: list[tuple[str, str]] = []  # (type, text)

    def update_content(self, text: str):
        self._content = text
        self._render()

    def append_content(self, text: str):
        self._content += text
        self._render()

    def add_tool_call(self, name: str, args_text: str):
        self._tool_items.append(("call", f"🔧 {name}({args_text})"))
        self._render()

    def add_tool_result(self, result: str):
        preview = result[:200] + ("..." if len(result) > 200 else "")
        self._tool_items.append(("result", preview))
        self._render()

    def _render(self):
        elements = []

        if self._content:
            elements.append(Text(self._content))

        for ttype, text in self._tool_items:
            if ttype == "call":
                elements.append(Text(text, style="bold cyan"))
            elif ttype == "result":
                elements.append(Text(text, style="dim white"))

        label = "你" if self.role == "user" else "DeepSeek"
        style = "bold green" if self.role == "user" else "bold blue"

        panel = Panel(
            Group(*elements) if elements else Text(""),
            title=Text(label, style=style),
            border_style="green" if self.role == "user" else "blue",
            padding=(0, 1),
        )
        self.update(panel)
