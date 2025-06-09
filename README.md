# local_mcp
基于fastmcp的天气查询助手。采用Qwen模型进行实时对话并调用心知天气API回复实时天气情况

# 文件介绍

`leo_app.py`：固定对话，没有用到fastmcp

`leo_app2.py`：固定对话，但模型主动调用mcp

`leo_app3.py`：自由对话，模型主动调用mcp

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
