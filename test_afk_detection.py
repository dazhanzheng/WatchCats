#!/usr/bin/env python3
"""
测试AFK检测功能

该脚本测试监督模式的AFK检测是否正确工作：
1. 连接到ActivityWatch获取AFK数据
2. 检查是否正确判断持续AFK状态
3. 显示详细的AFK统计信息
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from baal.aw_stats.stats_processor import StatsProcessor
from baal.desktop_pet.supervision_mode import SupervisionMode

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_afk_stats():
    """测试AFK统计数据获取"""
    print("\n" + "="*60)
    print("测试 AFK 统计数据获取")
    print("="*60)
    
    try:
        with StatsProcessor() as sp:
            # 获取AFK统计
            afk_stats = sp.get_afk_time_5m()
            
            print("\n📊 过去5分钟的AFK统计：")
            print(f"   总AFK时间: {afk_stats.get('afk_seconds', 0):.1f} 秒")
            print(f"   持续AFK: {afk_stats.get('continuous_afk', False)}")
            print(f"   距离最后活动: {afk_stats.get('last_active_seconds_ago', 0):.1f} 秒前")
            
            # 判断是否应该跳过监督
            afk_seconds = afk_stats.get('afk_seconds', 0)
            continuous_afk = afk_stats.get('continuous_afk', False)
            last_active_seconds = afk_stats.get('last_active_seconds_ago', 0)
            
            # 使用与监督模式相同的判断逻辑
            should_skip = continuous_afk or last_active_seconds > 240 or afk_seconds > 270
            
            print(f"\n🎯 监督模式判断:")
            print(f"   应该跳过监督: {should_skip}")
            
            if should_skip:
                print("   原因: ", end="")
                reasons = []
                if continuous_afk:
                    reasons.append("持续AFK")
                if last_active_seconds > 240:
                    reasons.append(f"超过4分钟无活动({last_active_seconds:.0f}秒)")
                if afk_seconds > 270:
                    reasons.append(f"总AFK时间超过4.5分钟({afk_seconds:.0f}秒)")
                print(" | ".join(reasons))
            else:
                print("   用户活跃，应该进行监督检查")
            
            # 获取更详细的AFK事件
            print("\n📝 最近的AFK事件详情：")
            afk_bucket = sp._get_afk_bucket()
            if afk_bucket:
                from datetime import timezone
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(minutes=5)
                
                events = sp.client.get_events(
                    afk_bucket,
                    start=start_time,
                    end=end_time,
                    limit=10
                )
                
                for i, event in enumerate(events[:5], 1):
                    status = event.data.get('status', 'unknown')
                    duration = event.duration.total_seconds()
                    timestamp = event.timestamp.strftime('%H:%M:%S')
                    print(f"   {i}. [{timestamp}] {status:8} - {duration:.1f}秒")
                    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def test_supervision_afk_check():
    """测试监督模式的AFK检查"""
    print("\n" + "="*60)
    print("测试监督模式 AFK 检查")
    print("="*60)
    
    try:
        # 创建监督模式实例
        supervision = SupervisionMode()
        
        # 测试AFK检查
        is_afk = supervision._is_user_afk()
        
        print(f"\n🔍 监督模式AFK检查结果: {is_afk}")
        
        if is_afk:
            print("   ✅ 用户处于AFK状态，监督模式将跳过检查")
            print("   💤 这是正确的行为 - 用户离开时不应该被打扰")
        else:
            print("   ⚡ 用户活跃，监督模式将执行检查")
            print("   👀 这是正确的行为 - 活跃用户需要被监督")
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("\n" + "="*60)
    print("AFK 检测功能测试")
    print("="*60)
    print("\n说明：")
    print("1. 此测试连接到ActivityWatch获取真实的AFK数据")
    print("2. 确保ActivityWatch正在运行")
    print("3. 测试将显示过去5分钟的AFK状态")
    
    # 运行测试
    test_afk_stats()
    test_supervision_afk_check()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    
    print("\n💡 提示：")
    print("- 如果你刚才一直在使用电脑，应该显示'用户活跃'")
    print("- 如果你离开电脑超过4分钟，应该显示'用户AFK'")
    print("- 可以离开电脑5分钟后再运行测试，验证AFK检测")

if __name__ == "__main__":
    main()