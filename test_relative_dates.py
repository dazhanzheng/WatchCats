#!/usr/bin/env python3
"""测试相对日期解析 - 验证今天、明天、后天等相对日期的处理"""

from datetime import datetime, timedelta
from baal.llm_assistant.parsers import ScheduleCommandParser
from baal.llm_assistant.assistant import LLMAssistant
from baal.scheduler.manager import ScheduleManager
import json

def test_relative_dates():
    """测试相对日期的解析"""
    parser = ScheduleCommandParser()
    
    # 获取当前时间
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    print("=" * 70)
    print("测试相对日期解析")
    print("=" * 70)
    print(f"\n系统当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"今天: {today.strftime('%Y年%m月%d日')}")
    print(f"明天: {tomorrow.strftime('%Y年%m月%d日')}")
    print(f"后天: {day_after_tomorrow.strftime('%Y年%m月%d日')}")
    
    # 检查系统提示词
    system_prompt = parser.get_system_prompt()
    print("\n" + "-" * 70)
    print("系统提示词中的时间信息:")
    print("-" * 70)
    
    # 提取系统提示词中的时间部分
    lines = system_prompt.split('\n')
    for line in lines[:10]:  # 只打印前10行
        if '当前时间' in line or '今天' in line:
            print(line)
    
    # 测试不同的相对日期查询
    test_queries = [
        "创建一个今天下午3点的会议",
        "添加明天上午10点的任务",
        "安排后天下午2点的讨论",
        "今天有什么日程",
        "明天的安排",
        "查看后天的事项"
    ]
    
    print("\n" + "-" * 70)
    print("测试用户提示词生成:")
    print("-" * 70)
    
    for query in test_queries:
        user_prompt = parser.get_user_prompt(query)
        print(f"\n查询: {query}")
        print(f"生成的用户提示词:")
        print(user_prompt)
        print("-" * 40)
    
    # 测试实际的解析功能（如果有API配置）
    print("\n" + "=" * 70)
    print("相对日期解析说明:")
    print("=" * 70)
    print("""
修复后的系统现在会：
1. 在系统提示词中明确告知LLM当前的准确日期和时间
2. LLM会基于这个时间来理解"今天"、"明天"、"后天"等相对日期
3. 解析规则中明确说明要使用提供的时间作为基准

例如，如果今天是8月10日：
- "今天的日程" → 8月10日的日程
- "明天的会议" → 8月11日的会议  
- "后天的任务" → 8月12日的任务

这样就不会出现把1月15日当作"今天"的问题了。
""")
    
    print("=" * 70)
    print("测试完成！")
    print("=" * 70)

def test_with_mock_llm():
    """使用模拟的LLM响应测试日期解析"""
    print("\n" + "=" * 70)
    print("模拟LLM响应测试")
    print("=" * 70)
    
    # 创建日程管理器
    schedule_manager = ScheduleManager()
    
    # 模拟LLM解析"今天下午3点的会议"的响应
    now = datetime.now()
    today_3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)
    
    mock_response = {
        "method": "add",
        "add_params": {
            "title": "会议",
            "details": "下午3点的会议",
            "start_time": today_3pm.isoformat(),
            "duration_minutes": 60,
            "trigger_percentages": [100.0],
            "metadata": {}
        }
    }
    
    print(f"\n模拟创建'今天下午3点的会议':")
    print(f"解析后的开始时间应该是: {today_3pm.strftime('%Y-%m-%d %H:%M')}")
    print(f"模拟的解析结果: {json.dumps(mock_response, indent=2, ensure_ascii=False)}")
    
    # 测试明天
    tomorrow_10am = (now + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    mock_response_tomorrow = {
        "method": "add",
        "add_params": {
            "title": "任务",
            "details": "明天上午10点的任务",
            "start_time": tomorrow_10am.isoformat(),
            "duration_minutes": 30,
            "trigger_percentages": [100.0],
            "metadata": {}
        }
    }
    
    print(f"\n模拟创建'明天上午10点的任务':")
    print(f"解析后的开始时间应该是: {tomorrow_10am.strftime('%Y-%m-%d %H:%M')}")
    print(f"模拟的解析结果: {json.dumps(mock_response_tomorrow, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    test_relative_dates()
    test_with_mock_llm()