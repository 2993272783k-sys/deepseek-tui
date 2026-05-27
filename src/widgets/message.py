from textual.widgets import Static
from rich.text import Text
from rich.console import Group


class MessageWidget(Static):
    """A single chat message, using Textual-native rendering."""

    def __init__(self, role: str, content: str = "", **kwargs):
        self.role = role
        self._content = content
        self._tool_items: list[tuple[str, str]] = []
        super().__init__("", **kwargs)
        self._update_classes()

    def _update_classes(self):
        self.classes = f"message {self.role}"

    def update_content(self, text: str):
        self._content = text
        self.refresh()

    def append_content(self, text: str):
        self._content += text
        self.refresh()

    def add_tool_call(self, name: str, args_text: str):
        self._tool_items.append(("call", f">> {name}({args_text})"))
        self.refresh()

    def add_tool_result(self, result: str):
        preview = result[:200] + ("..." if len(result) > 200 else "")
        self._tool_items.append(("result", f"={preview}"))
        self.refresh()

    def render(self):
        elements = []
        header = Text()
        if self.role == "user":
            header.append("You", style="bold green")
        else:
            header.append("DeepSeek", style="bold blue")

        elements.append(header)

        if self._content:
            elements.append(Text("\n" + self._content))

        for ttype, text in self._tool_items:
            style = "bold cyan" if ttype == "call" else "dim white"
            elements.append(Text("\n" + text, style=style))

        return Group(*elements) if elements else Text("(thinking...)")
