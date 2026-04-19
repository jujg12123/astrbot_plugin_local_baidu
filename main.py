import asyncio
import json
from typing import Dict, List, Optional
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from baidusearch.baidusearch import search as baidu_search

@register("astrbot_plugin_local_baidu", "Your Name", "一个适配国内网络的百度搜索插件", "1.0.0")
class LocalBaiduSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 注册核心工具，让 AI 能够发现并调用它
        context.llm_tools.reg_core_tool(self._get_search_tool(), self._search_handler)
        logger.info("本地百度搜索插件已初始化并注册工具。")

    # 定义 AI 能看到的工具描述
    def _get_search_tool(self) -> Dict:
        return {
            "type": "function",
            "function": {
                "name": "local_baidu_search",
                "description": "当用户的问题需要获取最新、实时信息时，使用此工具通过百度搜索引擎进行联网搜索。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "用户想要搜索的关键词。",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "期望返回的搜索结果数量。默认为5，最大不超过10。",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
        }

    # 工具被调用时的异步处理函数
    async def _search_handler(self, arguments: str) -> str:
        args = json.loads(arguments)
        query = args.get("query")
        num_results = min(args.get("num_results", 5), 10) # 限制结果数量

        logger.info(f"正在执行百度搜索: '{query}'")

        try:
            results = await self._perform_search(query, num_results)
            if not results:
                return f"抱歉，没有找到关于“{query}”的相关信息。"

            # 格式化结果给 AI
            formatted_results = []
            for i, res in enumerate(results):
                formatted_results.append(f"{i+1}. 标题: {res['title']}\n   摘要: {res.get('abstract', '无')}\n   链接: {res['url']}")
            return "\n\n".join(formatted_results)

        except Exception as e:
            logger.error(f"百度搜索失败: {e}")
            return f"执行搜索时发生错误：{e}"

    # 异步调用 baidusearch 库
    async def _perform_search(self, query: str, num_results: int = 5) -> List[Dict]:
        return await asyncio.to_thread(baidu_search, query, num_results=num_results)

    async def terminate(self):
        # 可在此处进行资源清理（如有需要）
        logger.info("本地百度搜索插件已卸载。")
