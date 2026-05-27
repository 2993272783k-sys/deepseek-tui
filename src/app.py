import os

from textual.app import App, ComposeResult
from .screens.main_screen import MainScreen


def load_env():
    """Load .env file from project root."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip("\"'")
                if key and not os.environ.get(key):
                    os.environ[key] = val


class DeepSeekTUI(App):
    """DeepSeek TUI - 终端 AI 编程助手"""

    CSS = """
    Screen {
        background: #1a1b26;
    }
    Header {
        background: #24283b;
        color: #c0caf5;
    }
    #status-bar {
        background: #24283b;
        color: #565f89;
        height: 1;
        padding: 0 1;
    }
    ChatView {
        height: 1fr;
    }
    #chat-scroll {
        height: 100%;
    }
    ChatView VerticalScroll {
        overflow-y: auto;
    }
    InputBar {
        dock: bottom;
        height: 3;
        padding: 0 1;
        background: #1a1b26;
    }
    InputBar Input {
        width: 100%;
    }
    """

    TITLE = "DeepSeek TUI"

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key

    def on_mount(self):
        self.push_screen(MainScreen(self.api_key))


def main():
    load_env()

    import argparse

    parser = argparse.ArgumentParser(description="DeepSeek TUI - 终端 AI 编程助手")
    parser.add_argument("--api-key", help="DeepSeek API Key")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误：请设置 DEEPSEEK_API_KEY 环境变量或使用 --api-key 参数")
        print("获取 API Key: https://platform.deepseek.com/api_keys")
        exit(1)

    app = DeepSeekTUI(api_key)
    app.run()


if __name__ == "__main__":
    main()
