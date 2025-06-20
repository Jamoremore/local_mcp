"""
固定对话，但模型主动调用mcp
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


    def __init__(self, script = "leo_server.py",model="Qwen3:32B"):
        no_proxy_client = httpx.Client(trust_env=False)

        self.model = model
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            base_url="你的base_url",
            api_key="你的api_key",
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
        async with self.mcp_client:
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
        while True:
            question = input("User:")
            message = {
                "role":"user",
                "content":question
            }
            self.messages.append(message)
            response_message = await self.chat(self.messages)
            print("AI:",response_message.get('content'))


async def main():
    user_client = UserClient()
    response_message = await user_client.chat([
        {"role":"user","content":"南昌今天天气怎么样？"}
    ])
    print(response_message)

if __name__ == '__main__':
    asyncio.run(main())