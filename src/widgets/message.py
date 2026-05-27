from textual.widgets import Static


class MessageWidget(Static):
    """A chat message. Uses Textual-native rendering with CSS."""

    def __init__(self, role: str, content: str = "", **kwargs):
        self.role = role
        self._text = content
        super().__init__(content, **kwargs)
        self.classes = f"message {role}"

    @property
    def text(self):
        return self._text

    def update_content(self, content: str):
        self._text = content
        self.update(content)

    def append_content(self, content: str):
        self._text += content
        self.update(self._text)

    def add_tool_call(self, name: str, args: str):
        line = f"\n  [cyan]> {name}({args})[/cyan]"
        self._text += line
        self.update(self._text)

    def add_tool_result(self, result: str):
        preview = result[:200] + ("..." if len(result) > 200 else "")
        line = f"\n  [dim]=> {preview}[/dim]"
        self._text += line
        self.update(self._text)
