#!/usr/bin/env python3
"""测试日期修复 - 验证"今天"的日程是否正确创建"""

from datetime import datetime
from baal.llm_assistant.parsers import ScheduleCommandParser

def test_date_parsing():
    """测试日期解析是否正确"""
    parser = ScheduleCommandParser()
    
    # 测试系统提示词是否包含当前日期
    system_prompt = parser.get_system_prompt()
    today = datetime.now()
    expected_date = today.strftime("%Y年%m月%d日")
    expected_time = today.strftime("%Y-%m-%d")
    
    print("=" * 60)
    print("测试日期解析修复")
    print("=" * 60)
    print(f"\n当前实际日期: {expected_date}")
    print(f"当前实际时间: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n检查系统提示词中的日期信息:")
    print("-" * 40)
    
    # 检查系统提示词中是否包含正确的日期
    if expected_date in system_prompt:
        print(f"✓ 系统提示词包含正确的日期: {expected_date}")
    else:
        print(f"✗ 系统提示词未包含正确的日期")
        
    if expected_time in system_prompt:
        print(f"✓ 系统提示词包含正确的时间格式")
    else:
        print(f"✗ 系统提示词未包含正确的时间格式")
    
    # 打印系统提示词的前500个字符以供检查
    print("\n系统提示词前500字符:")
    print("-" * 40)
    print(system_prompt[:500])
    
    # 测试用户提示词
    print("\n测试用户提示词:")
    print("-" * 40)
    user_prompt = parser.get_user_prompt("创建一个今天下午3点的会议")
    print(f"用户提示词:\n{user_prompt}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("如果上面显示的日期是正确的（今天是1月10日），")
    print("那么修复成功，Baal应该能正确创建今天的日程了。")
    print("=" * 60)

if __name__ == "__main__":
    test_date_parsing()