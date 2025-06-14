"""
1. 创建fastmcp的实例
2. 创建函数，添加文档
3. @mcp.tool
4. 运行服务器
"""
from fastmcp import FastMCP

mcp=FastMCP()

@mcp.tool()
def get_weather(city:str):
    """
    获取对应城市的天气
    :param city:城市
    :return:城市天气的描述
    """
    return f"{city}今天天气晴，18度"

if __name__ == '__main__':
    mcp.run()