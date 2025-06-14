import os
import sys
import json
import asyncio
from openai import OpenAI
from fastmcp import Client

# 初始化客户端
client = OpenAI(
    api_key="阿里云apiKEY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 系统提示词
system_prompt = """你是一个天气查询助手，用户可以调用天气查询工具来查询各地区的实时天气。"""

# 初始化消息列表
messages = [
    {"role": "system", "content": system_prompt}
]

# 初始化mcp客户端
mcp_client = Client("server.py")
tools = []

# 准备工具
async def prepare_tools():
    global tools
    if not tools:
        fetched_tools = await mcp_client.list_tools()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in fetched_tools
        ]
    return tools

# 执行工具
async def execute_tool(name, arguments):
    response = await mcp_client.call_tool(
        name,
        json.loads(arguments)
    )
    return response[0].text

# 获取流式响应
async def get_streaming_response(messages, tools):
    completion = client.chat.completions.create(
        model="qwen3-32b",
        messages=messages,
        tools=tools,
        stream=True,
        parallel_tool_calls=True,
        extra_body={
            # 开启深度思考，该参数对 QwQ 模型无效
            "enable_thinking": True
        },
    )

    full_content = ""
    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""  # 定义完整回复
    tool_info = []  # 存储工具调用信息
    is_answering = False  # 判断是否结束思考过程并开始回复
    print("=" * 20 + "思考过程" + "=" * 20)
    for chunk in completion:
        if not chunk.choices:
            # 处理用量统计信息
            print("\n" + "=" * 20 + "Usage" + "=" * 20)
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            # 处理AI的思考过程（链式推理）
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content
                print(delta.reasoning_content, end="", flush=True)  # 实时输出思考过程

            # 处理最终回复内容
            else:
                if not is_answering:  # 首次进入回复阶段时打印标题
                    is_answering = True
                    print("\n" + "=" * 20 + "回复内容" + "=" * 20)
                if delta.content is not None:
                    answer_content += delta.content
                    print(delta.content, end="", flush=True)  # 流式输出回复内容

                # 处理工具调用信息（支持并行工具调用）
                if delta.tool_calls is not None:
                    for tool_call in delta.tool_calls:
                        index = tool_call.index  # 工具调用索引，用于并行调用

                        # 动态扩展工具信息存储列表
                        while len(tool_info) <= index:
                            tool_info.append({})

                        # 收集工具调用ID（用于后续函数调用）
                        if tool_call.id:
                            tool_info[index]['id'] = tool_info[index].get('id', '') + tool_call.id

                        # 收集函数名称（用于后续路由到具体函数）
                        if tool_call.function and tool_call.function.name:
                            tool_info[index]['name'] = tool_info[index].get('name', '') + tool_call.function.name

                        # 收集函数参数（JSON字符串格式，需要后续解析）
                        if tool_call.function and tool_call.function.arguments:
                            tool_info[index]['arguments'] = tool_info[index].get('arguments',
                                                                                 '') + tool_call.function.arguments
    if tool_info:
        response = await execute_tool(tool_info[0]['name'], tool_info[0]['arguments'])
        print(response)
    else:
        response = answer_content
    return response
    # return full_content.strip()

# 多轮对话循环
async def main():
    sys.stdout.flush()
    async with mcp_client:  # 使用上下文管理器确保客户端连接
        await prepare_tools()
        while True:
            # 用户输入
            user_input = input("\n请输入：").strip()
            messages.append({"role": "user", "content": user_input})

            # 获取模型回复
            print("\n模型输出：")
            assistant_reply = await get_streaming_response(messages, tools)
            messages.append({"role": "assistant", "content": assistant_reply})
            print("\n")

if __name__ == '__main__':
    asyncio.run(main())