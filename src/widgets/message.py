from textual.widgets import Static


class MessageWidget(Static):
    """A chat message."""

    def __init__(self, role: str, content: str = "", **kwargs):
        self.role = role
        self._text = content
        # Always start with at least a space so widget has height
        display = content if content else " "
        super().__init__(display, **kwargs)
        self.classes = f"message {role}"

    def update_content(self, content: str):
        self._text = content
        self.update(content if content else " ")
        self.refresh()

    def append_content(self, content: str):
        self._text += content
        self.update(self._text)
        self.refresh()

    def add_tool_call(self, name: str, args: str):
        line = f"\n  [cyan]> {name}({args})[/cyan]"
        self._text += line
        self.update(self._text)
        self.refresh()

    def add_tool_result(self, result: str):
        preview = result[:200] + ("..." if len(result) > 200 else "")
        line = f"\n  [dim]=> {preview}[/dim]"
        self._text += line
        self.update(self._text)
        self.refresh()
