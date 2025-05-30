# local_mcp
基于fastmcp实现完全的本地MCP服务器，本地大模型调用MCP

# 使用方法

打开`leo_app.py`，修改下面的代码，调整里面的base_url和api_key

```
        self.openai_client = OpenAI(
            base_url="你的base_url",
            api_key="你的api_key",
            http_client=no_proxy_client
        )
```

# 注

因为本地代理配置问题，增加了`no_proxy_client`。如果遇到问题，可以尝试删掉`http_client=no_proxy_client`
