from textual.widgets import Static
from rich.text import Text
from rich.panel import Panel
from rich.console import Group


class MessageWidget(Static):
    """A single chat message (user or assistant)."""

    def __init__(self, role: str, content: str = "", **kwargs):
        self.role = role
        self._content = content
        self._tool_items: list[tuple[str, str]] = []
        super().__init__("", **kwargs)

    def update_content(self, text: str):
        self._content = text
        self.refresh()

    def append_content(self, text: str):
        self._content += text
        self.refresh()

    def add_tool_call(self, name: str, args_text: str):
        self._tool_items.append(("call", f"\n🔧 {name}({args_text})"))
        self.refresh()

    def add_tool_result(self, result: str):
        preview = result[:200] + ("..." if len(result) > 200 else "")
        self._tool_items.append(("result", f"\n📋 {preview}"))
        self.refresh()

    def render(self):
        elements = []
        if self._content:
            elements.append(Text(self._content))
        for ttype, text in self._tool_items:
            style = "bold cyan" if ttype == "call" else "dim white"
            elements.append(Text(text, style=style))

        label = "你" if self.role == "user" else "DeepSeek"
        label_style = "bold green" if self.role == "user" else "bold blue"
        border_style = "green" if self.role == "user" else "blue"

        return Panel(
            Group(*elements) if elements else Text("（等待响应...）"),
            title=Text(label, style=label_style),
            border_style=border_style,
            padding=(0, 1),
        )
