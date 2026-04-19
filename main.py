import asyncio
import json
from typing import Dict, List
from astrbot.api.event import filter, AstrMessageEvent, register_llm_tool
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from baidusearch.baidusearch import search as baidu_search

@register("astrbot_plugin_local_baidu", "Your Name", "一个适配国内网络的百度搜索插件", "1.0.0")
class LocalBaiduSearchPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 不再需要手动注册工具，一切都由装饰器处理
        logger.info("本地百度搜索插件已初始化。")

    # 1. 使用装饰器定义并注册工具
    @register_llm_tool(name="local_baidu_search")
    async def baidu_search_tool(self, query: str, num_results: int = 5):
        """
        当需要获取最新、实时信息时，通过百度搜索引擎进行联网搜索。
        
        :param query: 用户想要搜索的关键词。
        :param num_results: 期望返回的搜索结果数量，默认为5，最大不超过10。
        """
        logger.info(f"正在执行百度搜索: '{query}'")
        num_results = min(num_results, 10) # 限制结果数量

        try:
            # 调用实际的搜索函数
            results = await self._perform_search(query, num_results)
            
            if not results:
                return f"抱歉，没有找到关于“{query}”的相关信息。"

            # 格式化结果返回给 AI
            formatted_results = []
            for i, res in enumerate(results):
                formatted_results.append(f"{i+1}. 标题: {res['title']}\n   摘要: {res.get('abstract', '无')}\n   链接: {res['url']}")
            return "\n\n".join(formatted_results)

        except Exception as e:
            logger.error(f"百度搜索失败: {e}")
            return f"执行搜索时发生错误：{e}"

    # 2. 实际的搜索实现（异步封装）
    async def _perform_search(self, query: str, num_results: int = 5) -> List[Dict]:
        return await asyncio.to_thread(baidu_search, query, num_results=num_results)

    # 3. （可选）保留一个指令用于手动测试
    @filter.command("search_baidu")
    async def search_baidu_command(self, event: AstrMessageEvent, query: str):
        """手动测试百度搜索的指令。用法：/search_baidu <关键词>"""
        yield event.plain_result(f"🔍 正在为您搜索「{query}」...")
        result = await self.baidu_search_tool(query)
        yield event.plain_result(str(result))

    async def terminate(self):
        logger.info("本地百度搜索插件已卸载。")
