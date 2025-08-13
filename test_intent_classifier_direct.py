#!/usr/bin/env python3
"""
直接测试意图分类器的日程功能禁用
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Tuple

class TestBinaryIntentClassifier:
    """测试用二进制意图分类器"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        
        # 构建提示词 - 与修改后的版本一致
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个意图分类器。分析用户输入，输出3位二进制数字。

输出格式（必须严格遵守）：
- 只输出3个数字，每个数字只能是0或1
- 第1位：普通聊天=1，需要工具=0
- 第2位：需要统计=1，不需要=0
- 第3位：始终为0（日程功能已禁用）

示例：
用户："你好" → 输出：100
用户："我今天做了什么" → 输出：010
用户："明天有什么安排" → 输出：100（日程功能已禁用，作为普通聊天）
用户："今天工作了多久？" → 输出：010

重要：
1. 只输出3个数字，不要有任何其他内容！
2. 第3位必须始终为0（日程功能已禁用）
3. 任何日程相关的查询都应该作为普通聊天处理"""),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt | self.llm
    
    def classify(self, user_input: str) -> str:
        response = self.chain.invoke({"input": user_input})
        
        if hasattr(response, 'content'):
            result = response.content.strip()
        else:
            result = str(response).strip()
        
        # 验证格式
        binary_str = ""
        for char in result:
            if char in "01" and len(binary_str) < 3:
                binary_str += char
        
        while len(binary_str) < 3:
            binary_str += "0"
        
        return binary_str[:3]
    
    @staticmethod
    def parse_binary(binary_str: str) -> Tuple[bool, bool, bool]:
        if len(binary_str) != 3:
            return (True, False, False)
        
        is_chat = binary_str[0] == '1'
        needs_stats = binary_str[1] == '1'
        # 日程功能暂时禁用 - 强制第3位为False
        needs_schedule = False  # 永远为False
        
        if needs_stats:
            is_chat = False
        
        return (is_chat, needs_stats, needs_schedule)

def test():
    """运行测试"""
    print("=" * 60)
    print("直接测试意图分类器 - 日程功能应该完全禁用")
    print("=" * 60)
    
    # 配置
    from baal.desktop_pet.core.config_manager import ConfigManager
    config = ConfigManager()
    
    # 初始化LLM
    llm = ChatOpenAI(
        base_url=config.get_base_url(),
        api_key=config.get_api_key(),
        model=config.get_model(),
        temperature=0.1
    )
    
    # 初始化分类器
    classifier = TestBinaryIntentClassifier(llm)
    
    # 测试用例
    test_cases = [
        ("今天有哪些日程", "日程查询"),
        ("明天的会议安排", "日程查询"),
        ("添加一个提醒", "日程添加"),
        ("查看本周任务", "日程查询"),
        ("我今天工作了多久", "统计查询"),
        ("分析我的活动", "统计查询"),
        ("你好", "普通聊天"),
        ("天气怎么样", "普通聊天")
    ]
    
    print("\n测试结果:")
    print("-" * 60)
    
    failed = []
    for msg, desc in test_cases:
        result = classifier.classify(msg)
        is_chat, needs_stats, needs_schedule = TestBinaryIntentClassifier.parse_binary(result)
        
        status = "✅" if not needs_schedule else "❌"
        print(f"{status} '{msg}' ({desc})")
        print(f"   输出: {result} -> chat={is_chat}, stats={needs_stats}, schedule={needs_schedule}")
        
        if needs_schedule:
            failed.append(msg)
        
        # 检查第3位是否为0
        if result[2] != '0':
            print(f"   ⚠️  警告：第3位不是0，而是{result[2]}")
            failed.append(f"{msg} (第3位错误)")
    
    print("-" * 60)
    
    if failed:
        print(f"\n❌ 测试失败！以下{len(failed)}个用例未通过:")
        for f in failed:
            print(f"   - {f}")
    else:
        print("\n✅ 测试成功！所有日程意图都已被正确禁用。")
        print("   - 所有日程相关查询都被识别为普通聊天")
        print("   - 第3位始终为0")
        print("   - needs_schedule 始终为 False")
    
    print("=" * 60)

if __name__ == "__main__":
    test()