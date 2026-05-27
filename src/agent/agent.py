import json
from ..api.deepseek import DeepSeekClient
from ..tools.registry import ToolRegistry
from .system_prompt import SYSTEM_PROMPT


class AgentEvent:
    """Events emitted by the agent during execution."""

    def __init__(self, type: str, data: dict):
        self.type = type  # "text_chunk", "tool_start", "tool_result", "error"
        self.data = data


class Agent:
    def __init__(self, client: DeepSeekClient, registry: ToolRegistry):
        self.client = client
        self.registry = registry
        self.messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.tools = registry.to_openai_tools()

    async def run(self, user_message: str):
        """Run the agent with a user message. Yields AgentEvents."""
        self.messages.append({"role": "user", "content": user_message})

        while True:
            collected_content = ""
            tool_calls: dict[str, tuple[str, str, dict]] = {}  # index -> (id, name, args)

            stream = self.client.chat_stream(self.messages, self.tools)
            async for chunk in stream:
                delta = chunk.get("choices", [{}])[0].get("delta", {})

                if content := delta.get("content"):
                    collected_content += content
                    yield AgentEvent("text_chunk", {"text": content})

                if tc := delta.get("tool_calls"):
                    for tcc in tc:
                        idx = tcc.get("index", 0)
                        if idx not in tool_calls:
                            tool_calls[idx] = (
                                tcc.get("id", ""),
                                tcc.get("function", {}).get("name", ""),
                                tcc.get("function", {}).get("arguments", ""),
                            )
                        else:
                            tid, tname, targs = tool_calls[idx]
                            tool_calls[idx] = (
                                tid or tcc.get("id", ""),
                                tname or tcc.get("function", {}).get("name", ""),
                                targs + (tcc.get("function", {}).get("arguments", "") or ""),
                            )

            assistant_msg = {"role": "assistant", "content": collected_content or None}

            if tool_calls:
                tc_list = []
                for idx in sorted(tool_calls.keys()):
                    tid, tname, targs = tool_calls[idx]
                    tc_list.append({
                        "id": tid or f"call_{idx}",
                        "type": "function",
                        "function": {"name": tname, "arguments": targs},
                    })
                assistant_msg["tool_calls"] = tc_list

            self.messages.append(assistant_msg)

            if not tool_calls:
                break

            for idx in sorted(tool_calls.keys()):
                tid, tname, targs = tool_calls[idx]
                try:
                    args = json.loads(targs) if targs else {}
                except json.JSONDecodeError:
                    args = {}

                yield AgentEvent("tool_start", {
                    "name": tname,
                    "arguments": args,
                })

                result = await self.registry.execute(tname, **args)

                yield AgentEvent("tool_result", {
                    "name": tname,
                    "result": result,
                })

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tid or f"call_{idx}",
                    "content": result,
                })
