"""
自由对话，模型主动调用mcp
用户 client:
    调用大语言模型：    openai client
    调用 mcp 服务器： mcp client
"""
import json
import asyncio

from typing import List,Dict

from fastmcp import Client
from openai import OpenAI
import httpx

class UserClient:


    def __init__(self, script = "leo_server2.py",model="qwen3-32b"):
        no_proxy_client = httpx.Client(trust_env=False)

        self.model = model
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key="sk-0d4e7900460e47cf8733f225d4aa19cd",
            http_client=no_proxy_client
        )
        self.messages = [
            {
                "role":"system",
                "content":"你是一个AI助手，你需要借助工具，回答用户问题"
            }
        ]
        self.tools = []

    async def prepare_tools(self):
        tools = await self.mcp_client.list_tools()
        tools =        [
            {
                "type":"function",
                "function":{
                    "name":tool.name,
                    "description":tool.description,
                    "input_schema":tool.inputSchema
                }
            }
            for tool in tools
        ]
        return tools
        # {
        #     "type":"function",
        #     "function":{
        #         "name":"xxx",
        #         "description":"xxx",
        #         "input_schema":{}
        #     }
        # }

    async def chat(self, messages: List[Dict]):
        if not self.tools:
            self.tools = await self.prepare_tools()

        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools
        )
        if response.choices[0].finish_reason != "tool_calls":
            return response.choices[0].message
        
        # 执行工具
        for tool_call in response.choices[0].message.tool_calls:
            response = await self.mcp_client.call_tool(
                tool_call.function.name, 
                json.loads(tool_call.function.arguments)
            )
            # print(response)

            self.messages.append({
                'role':'assistant',
                'content':response[0].text
            })

            return await self.chat(self.messages)



    async def loop(self):
        async with self.mcp_client:
            while True:
                question = input("User:")
                message = [{"role": "system", "content": "You are a helpful assistant."},
                           {"role": "user", "content": question},
                           ]
                self.messages.append(message)
                response_message = await self.chat(self.messages)
                print("AI:",response_message.content)


async def main():
    user_client = UserClient()
    await user_client.loop()

if __name__ == '__main__':
    asyncio.run(main())