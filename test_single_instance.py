#!/usr/bin/env python
"""
测试单实例功能
"""

import sys
import time
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.core.single_instance import SingleInstance, check_single_instance


def test_basic_lock():
    """测试基本的锁机制"""
    print("测试基本锁机制...")
    
    # 创建第一个实例
    instance1 = SingleInstance("TestApp")
    result1 = instance1.check()
    print(f"第一个实例获取锁: {result1}")
    assert result1 == True, "第一个实例应该成功获取锁"
    
    # 尝试创建第二个实例
    instance2 = SingleInstance("TestApp")
    result2 = instance2.check()
    print(f"第二个实例获取锁: {result2}")
    assert result2 == False, "第二个实例不应该获取到锁"
    
    # 释放第一个实例的锁
    instance1.release()
    print("第一个实例释放锁")
    
    # 现在第三个实例应该可以获取锁
    instance3 = SingleInstance("TestApp")
    result3 = instance3.check()
    print(f"第三个实例获取锁（在第一个释放后）: {result3}")
    assert result3 == True, "第三个实例应该成功获取锁"
    
    # 清理
    instance3.release()
    
    print("✅ 基本锁机制测试通过\n")


def test_check_function():
    """测试便捷检查函数"""
    print("测试便捷检查函数...")
    
    # 第一次调用应该成功
    lock1 = check_single_instance("TestApp2")
    assert lock1 is not None, "第一次调用应该返回锁对象"
    print("第一次调用成功获取锁")
    
    # 第二次调用应该失败（会显示消息）
    print("尝试第二次调用（应该失败）...")
    lock2 = check_single_instance("TestApp2")
    assert lock2 is None, "第二次调用应该返回 None"
    print("第二次调用正确失败")
    
    # 释放第一个锁
    lock1.release()
    
    print("✅ 便捷函数测试通过\n")


def test_process_check():
    """测试进程检查功能"""
    print("测试进程检查功能...")
    
    instance = SingleInstance("TestApp3")
    
    # 测试当前进程
    current_pid = os.getpid()
    is_running = instance._is_process_running(current_pid)
    print(f"当前进程 (PID: {current_pid}) 运行状态: {is_running}")
    assert is_running == True, "当前进程应该在运行"
    
    # 测试不存在的进程
    fake_pid = 999999
    is_running = instance._is_process_running(fake_pid)
    print(f"不存在的进程 (PID: {fake_pid}) 运行状态: {is_running}")
    assert is_running == False, "不存在的进程不应该在运行"
    
    print("✅ 进程检查测试通过\n")


def test_file_lock_persistence():
    """测试文件锁的持久性"""
    print("测试文件锁持久性...")
    
    # 创建并获取锁
    instance1 = SingleInstance("TestApp4")
    instance1._init_file_lock()  # 强制使用文件锁
    result = instance1._check_file_lock()
    print(f"创建文件锁: {result}")
    assert result == True, "应该成功创建文件锁"
    
    # 检查锁文件是否存在
    if hasattr(instance1, 'lock_file_path'):
        exists = instance1.lock_file_path.exists()
        print(f"锁文件存在: {exists}")
        assert exists == True, "锁文件应该存在"
        
        # 读取锁文件内容
        with open(instance1.lock_file_path, 'r') as f:
            pid = f.read()
        print(f"锁文件中的 PID: {pid}")
        assert pid == str(os.getpid()), "锁文件应该包含当前进程 PID"
    
    # 释放锁
    instance1.release()
    
    # 检查锁文件是否被删除
    if hasattr(instance1, 'lock_file_path'):
        exists = instance1.lock_file_path.exists()
        print(f"释放后锁文件存在: {exists}")
        assert exists == False, "释放后锁文件应该被删除"
    
    print("✅ 文件锁持久性测试通过\n")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("单实例功能测试")
    print("=" * 50)
    print()
    
    try:
        test_basic_lock()
        test_check_function()
        test_process_check()
        test_file_lock_persistence()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()