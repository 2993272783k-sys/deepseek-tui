import asyncio
import os
import re
from pathlib import Path

from .base import Tool


def _safe_path(base: str, target: str) -> Path:
    p = Path(target)
    if not p.is_absolute():
        p = Path(base) / p
    return p.resolve()


class ReadTool(Tool):
    name = "read"
    description = "读取文件内容。适用于查看代码、配置文件、文本文档等。"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要读取的文件路径（相对或绝对路径）",
            }
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str, **kwargs) -> str:
        path = _safe_path(os.getcwd(), file_path)
        if not path.exists():
            return f"错误：文件不存在 {path}"
        if not path.is_file():
            return f"错误：路径不是文件 {path}"
        try:
            content = path.read_text(encoding="utf-8")
            return f"文件 {path} 的内容：\n```\n{content}\n```"
        except Exception as e:
            return f"读取文件失败: {e}"


class WriteTool(Tool):
    name = "write"
    description = "创建新文件或完全覆盖已有文件的内容。适用于创建新文件、重写整个文件。"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要写入的文件路径（相对或绝对路径）",
            },
            "content": {
                "type": "string",
                "description": "要写入的文件内容",
            },
        },
        "required": ["file_path", "content"],
    }

    async def execute(self, file_path: str, content: str, **kwargs) -> str:
        path = _safe_path(os.getcwd(), file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"已写入文件 {path}（{len(content)} 字符）"
        except Exception as e:
            return f"写入文件失败: {e}"


class EditTool(Tool):
    name = "edit"
    description = "对文件进行精确的字符串替换编辑。适用于修改现有文件的部分内容。"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要编辑的文件路径",
            },
            "old_string": {
                "type": "string",
                "description": "要被替换的原始文本（必须在文件中唯一匹配）",
            },
            "new_string": {
                "type": "string",
                "description": "替换后的新文本",
            },
        },
        "required": ["file_path", "old_string", "new_string"],
    }

    async def execute(
        self, file_path: str, old_string: str, new_string: str, **kwargs
    ) -> str:
        path = _safe_path(os.getcwd(), file_path)
        if not path.exists():
            return f"错误：文件不存在 {path}"
        try:
            content = path.read_text(encoding="utf-8")
            count = content.count(old_string)
            if count == 0:
                return "错误：在文件中未找到匹配的文本"
            if count > 1:
                return f"错误：找到 {count} 处匹配，编辑需要唯一匹配"
            content = content.replace(old_string, new_string)
            path.write_text(content, encoding="utf-8")
            return f"已编辑文件 {path}，替换了 {len(old_string)} → {len(new_string)} 字符"
        except Exception as e:
            return f"编辑文件失败: {e}"


class BashTool(Tool):
    name = "bash"
    description = "在终端中执行 shell 命令。适用于运行代码、安装依赖、执行构建等。"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "要执行的 shell 命令",
            },
            "description": {
                "type": "string",
                "description": "命令用途的简短说明",
            },
            "timeout": {
                "type": "integer",
                "description": "超时时间（毫秒），默认 30000",
            },
        },
        "required": ["command", "description"],
    }

    async def execute(
        self, command: str, description: str = "", timeout: int = 30000, **kwargs
    ) -> str:
        timeout_s = max(5, timeout / 1000)
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd(),
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout_s
                )
            except asyncio.TimeoutError:
                proc.kill()
                return f"命令执行超时（{timeout_s}秒）"
            output = ""
            if stdout:
                output += stdout.decode("utf-8", errors="replace")
            if stderr:
                if output:
                    output += "\n--- stderr ---\n"
                output += stderr.decode("utf-8", errors="replace")
            result = f"命令: {command}\n退出码: {proc.returncode}"
            if output:
                result += f"\n输出:\n{output[:10000]}"
                if len(output) > 10000:
                    result += "\n...（输出已截断）"
            return result
        except Exception as e:
            return f"命令执行失败: {e}"


class GlobTool(Tool):
    name = "glob"
    description = "使用 glob 模式搜索文件。适用于查找特定类型的文件或按名称模式搜索。"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "glob 搜索模式，如 **/*.py 或 src/**/*",
            },
        },
        "required": ["pattern"],
    }

    async def execute(self, pattern: str, **kwargs) -> str:
        try:
            import glob as glob_mod

            base = os.getcwd()
            matches = glob_mod.glob(pattern, root_dir=base, recursive=True)
            matches = sorted(matches)[:200]
            if not matches:
                return f"未找到匹配 {pattern} 的文件"
            result = f"匹配 {pattern} 的文件（共 {len(matches)} 个）：\n"
            result += "\n".join(f"  {m}" for m in matches)
            return result
        except Exception as e:
            return f"搜索文件失败: {e}"


class GrepTool(Tool):
    name = "grep"
    description = "搜索文件内容中的文本模式。适用于查找代码中特定函数、变量、字符串等。"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "要搜索的正则表达式模式",
            },
            "include": {
                "type": "string",
                "description": "文件过滤模式，如 *.py",
            },
        },
        "required": ["pattern"],
    }

    async def execute(self, pattern: str, include: str = "", **kwargs) -> str:
        try:
            import glob as glob_mod

            base = os.getcwd()
            if include:
                files = glob_mod.glob(f"**/{include}", root_dir=base, recursive=True)
            else:
                files = glob_mod.glob("**/*", root_dir=base, recursive=True)
                files = [f for f in files if os.path.isfile(os.path.join(base, f))]

            files = sorted(files)[:500]

            matches = []
            for filepath in files:
                try:
                    full_path = os.path.join(base, filepath)
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        for i, line in enumerate(f, 1):
                            if re.search(pattern, line):
                                line = line.rstrip("\n\r")
                                if len(line) > 200:
                                    line = line[:200] + "..."
                                matches.append(f"{filepath}:{i}:{line}")
                                if len(matches) >= 50:
                                    break
                    if len(matches) >= 50:
                        break
                except Exception:
                    continue

            if not matches:
                return f"未找到匹配 '{pattern}' 的内容"
            result = f"搜索 '{pattern}' 的结果（共 {len(matches)} 条）：\n"
            result += "\n".join(matches)
            return result
        except Exception as e:
            return f"搜索失败: {e}"
