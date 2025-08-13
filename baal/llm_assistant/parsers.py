"""
结构化解析器模块

使用 Pydantic 和 LangChain 的输出解析器实现精确的自然语言到函数参数的转换
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, validator
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate


# ===== 统计查询相关的解析器 =====

class ParsedStatsCommand(BaseModel):
    """解析后的统计查询命令"""
    
    method: Literal[
        "get_aggregated_stats",
        "get_detailed_stats", 
        "get_stats_7d",
        "get_stats_1d",
        "get_stats_2h",
        "get_stats_30m",
        "get_stats_5m"
    ] = Field(description="要调用的统计方法名")
    
    # get_aggregated_stats 参数
    days: Optional[int] = Field(None, description="天数参数（用于 get_aggregated_stats）")
    
    # get_detailed_stats 参数
    hours: Optional[float] = Field(None, description="小时数参数（用于 get_detailed_stats）")
    
    @validator("days")
    def validate_days(cls, v, values):
        method = values.get("method")
        if method == "get_aggregated_stats" and v is None:
            raise ValueError("get_aggregated_stats 需要 days 参数")
        return v
    
    @validator("hours")
    def validate_hours(cls, v, values):
        method = values.get("method")
        if method == "get_detailed_stats" and v is None:
            raise ValueError("get_detailed_stats 需要 hours 参数")
        return v


class StatsCommandParser:
    """统计命令解析器"""
    
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ParsedStatsCommand)
        
        # 系统提示词模板
        self.system_prompt = """你是一个精确的命令解析器，专门将用户的自然语言查询转换为 ActivityWatch 统计查询命令。

可用的方法及其参数：
1. get_stats_7d() - 获取7天的聚合统计
2. get_stats_1d() - 获取1天的聚合统计  
3. get_stats_2h() - 获取2小时的详细统计
4. get_stats_30m() - 获取30分钟的详细统计
5. get_stats_5m() - 获取5分钟的详细统计
6. get_aggregated_stats(days: int) - 获取指定天数的聚合统计
7. get_detailed_stats(hours: float) - 获取指定小时数的详细统计

聚合统计：显示应用使用时长排行和占比
详细统计：显示原始事件流和聚合统计

{format_instructions}"""
        
        # 用户提示词模板
        self.user_prompt_template = PromptTemplate(
            template="将以下查询解析为统计命令：{query}",
            input_variables=["query"],
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.system_prompt.format(
            format_instructions=self.parser.get_format_instructions()
        )
    
    def get_user_prompt(self, query: str) -> str:
        """获取用户提示词"""
        return self.user_prompt_template.format(query=query)