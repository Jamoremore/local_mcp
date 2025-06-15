import os
import sys
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key="你的api_key",
    base_url="你的base_url"
)

# 系统提示词
system_prompt = """你是一名阿里云百炼手机商店的店员，你负责给用户推荐手机。手机有两个参数：屏幕尺寸（包括6.1英寸、6.5英寸、6.7英寸）、分辨率（包括2K、4K）。
你一次只能向用户提问一个参数。如果用户提供的信息不全，你需要反问他，让他提供没有提供的参数。如果参数收集完成，你要说：我已了解您的购买意向，请稍等。"""

# 初始化消息列表
messages = [
    {"role": "system", "content": system_prompt}
]


# 获取流式响应
def get_streaming_response(messages):
    completion = client.chat.completions.create(
        model="qwen3-32b",
        messages=messages,
        stream=True,
    )

    full_content = ""
    for chunk in completion:
        if chunk.choices:
            content = chunk.choices[0].delta.content
            if content:
                # 逐词输出而不换行
                sys.stdout.write(content)
                sys.stdout.flush()
                full_content += content

    return full_content.strip()


# # 系统先发起对话
# print("流式输出内容为：")
sys.stdout.flush()
#
# # 获取第一轮回复（系统先提问）
# first_reply = get_streaming_response(messages)
# messages.append({"role": "assistant", "content": first_reply})
# print("\n")

# 多轮对话循环
while True:
    # 用户输入
    user_input = input("\n请输入：").strip()
    messages.append({"role": "user", "content": user_input})

    # 获取模型回复
    print("\n模型输出：")
    assistant_reply = get_streaming_response(messages)
    messages.append({"role": "assistant", "content": assistant_reply})
    print("\n")

    # 检查结束条件
    if "我已了解您的购买意向" in assistant_reply:
        print("对话结束。")
        break
# import os
# import sys
# from openai import OpenAI
#
# client = OpenAI(
#     # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
#     api_key="sk-96f3241521c04e419da90cf55083e586",
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
# )
#
# print("流式输出内容为：")
# sys.stdout.flush()  # 确保输出立即显示
#
# completion = client.chat.completions.create(
#     model="qwen3-32b",  # 使用qwen3-32B模型
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "介绍一下你自己，并解释什么是人工智能？"}
#     ],
#     stream=True,
#     # extra_body={"enable_thinking": False},
# )
#
# full_content = ""
# for chunk in completion:
#     if chunk.choices:
#         content = chunk.choices[0].delta.content
#         if content:
#             # 逐词输出而不换行
#             sys.stdout.write(content)
#             sys.stdout.flush()  # 立即刷新输出缓冲区
#             full_content += content
#
# # # 输出结束后换行
# # print("\n\n完整内容为：")
# # print(full_content)
