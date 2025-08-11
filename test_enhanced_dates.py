#!/usr/bin/env python3
"""增强的日期测试 - 验证今天、明天、后天的具体日期都在系统提示词中"""

from datetime import datetime, timedelta
from baal.llm_assistant.parsers import ScheduleCommandParser

def test_enhanced_dates():
    """测试增强的日期处理"""
    parser = ScheduleCommandParser()
    
    # 获取当前时间和相对日期
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    print("=" * 70)
    print("增强的相对日期解析测试")
    print("=" * 70)
    print(f"\n系统当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"今天: {today.strftime('%Y年%m月%d日')}")
    print(f"明天: {tomorrow.strftime('%Y年%m月%d日')}")
    print(f"后天: {day_after_tomorrow.strftime('%Y年%m月%d日')}")
    
    # 获取系统提示词
    system_prompt = parser.get_system_prompt()
    
    print("\n" + "-" * 70)
    print("系统提示词中的日期信息:")
    print("-" * 70)
    
    # 检查所有日期是否都在系统提示词中
    dates_to_check = [
        ("今天", today.strftime("%Y年%m月%d日")),
        ("明天", tomorrow.strftime("%Y年%m月%d日")),
        ("后天", day_after_tomorrow.strftime("%Y年%m月%d日"))
    ]
    
    all_found = True
    for label, date_str in dates_to_check:
        if date_str in system_prompt:
            print(f"✓ {label}的具体日期 ({date_str}) 已包含在系统提示词中")
        else:
            print(f"✗ {label}的具体日期 ({date_str}) 未找到")
            all_found = False
    
    # 打印时间解析规则部分
    print("\n" + "-" * 70)
    print("系统提示词中的时间解析规则部分:")
    print("-" * 70)
    
    # 查找并打印时间解析规则
    lines = system_prompt.split('\n')
    printing = False
    for line in lines:
        if '时间解析规则' in line:
            printing = True
        if printing:
            print(line)
            if '重要：' in line:
                break
    
    print("\n" + "=" * 70)
    print("测试结果:")
    print("=" * 70)
    
    if all_found:
        print("✅ 所有相对日期都正确配置！")
        print("\nLLM现在会收到明确的指示:")
        print(f"  - '今天' 应该解析为 {today.strftime('%Y年%m月%d日')}")
        print(f"  - '明天' 应该解析为 {tomorrow.strftime('%Y年%m月%d日')}")
        print(f"  - '后天' 应该解析为 {day_after_tomorrow.strftime('%Y年%m月%d日')}")
        print("\n这样就不会出现日期混淆的问题了！")
    else:
        print("❌ 某些日期配置有问题，请检查代码")
    
    # 测试几个示例查询
    print("\n" + "-" * 70)
    print("示例查询的用户提示词:")
    print("-" * 70)
    
    test_queries = [
        "创建一个明天上午9点的会议",
        "后天下午有个演讲",
        "查看今天的所有日程"
    ]
    
    for query in test_queries:
        user_prompt = parser.get_user_prompt(query)
        print(f"\n查询: {query}")
        print("用户提示词:")
        for line in user_prompt.split('\n'):
            print(f"  {line}")

if __name__ == "__main__":
    test_enhanced_dates()