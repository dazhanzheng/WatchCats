#!/usr/bin/env python3
"""
测试监督模式工作流程
验证是否正确获取5分钟、2小时、24小时数据
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.core.config_manager import ConfigManager

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# 获取监督模式日志器
supervision_logger = logging.getLogger('supervision')
supervision_logger.setLevel(logging.DEBUG)

def test_comprehensive_stats():
    """测试综合统计数据获取"""
    print("\n" + "="*80)
    print("测试监督模式工作流程")
    print("="*80)
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    print("\n[1] 测试多时段数据获取")
    print("-" * 40)
    
    # 获取综合统计
    stats = supervision._get_comprehensive_activity_stats()
    
    if stats:
        print("\n✓ 成功获取多时段数据:")
        
        # 显示各时段数据概要
        for key, label in [
            ('stats_5m', '5分钟数据'),
            ('stats_2h', '2小时数据'),
            ('stats_today', '今日数据'),
            ('stats_24h', '24小时数据')
        ]:
            if key in stats and stats[key]:
                data = stats[key]
                if isinstance(data, str):
                    lines = data.split('\n')
                    print(f"\n  【{label}】")
                    print(f"    - 数据长度: {len(data)} 字符")
                    print(f"    - 行数: {len(lines)}")
                    # 显示前3行
                    for i, line in enumerate(lines[:3]):
                        if line.strip():
                            print(f"    - {line[:80]}...")
                            if i == 2:
                                print(f"    ... (还有 {len(lines)-3} 行)")
                                break
            else:
                print(f"\n  【{label}】: 无数据")
        
        print(f"\n  时间戳: {stats.get('timestamp', 'N/A')}")
    else:
        print("\n✗ 获取数据失败")
    
    return stats

def test_evaluation_prompt(stats):
    """测试评估提示词生成"""
    print("\n[2] 测试LLM评估流程")
    print("-" * 40)
    
    supervision = SupervisionMode()
    
    # 设置测试目标
    supervision.long_term_goal = "完成Python项目开发"
    supervision.short_term_goals = ["修复bug", "编写测试", "优化性能"]
    
    print(f"  长期目标: {supervision.long_term_goal}")
    print(f"  短期目标: {', '.join(supervision.short_term_goals)}")
    
    # 测试评估（如果有LLM配置）
    if supervision.llm_assistant:
        print("\n  开始LLM评估...")
        result = supervision._evaluate_activity_enhanced(stats)
        
        if result:
            print("\n  ✓ 评估结果:")
            print(f"    - 需要提醒: {result.get('should_remind', False)}")
            print(f"    - 偏离程度: {result.get('deviation_level', '未知')}")
            print(f"    - 分析说明: {result.get('analysis', 'N/A')[:100]}...")
            
            if result.get('time_period_analysis'):
                print("\n    时段分析:")
                for period, analysis in result['time_period_analysis'].items():
                    print(f"      - {period}: {analysis[:50]}...")
            
            if result.get('reminder_message'):
                print(f"\n    提醒消息: {result['reminder_message'][:100]}...")
        else:
            print("\n  ✗ 评估失败或无需提醒")
    else:
        print("\n  ⚠ 未配置LLM，跳过评估测试")

def test_full_workflow():
    """测试完整工作流程"""
    print("\n[3] 测试完整检查流程")
    print("-" * 40)
    
    supervision = SupervisionMode()
    
    # 设置测试目标
    supervision.long_term_goal = "专注编程工作"
    supervision.short_term_goals = ["完成代码审查", "修复测试失败"]
    
    print(f"  设置监督目标...")
    print(f"  - 长期: {supervision.long_term_goal}")
    print(f"  - 短期: {supervision.short_term_goals}")
    
    # 执行一次检查
    print("\n  执行活动检查...")
    supervision._check_activity()
    
    print("\n  ✓ 检查完成")

def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("监督模式工作流程测试")
    print("="*80)
    print("\n说明:")
    print("1. 此测试验证监督模式是否正确获取所有时段数据")
    print("2. 测试数据包括：5分钟、2小时、24小时")
    print("3. 验证LLM评估流程是否正确处理多时段数据")
    
    # 测试1：获取多时段数据
    stats = test_comprehensive_stats()
    
    if stats:
        # 测试2：评估流程
        test_evaluation_prompt(stats)
    
    # 测试3：完整流程
    test_full_workflow()
    
    print("\n" + "="*80)
    print("监督模式工作流程总结")
    print("="*80)
    print("\n✓ 工作流程:")
    print("  1. 每5秒执行一次检查（调试模式）")
    print("  2. 同时获取5分钟、2小时、24小时数据")
    print("  3. 将所有数据发送给LLM进行综合评估")
    print("  4. LLM根据多时段数据判断是否需要提醒")
    print("  5. 返回包含时段分析的详细评估结果")
    
    print("\n✓ 决策规则:")
    print("  - 5分钟数据: 反映即时行为")
    print("  - 2小时数据: 显示短期趋势")
    print("  - 24小时数据: 展示整体表现")
    print("  - 综合判断: 避免过度提醒，平衡即时和长期表现")
    
    print("\n💡 提示:")
    print("  - 查看日志了解详细的数据获取过程")
    print("  - 开发者控制台可实时查看监督模式日志")
    print("  - 使用 SUPERVISION_CHECK_INTERVAL 环境变量调整检查间隔")
    print("="*80)

if __name__ == "__main__":
    main()