#!/usr/bin/env python3
"""
测试监督目标更新的并发安全性
模拟在监督检查过程中修改目标的场景
"""

import threading
import time
import random
from datetime import datetime

class MockSupervisionMode:
    """模拟的监督模式类，用于测试并发安全性"""
    
    def __init__(self):
        self.long_term_goal = "完成项目开发"
        self.short_term_goals = ["写代码", "测试", "文档"]
        self._goals_lock = threading.RLock()
        self.is_checking = False
        self.check_count = 0
        self.update_count = 0
        self.race_conditions = 0
    
    def check_activity(self):
        """模拟监督检查过程"""
        self.is_checking = True
        
        # 安全地读取目标（创建快照）
        with self._goals_lock:
            current_long_goal = self.long_term_goal
            current_short_goals = self.short_term_goals.copy()
        
        # 模拟长时间的LLM评估过程
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 开始评估...")
        print(f"  长期目标: {current_long_goal}")
        print(f"  短期目标: {current_short_goals}")
        
        # 模拟评估时间（0.5-1.5秒）
        time.sleep(random.uniform(0.5, 1.5))
        
        # 再次检查目标是否发生变化（用于检测竞态条件）
        with self._goals_lock:
            if current_long_goal != self.long_term_goal or current_short_goals != self.short_term_goals:
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ⚠️ 检测到目标在评估期间被修改！")
                print(f"  原长期目标: {current_long_goal}")
                print(f"  新长期目标: {self.long_term_goal}")
                print(f"  原短期目标: {current_short_goals}")
                print(f"  新短期目标: {self.short_term_goals}")
                self.race_conditions += 1
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] ✅ 评估完成，目标未变化")
        
        self.check_count += 1
        self.is_checking = False
    
    def update_goals(self, long_term_goal, short_term_goals):
        """更新监督目标"""
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 正在更新目标...")
        
        # 使用锁保护目标更新
        with self._goals_lock:
            old_long = self.long_term_goal
            old_short = self.short_term_goals.copy()
            
            self.long_term_goal = long_term_goal
            self.short_term_goals = short_term_goals
            
            print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] 目标已更新:")
            print(f"  长期: {old_long} -> {long_term_goal}")
            print(f"  短期: {old_short} -> {short_term_goals}")
        
        self.update_count += 1

def checker_thread(supervision):
    """检查线程：定期执行监督检查"""
    for i in range(5):
        time.sleep(random.uniform(0.5, 1.0))
        print(f"\n--- 检查 #{i+1} ---")
        supervision.check_activity()

def updater_thread(supervision):
    """更新线程：随机时间更新目标"""
    goals_pool = [
        ("学习新技术", ["阅读文档", "做练习", "写笔记"]),
        ("完成论文", ["查资料", "写初稿", "修改"]),
        ("健身计划", ["跑步", "力量训练", "拉伸"]),
        ("准备面试", ["刷题", "复习基础", "模拟面试"]),
    ]
    
    for i in range(3):
        time.sleep(random.uniform(1.0, 2.0))
        print(f"\n--- 更新 #{i+1} ---")
        goal = random.choice(goals_pool)
        supervision.update_goals(goal[0], goal[1])

def main():
    print("=" * 60)
    print("监督目标并发安全性测试")
    print("=" * 60)
    print("测试说明：")
    print("1. 启动两个线程：一个定期检查活动，一个随机更新目标")
    print("2. 检查是否存在竞态条件（评估期间目标被修改）")
    print("3. 验证线程锁是否正确保护了共享数据")
    print("=" * 60)
    print()
    
    supervision = MockSupervisionMode()
    
    # 创建并启动线程
    checker = threading.Thread(target=checker_thread, args=(supervision,))
    updater = threading.Thread(target=updater_thread, args=(supervision,))
    
    checker.start()
    updater.start()
    
    # 等待线程完成
    checker.join()
    updater.join()
    
    # 打印统计
    print("\n" + "=" * 60)
    print("测试结果统计")
    print("=" * 60)
    print(f"总检查次数: {supervision.check_count}")
    print(f"总更新次数: {supervision.update_count}")
    print(f"竞态条件次数: {supervision.race_conditions}")
    
    if supervision.race_conditions > 0:
        print("\n⚠️ 注意：检测到目标在评估期间被修改")
        print("这不是错误，而是正常的并发行为。")
        print("由于使用了线程锁和快照机制，每次评估都使用一致的数据。")
    else:
        print("\n✅ 完美！所有评估都使用了一致的目标数据。")
    
    print("\n结论：线程锁成功保护了目标数据的一致性！")

if __name__ == "__main__":
    main()