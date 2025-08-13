#!/usr/bin/env python3
"""
测试AFK检测功能（简化版）

该脚本直接测试AFK检测，避免循环导入问题
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from aw_client import ActivityWatchClient

def test_afk_detection():
    """直接测试AFK检测"""
    print("\n" + "="*60)
    print("AFK 检测测试（直接连接ActivityWatch）")
    print("="*60)
    
    try:
        # 直接创建ActivityWatch客户端
        client = ActivityWatchClient("afk-test-client", testing=False)
        client.connect()
        
        # 获取所有桶
        buckets = client.get_buckets()
        
        # 查找AFK桶
        afk_bucket = None
        for bucket_id in buckets:
            if "afk" in bucket_id and "watcher" in bucket_id:
                afk_bucket = bucket_id
                break
        
        if not afk_bucket:
            print("❌ 未找到AFK监视器桶")
            print("   请确保 aw-watcher-afk 正在运行")
            return
        
        print(f"✅ 找到AFK桶: {afk_bucket}")
        
        # 获取过去5分钟的事件
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=5)
        
        events = client.get_events(
            afk_bucket,
            start=start_time,
            end=end_time
        )
        
        print(f"\n📊 过去5分钟的AFK事件数: {len(events)}")
        
        # 分析事件
        afk_seconds = 0
        not_afk_seconds = 0
        last_active_time = None
        events_sorted = sorted(events, key=lambda e: e.timestamp)
        
        print("\n📝 事件详情（最近10个）：")
        for i, event in enumerate(events_sorted[-10:], 1):
            status = event.data.get('status', 'unknown')
            duration = event.duration.total_seconds()
            timestamp = event.timestamp.strftime('%H:%M:%S')
            
            if status == 'afk':
                afk_seconds += duration
                emoji = "💤"
            else:  # not-afk
                not_afk_seconds += duration
                last_active_time = event.timestamp + event.duration
                emoji = "⚡"
            
            print(f"   {i:2}. [{timestamp}] {emoji} {status:8} - {duration:6.1f}秒")
        
        # 计算持续AFK
        continuous_afk = False
        seconds_since_active = 0
        
        if last_active_time:
            seconds_since_active = (end_time - last_active_time).total_seconds()
            continuous_afk = seconds_since_active > 240
        elif afk_seconds > 240:
            continuous_afk = True
            seconds_since_active = afk_seconds
        
        print(f"\n📈 统计摘要：")
        print(f"   总AFK时间: {afk_seconds:.1f} 秒 ({afk_seconds/60:.1f} 分钟)")
        print(f"   总活动时间: {not_afk_seconds:.1f} 秒 ({not_afk_seconds/60:.1f} 分钟)")
        print(f"   距离最后活动: {seconds_since_active:.1f} 秒前")
        print(f"   持续AFK状态: {continuous_afk}")
        
        # 监督模式判断
        should_skip_supervision = continuous_afk or seconds_since_active > 240 or afk_seconds > 270
        
        print(f"\n🎯 监督模式判断：")
        if should_skip_supervision:
            print("   ✅ 应跳过监督（用户AFK）")
            reasons = []
            if continuous_afk:
                reasons.append("持续AFK超过4分钟")
            if seconds_since_active > 240:
                reasons.append(f"距离最后活动{seconds_since_active/60:.1f}分钟")
            if afk_seconds > 270:
                reasons.append(f"总AFK时间{afk_seconds/60:.1f}分钟")
            print(f"   原因: {' | '.join(reasons)}")
        else:
            print("   ⚡ 应执行监督（用户活跃）")
            print(f"   用户在过去5分钟活跃了 {not_afk_seconds/60:.1f} 分钟")
        
        client.disconnect()
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    
    print("\n💡 使用提示：")
    print("1. 确保 ActivityWatch 正在运行")
    print("2. 如果要测试AFK检测，可以离开电脑5分钟")
    print("3. 监督模式会在用户持续AFK超过4分钟时跳过检查")

if __name__ == "__main__":
    test_afk_detection()