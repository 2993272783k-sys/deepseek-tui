from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static
from textual.containers import VerticalScroll

from ..widgets.chat_view import ChatView
from ..widgets.input_bar import InputBar
from ..widgets.message import MessageWidget
from ..api.deepseek import DeepSeekClient, DeepSeekError
from ..tools.registry import ToolRegistry
from ..agent.agent import Agent, AgentEvent


class MainScreen(Screen):
    BINDINGS = [
        ("ctrl+q", "quit", "退出"),
    ]

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = DeepSeekClient(api_key)
        self.registry = ToolRegistry()
        self.agent = Agent(self.client, self.registry)
        self.current_msg: MessageWidget | None = None

    def compose(self):
        yield Header(show_clock=True)
        yield Static(" DeepSeek TUI  |  Ctrl+Q 退出", id="status-bar")
        yield ChatView()
        yield InputBar()

    def on_mount(self):
        pass

    def on_input_bar_submitted(self, event: InputBar.Submitted):
        self.current_msg = None
        self.run_worker(self._run_agent(event.text), exclusive=True)

    def action_quit(self):
        async def _quit():
            await self.client.close()
            self.app.exit()
        self.run_worker(_quit(), exclusive=True)

    async def _run_agent(self, user_message: str):
        chat = self.query_one(ChatView)
        input_bar = self.query_one(InputBar)
        input_bar.set_loading(True)

        await chat.add_user_message(user_message)
        msg = await chat.add_assistant_message()
        self.current_msg = msg

        try:
            async for event in self.agent.run(user_message):
                if event.type == "text_chunk":
                    msg.append_content(event.data["text"])
                elif event.type == "tool_start":
                    name = event.data["name"]
                    args = event.data["arguments"]
                    args_str = ", ".join(f"{k}={v}" for k, v in args.items())
                    msg.add_tool_call(name, args_str)
                elif event.type == "tool_result":
                    msg.add_tool_result(event.data["result"])
                elif event.type == "error":
                    msg.update_content(f"错误: {event.data['message']}")

        except DeepSeekError as e:
            if self.current_msg:
                self.current_msg.update_content(f"发生错误: {e}")
        except Exception as e:
            if self.current_msg:
                self.current_msg.update_content(f"遇到错误: {e}")
        finally:
            input_bar.set_loading(False)
