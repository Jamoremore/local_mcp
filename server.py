"""
1. 创建fastmcp的实例
2. 创建函数，添加文档
3. @mcp.tool
4. 运行服务器
"""
import requests
from fastmcp import FastMCP

mcp = FastMCP()

# 替换为你自己的心知天气 API 密钥和私钥
API_KEY = '心知天气 API 密钥'
API_SECRET = '心知天气 API 私钥'

@mcp.tool()
def get_weather(city: str):
    """
    获取对应城市的天气
    :param city: 城市
    :return: 城市天气的描述
    """
    url = f'https://api.seniverse.com/v3/weather/now.json?key={API_SECRET}&&location={city}&language=zh-Hans&unit=c'
    try:
        response = requests.get(url)
        data = response.json()
        if 'results' in data:
            weather = data['results'][0]['now']
            return f"{city}当前天气 {weather['text']}，气温 {weather['temperature']} 度"
        else:
            return f"无法获取 {city} 的天气信息"
    except Exception as e:
        return f"查询天气时出现错误: {e}"

if __name__ == '__main__':
    mcp.run()