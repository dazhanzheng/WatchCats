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


# ===== 日程管理相关的解析器 =====

class ScheduleCreateParams(BaseModel):
    """创建日程的参数"""
    title: str = Field(description="日程标题")
    details: str = Field(description="日程详情")
    start_time: datetime = Field(description="开始时间")
    duration_minutes: int = Field(description="持续时间（分钟）")
    trigger_percentages: Optional[List[float]] = Field(
        default=[100.0], 
        description="触发百分比列表"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="额外元数据"
    )


class ScheduleUpdateParams(BaseModel):
    """更新日程的参数"""
    schedule_id: str = Field(description="日程ID")
    title: Optional[str] = Field(None, description="新标题")
    details: Optional[str] = Field(None, description="新详情")
    start_time: Optional[datetime] = Field(None, description="新开始时间")
    duration_minutes: Optional[int] = Field(None, description="新持续时间")
    trigger_percentages: Optional[List[float]] = Field(None, description="新触发百分比列表")
    is_active: Optional[bool] = Field(None, description="是否激活")
    metadata: Optional[Dict[str, Any]] = Field(None, description="新元数据")


class ScheduleListParams(BaseModel):
    """列出日程的参数"""
    active_only: bool = Field(False, description="仅返回激活的日程")
    include_past: bool = Field(True, description="包含过去的日程")
    include_future: bool = Field(True, description="包含未来的日程")
    sort_by: Literal["start_time", "created_at", "title"] = Field(
        "start_time",
        description="排序字段"
    )
    date_from: Optional[datetime] = Field(None, description="开始日期（包含）")
    date_to: Optional[datetime] = Field(None, description="结束日期（包含）")


class ParsedScheduleCommand(BaseModel):
    """解析后的日程管理命令"""
    
    method: Literal[
        "add",
        "update",
        "delete",
        "get",
        "list",
        "get_current",
        "get_upcoming",
        "get_schedules_for_date",
        "set_callback",
        "clear_triggered",
        "save",
        "reload",
        "backup",
        "export",
        "import_schedules"
    ] = Field(description="要调用的方法名")
    
    # 各方法的参数
    create_params: Optional[ScheduleCreateParams] = None
    update_params: Optional[ScheduleUpdateParams] = None
    schedule_id: Optional[str] = None
    list_params: Optional[ScheduleListParams] = None
    hours: Optional[int] = Field(None, description="查看未来多少小时（get_upcoming）")
    date: Optional[datetime] = Field(None, description="目标日期（get_schedules_for_date）")
    percentage: Optional[float] = None
    export_data: Optional[Dict[str, Any]] = None
    merge: Optional[bool] = Field(False, description="导入时是否合并")
    
    @validator("create_params")
    def validate_create_params(cls, v, values):
        if values.get("method") == "add" and v is None:
            raise ValueError("add 方法需要 create_params")
        return v
    
    @validator("schedule_id")
    def validate_schedule_id(cls, v, values):
        method = values.get("method")
        if method in ["update", "delete", "get", "set_callback", "clear_triggered"] and v is None:
            # 对于 update，schedule_id 在 update_params 中
            if method == "update" and values.get("update_params"):
                return v
            raise ValueError(f"{method} 方法需要 schedule_id")
        return v


class ScheduleCommandParser:
    """日程命令解析器"""
    
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ParsedScheduleCommand)
        
        # 系统提示词模板
        self.system_prompt_template = """你是一个精确的日程管理命令解析器，将自然语言转换为日程管理函数调用。

当前时间：{current_time}
今天的日期是：{today_date}

可用的方法：
1. add(title, details, start_time, duration_minutes, ...) - 创建新日程
2. update(schedule_id, ...) - 更新日程
3. delete(schedule_id) - 删除日程
4. get(schedule_id) - 获取单个日程
5. list(active_only, include_past, include_future, sort_by, date_from, date_to) - 列出日程
6. get_current() - 获取当前进行中的日程
7. get_upcoming(hours) - 获取即将开始的日程
8. get_schedules_for_date(date) - 获取特定日期的所有日程
9. set_callback(schedule_id, percentage, callback) - 设置回调（注：callback无法从文本解析）
10. clear_triggered(schedule_id) - 清除已触发记录
11. save() - 手动保存
12. reload() - 重新加载
13. backup() - 创建备份
14. export() - 导出数据
15. import_schedules(data, merge) - 导入数据

时间解析规则：
- 今天 = {today_date}
- 明天 = {tomorrow_date}  
- 后天 = {day_after_tomorrow_date}
- "下午3点"、"15:00"等会解析为时间
- 持续时间支持"2小时"、"90分钟"等表达
- 重要：必须使用上面提供的具体日期，不要使用你训练时的日期

特殊时间查询的处理：
- "今天的日程/事项/安排"：使用 get_schedules_for_date(date=今天)
- "明天的日程/事项/安排"：使用 get_schedules_for_date(date=明天)
- "后天的日程/事项/安排"：使用 get_schedules_for_date(date=后天)
- "本周的日程"：使用 list() 并设置 date_from 为本周一，date_to 为本周日
- "所有日程"：使用 list() 不带任何参数
- "未来的日程"：使用 get_upcoming() 或 list(include_past=false)
- 注意：优先使用 get_schedules_for_date 来查询特定日期的日程

{format_instructions}"""
        
        # 用户提示词模板
        self.user_prompt_template = PromptTemplate(
            template="""将以下请求解析为日程管理命令：{query}

当前时间：{current_time}""",
            input_variables=["query", "current_time"],
        )
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        now = datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)
        
        return self.system_prompt_template.format(
            current_time=now.strftime("%Y-%m-%d %H:%M:%S"),
            today_date=now.strftime("%Y年%m月%d日"),
            tomorrow_date=tomorrow.strftime("%Y年%m月%d日"),
            day_after_tomorrow_date=day_after_tomorrow.strftime("%Y年%m月%d日"),
            format_instructions=self.parser.get_format_instructions()
        )
    
    def get_user_prompt(self, query: str) -> str:
        """获取用户提示词"""
        return self.user_prompt_template.format(
            query=query,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ) 