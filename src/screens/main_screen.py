from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static

from ..widgets.chat_view import ChatView
from ..widgets.input_bar import InputBar
from ..widgets.message import MessageWidget
from ..api.deepseek import DeepSeekClient, DeepSeekError
from ..tools.registry import ToolRegistry
from ..agent.agent import Agent, AgentEvent


class MainScreen(Screen):
    BINDINGS = [
        ("ctrl+q", "quit"),
    ]

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = DeepSeekClient(api_key)
        self.registry = ToolRegistry()
        self.agent = Agent(self.client, self.registry)
        self._msg: MessageWidget | None = None

    def compose(self):
        yield Header(show_clock=True)
        yield Static(" DeepSeek TUI  |  Ctrl+Q quit", id="status-bar")
        yield ChatView()
        yield InputBar()

    def on_input_bar_submitted(self, event: InputBar.Submitted):
        self._msg = None
        self.run_worker(self._run(event.text), exclusive=True)

    def action_quit(self):
        async def q():
            await self.client.close()
            self.app.exit()
        self.run_worker(q(), exclusive=True)

    async def _run(self, text: str):
        chat = self.query_one(ChatView)
        inp = self.query_one(InputBar)
        inp.set_loading(True)

        await chat.add_message("user", text)
        self._msg = await chat.add_message("assistant", "")

        try:
            async for ev in self.agent.run(text):
                if ev.type == "text_chunk":
                    self._msg.append_content(ev.data["text"])
                elif ev.type == "tool_start":
                    self._msg.add_tool_call(ev.data["name"], str(ev.data.get("arguments", "")))
                elif ev.type == "tool_result":
                    self._msg.add_tool_result(ev.data["result"])
        except DeepSeekError as e:
            self._msg.update_content(f"[red]Error: {e}[/red]")
        except Exception as e:
            self._msg.update_content(f"[red]Error: {e}[/red]")
        finally:
            inp.set_loading(False)
