# ThinkFlow
Use the CoT (Chain of Thought) model to guide non - reasoning models and improve the quality of dialogue.
# ThinkFlow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

专为 Open WebUI 设计的智能推理管道，集成 DeepSeek 双阶段推理引擎。

```python
from thinkflow import Pipe

async def chat_handler(message: str) -> AsyncGenerator:
    pipe = Pipe()
    async for chunk in pipe.pipe({"messages": [{"role": "user", "content": message}]}):
        yield chunk  # 流式输出格式：<think>...</think> + 最终响应
