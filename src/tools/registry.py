from .base import Tool
from .tools import ReadTool, WriteTool, EditTool, BashTool, GlobTool, GrepTool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._register_defaults()

    def _register_defaults(self):
        for tool_cls in [ReadTool, WriteTool, EditTool, BashTool, GlobTool, GrepTool]:
            tool = tool_cls()
            self._tools[tool.name] = tool

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def to_openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]

    async def execute(self, name: str, **kwargs) -> str:
        tool = self.get(name)
        if not tool:
            return f"错误：未知工具 '{name}'"
        return await tool.execute(**kwargs)
