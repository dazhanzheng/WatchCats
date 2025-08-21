#!/usr/bin/env python3
"""
测试巴利的记忆系统
"""

import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.core.config_manager import ConfigManager
from baal.desktop_pet.core.llm_handler import LLMHandler
from baal.desktop_pet.core.persona_manager import PersonaLevel
from langchain_core.messages import HumanMessage, AIMessage


def test_memory_system():
    """测试记忆系统的完整流程"""
    
    print("=" * 60)
    print("测试巴利的记忆系统")
    print("=" * 60)
    
    # 1. 初始化配置管理器
    config_manager = ConfigManager()
    print(f"\n1. 配置目录: {config_manager.config_dir}")
    
    # 2. 清除旧的历史记录
    print("\n2. 清除旧的历史记录...")
    config_manager.clear_conversation_history()
    
    # 3. 初始化LLM处理器（第一次，无历史）
    print("\n3. 初始化LLM处理器（无历史记录）...")
    if not config_manager.is_configured():
        print("   错误：未配置API密钥")
        return
    
    llm_handler = LLMHandler(
        base_url=config_manager.get_base_url(),
        api_key=config_manager.get_api_key(),
        model=config_manager.get_model(),
        persona_level=PersonaLevel.STRICT_MASTER
    )
    
    print(f"   是否有历史记录: {llm_handler.has_conversation_history()}")
    
    # 4. 模拟对话
    print("\n4. 模拟对话...")
    test_messages = [
        ("你好", "仆人，有何吩咐？"),
        ("今天天气怎么样？", "我的职责是监督你的工作，不是闲聊天气。"),
        ("我要开始工作了", "很好，我会监视你的每一个动作。")
    ]
    
    for user_msg, ai_msg in test_messages:
        llm_handler.messages.append(HumanMessage(content=user_msg))
        llm_handler.messages.append(AIMessage(content=ai_msg))
        print(f"   用户: {user_msg}")
        print(f"   巴利: {ai_msg}")
    
    # 5. 保存对话历史
    print("\n5. 保存对话历史...")
    success = llm_handler.save_conversation_history()
    print(f"   保存成功: {success}")
    
    # 6. 重新初始化LLM处理器（有历史）
    print("\n6. 重新初始化LLM处理器（有历史记录）...")
    del llm_handler  # 删除旧实例
    
    llm_handler2 = LLMHandler(
        base_url=config_manager.get_base_url(),
        api_key=config_manager.get_api_key(),
        model=config_manager.get_model(),
        persona_level=PersonaLevel.STRICT_MASTER
    )
    
    print(f"   是否有历史记录: {llm_handler2.has_conversation_history()}")
    print(f"   历史消息数量: {len(llm_handler2.messages) - 1}")  # 减去系统消息
    
    # 7. 显示加载的历史
    print("\n7. 加载的历史记录:")
    for i, msg in enumerate(llm_handler2.messages[1:], 1):  # 跳过系统消息
        if isinstance(msg, HumanMessage):
            print(f"   [{i}] 用户: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"   [{i}] 巴利: {msg.content}")
    
    # 8. 测试对话总结（需要达到40条消息）
    print("\n8. 测试对话总结功能...")
    print(f"   当前消息数: {len([m for m in llm_handler2.messages if not hasattr(m, 'content') or '[历史总结]' not in m.content])}")
    print(f"   需要 40 条消息触发总结（20轮对话）")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_memory_system()