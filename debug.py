#!/usr/bin/env python3
"""DeepSeek TUI 诊断工具 - 排查闪退问题"""

import os
import sys
import traceback

def main():
    print("=" * 50)
    print("DeepSeek TUI 诊断工具")
    print("=" * 50)

    # 1. Check Python version
    print(f"\n[1] Python 版本: {sys.version}")

    # 2. Check dependencies
    print("\n[2] 检查依赖...")
    deps = {"textual": None, "httpx": None}
    for dep in deps:
        try:
            mod = __import__(dep)
            deps[dep] = mod.__version__
            print(f"    ✓ {dep} {mod.__version__}")
        except ImportError as e:
            print(f"    ✗ {dep}: {e}")

    # 3. Check API key
    print("\n[3] 检查 API Key...")
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("DEEPSEEK_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break
    if api_key:
        print(f"    ✓ API Key 已配置 ({api_key[:8]}...)")
    else:
        print("    ✗ 未找到 API Key")

    # 4. Test console encoding
    print("\n[4] 控制台编码...")
    import locale
    print(f"    locale: {locale.getpreferredencoding()}")
    print(f"    stdout: {sys.stdout.encoding}")
    print(f"    stdin:  {sys.stdin.encoding}")

    # 5. Test Chinese output
    print("\n[5] 中文显示测试...")
    print("    你好世界！测试中文显示。")

    # 6. Test rich rendering
    print("\n[6] Rich 渲染测试...")
    try:
        from rich.console import Console
        from rich.panel import Panel
        c = Console()
        c.print(Panel("测试 Panel 渲染"), width=50)
        print("    ✓ Rich 渲染正常")
    except Exception as e:
        print(f"    ✗ Rich 渲染失败: {e}")

    # 7. Try minimal Textual startup
    print("\n[7] Textual 启动测试...")
    try:
        import asyncio
        from textual.app import App
        from textual.widgets import Static, Input

        class MiniApp(App):
            CSS = "Static { height: 1fr; } Input { dock: bottom; height: 3; }"
            def compose(self):
                yield Static("测试")
                yield Input()

        async def test():
            app = MiniApp()
            async with app.run_test(size=(80, 24)) as pilot:
                await asyncio.sleep(0.2)
                print("    ✓ Textual 应用启动成功")
                pilot.app.exit()
                await asyncio.sleep(0.1)

        asyncio.run(test())
    except Exception as e:
        print(f"    ✗ Textual 启动失败: {e}")
        traceback.print_exc()

    # 8. Try real app startup
    print("\n[8] 完整应用启动测试...")
    try:
        import asyncio
        sys.path.insert(0, os.path.dirname(__file__))
        from src.app import DeepSeekTUI

        async def test_full():
            app = DeepSeekTUI(api_key=api_key)
            async with app.run_test(size=(80, 24)) as pilot:
                await asyncio.sleep(0.3)
                print("    ✓ 完整应用启动成功")
                # Check all widgets
                from src.widgets.chat_view import ChatView
                from src.widgets.input_bar import InputBar
                cv = app.screen.query_one(ChatView)
                ib = app.screen.query_one(InputBar)
                print(f"    ✓ ChatView: {cv is not None}")
                print(f"    ✓ InputBar: {ib is not None}")
                pilot.app.exit()
                await asyncio.sleep(0.2)

        asyncio.run(test_full())
    except Exception as e:
        print(f"    ✗ 完整应用启动失败: {e}")
        traceback.print_exc()

    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
