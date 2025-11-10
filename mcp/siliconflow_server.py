#!/usr/bin/env python3
"""
SiliconFlow MCP Server
硅基流动 API MCP 服务器

This MCP server connects Claude to SiliconFlow API, allowing natural language
AI interactions using SiliconFlow's LLM services.

Features:
- Text generation using SiliconFlow API
- Chat completions
- Model selection
"""

import os
import json
import logging
from typing import Any, Sequence
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("siliconflow-server")

# SiliconFlow API configuration
SILICONFLOW_API_BASE = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-R1"

def get_siliconflow_client():
    """Get SiliconFlow API key from environment."""
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError("SILICONFLOW_API_KEY not found in environment variables")
    return api_key

# Initialize MCP server
app = Server("siliconflow-server")

# Get API key
try:
    api_key = get_siliconflow_client()
    logger.info("SiliconFlow API key loaded successfully")
except ValueError as e:
    logger.error(f"Failed to load API key: {e}")
    api_key = None


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available SiliconFlow resources."""
    return [
        Resource(
            uri=AnyUrl("siliconflow://models"),
            name="Available Models",
            mimeType="application/json",
            description="List of available SiliconFlow models"
        ),
        Resource(
            uri=AnyUrl("siliconflow://config"),
            name="API Configuration",
            mimeType="application/json",
            description="Current SiliconFlow API configuration"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read and return SiliconFlow resource data."""
    uri_str = str(uri)
    
    if uri_str == "siliconflow://models":
        # Return list of common SiliconFlow models
        models = {
            "models": [
                "deepseek-ai/DeepSeek-R1",
                "deepseek-ai/DeepSeek-V3",
                "Qwen/Qwen2.5-72B-Instruct",
                "Qwen/Qwen2.5-32B-Instruct",
                "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "meta-llama/Meta-Llama-3.1-8B-Instruct",
                "01-ai/Yi-1.5-34B-Chat",
                "01-ai/Yi-1.5-9B-Chat"
            ],
            "default_model": DEFAULT_MODEL
        }
        return json.dumps(models, indent=2, ensure_ascii=False)
    
    elif uri_str == "siliconflow://config":
        config = {
            "api_base": SILICONFLOW_API_BASE,
            "default_model": DEFAULT_MODEL,
            "api_key_configured": api_key is not None
        }
        return json.dumps(config, indent=2, ensure_ascii=False)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available SiliconFlow tools."""
    return [
        Tool(
            name="chat_completion",
            description="使用硅基流动 API 进行对话补全。支持多轮对话、自定义模型和参数。",
            inputSchema={
                "type": "object",
                "properties": {
                    "messages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["system", "user", "assistant"],
                                    "description": "消息角色"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "消息内容"
                                }
                            },
                            "required": ["role", "content"]
                        },
                        "description": "对话消息列表，支持多轮对话"
                    },
                    "model": {
                        "type": "string",
                        "description": "要使用的模型名称（例如：deepseek-ai/DeepSeek-R1），如果不指定则使用默认模型",
                        "default": DEFAULT_MODEL
                    },
                    "temperature": {
                        "type": "number",
                        "description": "采样温度，控制输出的随机性（0-2），默认 0.7",
                        "default": 0.7,
                        "minimum": 0,
                        "maximum": 2
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "最大生成 token 数，默认 2000",
                        "default": 2000,
                        "minimum": 1
                    },
                    "stream": {
                        "type": "boolean",
                        "description": "是否使用流式输出，默认 false",
                        "default": False
                    }
                },
                "required": ["messages"]
            }
        ),
        Tool(
            name="text_generation",
            description="使用硅基流动 API 生成文本。适合单次文本生成任务。",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "文本生成提示词"
                    },
                    "model": {
                        "type": "string",
                        "description": "要使用的模型名称，如果不指定则使用默认模型",
                        "default": DEFAULT_MODEL
                    },
                    "temperature": {
                        "type": "number",
                        "description": "采样温度（0-2），默认 0.7",
                        "default": 0.7,
                        "minimum": 0,
                        "maximum": 2
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "最大生成 token 数，默认 2000",
                        "default": 2000,
                        "minimum": 1
                    }
                },
                "required": ["prompt"]
            }
        ),
        Tool(
            name="list_models",
            description="获取可用的硅基流动模型列表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute SiliconFlow tools."""
    try:
        if not api_key:
            return [TextContent(
                type="text",
                text="错误：未配置 SILICONFLOW_API_KEY 环境变量。请在 .env 文件中设置。"
            )]

        if name == "chat_completion":
            messages = arguments.get("messages", [])
            model = arguments.get("model", DEFAULT_MODEL)
            temperature = arguments.get("temperature", 0.7)
            max_tokens = arguments.get("max_tokens", 2000)
            stream = arguments.get("stream", False)

            if not messages:
                raise ValueError("messages 参数不能为空")

            # Prepare request
            url = f"{SILICONFLOW_API_BASE}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }

            logger.info(f"Calling SiliconFlow API with model: {model}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code != 200:
                error_msg = f"API 请求失败 (状态码: {response.status_code}): {response.text}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]

            result = response.json()
            
            # Extract the assistant's message
            if "choices" in result and len(result["choices"]) > 0:
                assistant_message = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                response_data = {
                    "content": assistant_message,
                    "model": result.get("model"),
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(response_data, indent=2, ensure_ascii=False)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"API 响应格式异常: {json.dumps(result, indent=2, ensure_ascii=False)}"
                )]

        elif name == "text_generation":
            prompt = arguments.get("prompt")
            model = arguments.get("model", DEFAULT_MODEL)
            temperature = arguments.get("temperature", 0.7)
            max_tokens = arguments.get("max_tokens", 2000)

            if not prompt:
                raise ValueError("prompt 参数不能为空")

            # Convert to chat format
            messages = [{"role": "user", "content": prompt}]

            # Use chat_completion internally
            url = f"{SILICONFLOW_API_BASE}/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            logger.info(f"Generating text with model: {model}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code != 200:
                error_msg = f"API 请求失败 (状态码: {response.status_code}): {response.text}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]

            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                response_data = {
                    "generated_text": generated_text,
                    "model": result.get("model"),
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(response_data, indent=2, ensure_ascii=False)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"API 响应格式异常: {json.dumps(result, indent=2, ensure_ascii=False)}"
                )]

        elif name == "list_models":
            # Return common SiliconFlow models
            models_data = {
                "models": [
                    {
                        "id": "deepseek-ai/DeepSeek-R1",
                        "name": "DeepSeek R1",
                        "description": "DeepSeek 最新推理模型"
                    },
                    {
                        "id": "deepseek-ai/DeepSeek-V3",
                        "name": "DeepSeek V3",
                        "description": "DeepSeek V3 模型"
                    },
                    {
                        "id": "Qwen/Qwen2.5-72B-Instruct",
                        "name": "Qwen 2.5 72B",
                        "description": "Qwen 2.5 72B 指令模型"
                    },
                    {
                        "id": "Qwen/Qwen2.5-32B-Instruct",
                        "name": "Qwen 2.5 32B",
                        "description": "Qwen 2.5 32B 指令模型"
                    },
                    {
                        "id": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                        "name": "Llama 3.1 70B",
                        "description": "Meta Llama 3.1 70B 指令模型"
                    },
                    {
                        "id": "meta-llama/Meta-Llama-3.1-8B-Instruct",
                        "name": "Llama 3.1 8B",
                        "description": "Meta Llama 3.1 8B 指令模型"
                    },
                    {
                        "id": "01-ai/Yi-1.5-34B-Chat",
                        "name": "Yi 1.5 34B",
                        "description": "零一万物 Yi 1.5 34B 对话模型"
                    },
                    {
                        "id": "01-ai/Yi-1.5-9B-Chat",
                        "name": "Yi 1.5 9B",
                        "description": "零一万物 Yi 1.5 9B 对话模型"
                    }
                ],
                "default_model": DEFAULT_MODEL,
                "note": "这是常用模型列表，实际可用模型可能更多，请访问 https://siliconflow.cn 查看完整列表"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(models_data, indent=2, ensure_ascii=False)
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(
            type="text",
            text=f"错误: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

