import asyncio
from pydantic import Field
from pydantic.dataclasses import dataclass
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.agent.run_context import ContextWrapper
from astrbot.core.agent.tool import FunctionTool, ToolExecResult
from astrbot.core.astr_agent_context import AstrAgentContext
from baidusearch.baidusearch import search as baidu_search

@dataclass
class BaiduSearchTool(FunctionTool[AstrAgentContext]):
    name: str = "local_baidu_search"
    description: str = "当需要获取最新、实时信息时，通过百度搜索引擎进行联网搜索。"
    parameters: dict = Field(
        default_factory=lambda: {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "用户想要搜索的关键词。"
                },
                "num_results": {
                    "type": "integer",
                    "description": "期望返回的搜索结果数量。默认为5。",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    )

    async def call(self, context: ContextWrapper[AstrAgentContext], **kwargs) -> ToolExecResult:
        query = kwargs.get("query")
        num_results = kwargs.get("num_results", 5)
        logger.info(f"正在执行百度搜索: '{query}'")

        try:
            results = await asyncio.to_thread(baidu_search, query, num_results=num_results)
            if not results:
                return ToolExecResult(f"抱歉，没有找到关于“{query}”的相关信息。")
            
            formatted_results = []
            for i, res in enumerate(results):
                formatted_results.append(f"{i+1}. 标题: {res['title']}\n   摘要: {res.get('abstract', '无')}\n   链接: {res['url']}")
            return ToolExecResult("\n\n".join(formatted_results))
        except Exception as e:
            logger.error(f"百度搜索失败: {e}")
            return ToolExecResult(f"执行搜索时发生错误：{e}")


@register("astrbot_plugin_websearch", "Your Name", "一个适配国内网络的百度搜索插件", "1.0.0")
class WebSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.baidu_search_tool = BaiduSearchTool()  # 实例化工具
        logger.info("百度搜索插件已初始化（使用新版 FunctionTool）。")

    # ...（插件的其他逻辑，例如手动触发指令）
