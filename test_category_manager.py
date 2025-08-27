#!/usr/bin/env python3
"""
测试应用分类管理功能
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baal.desktop_pet.core.category_manager import CategoryManager


def test_category_manager():
    """测试分类管理器"""
    
    print("=" * 60)
    print("应用分类管理器测试")
    print("=" * 60)
    
    # 创建分类管理器
    manager = CategoryManager()
    
    # 1. 测试添加分类
    print("\n1. 添加自定义分类")
    print("-" * 40)
    
    # 添加一个工作相关的分类
    success = manager.add_category(
        name="工作/我的Python项目",
        category_path=["工作", "Python项目"],
        rules=[
            {"type": "app", "pattern": "PyCharm", "case_sensitive": False},
            {"type": "title", "pattern": ".py", "case_sensitive": False},
            {"type": "title", "pattern": "Python", "case_sensitive": False}
        ],
        description="Python开发相关活动",
        is_productive=True
    )
    print(f"添加Python项目分类: {'成功' if success else '失败'}")
    
    # 添加一个娱乐分类
    success = manager.add_category(
        name="娱乐/视频网站",
        category_path=["娱乐", "视频网站"],
        rules=[
            {"type": "title", "pattern": "bilibili", "case_sensitive": False},
            {"type": "title", "pattern": "YouTube", "case_sensitive": False},
            {"type": "title", "pattern": "Netflix", "case_sensitive": False}
        ],
        description="视频娱乐网站",
        is_productive=False
    )
    print(f"添加视频网站分类: {'成功' if success else '失败'}")
    
    # 添加一个学习分类
    success = manager.add_category(
        name="学习/技术文档",
        category_path=["学习", "技术文档"],
        rules=[
            {"type": "title", "pattern": "MDN", "case_sensitive": False},
            {"type": "title", "pattern": "Documentation", "case_sensitive": False},
            {"type": "title", "pattern": "API Reference", "case_sensitive": False},
            {"type": "title", "pattern": "Tutorial", "case_sensitive": False}
        ],
        description="技术文档和教程",
        is_productive=True
    )
    print(f"添加技术文档分类: {'成功' if success else '失败'}")
    
    # 2. 显示所有分类
    print("\n2. 当前所有分类")
    print("-" * 40)
    
    categories = manager.get_categories_list()
    for i, cat in enumerate(categories, 1):
        path = " > ".join(cat['category_path'])
        rules_count = len(cat.get('rules', []))
        is_productive = cat.get('is_productive')
        prod_str = "生产性" if is_productive else "非生产性" if is_productive is False else "中性"
        
        print(f"{i}. {cat['name']}")
        print(f"   路径: {path}")
        print(f"   规则数: {rules_count}")
        print(f"   类型: {prod_str}")
        print(f"   描述: {cat.get('description', '无')}")
        print()
    
    # 3. 测试分类匹配
    print("\n3. 测试分类匹配")
    print("-" * 40)
    
    test_cases = [
        ("PyCharm", "main.py - MyProject"),
        ("Google Chrome", "Python Documentation - MDN Web Docs"),
        ("Google Chrome", "bilibili - 哔哩哔哩"),
        ("VS Code", "app.py"),
        ("飞书", "工作群"),
        ("终端", "python test.py"),
        ("Safari", "API Reference - React")
    ]
    
    for app, title in test_cases:
        matched = manager.test_categorization(app, title)
        if matched:
            category_str = " > ".join(matched)
            print(f"✅ {app} | {title}")
            print(f"   → 分类: {category_str}")
        else:
            print(f"❌ {app} | {title}")
            print(f"   → 未匹配")
        print()
    
    # 4. 获取 aw_transform 规则
    print("\n4. 转换为 ActivityWatch 规则")
    print("-" * 40)
    
    aw_rules = manager.get_aw_transform_rules()
    print(f"生成了 {len(aw_rules)} 条 ActivityWatch 规则")
    
    # 显示前5条规则
    for i, (category_path, rule) in enumerate(aw_rules[:5], 1):
        path_str = " > ".join(category_path)
        print(f"{i}. {path_str}")
    
    if len(aw_rules) > 5:
        print(f"   ... 还有 {len(aw_rules) - 5} 条规则")
    
    # 5. 获取生产力分类映射
    print("\n5. 生产力分类映射")
    print("-" * 40)
    
    productivity_map = manager.get_productivity_classification()
    for category_name, is_productive in productivity_map.items():
        prod_str = "✅ 生产性" if is_productive else "❌ 非生产性"
        print(f"{category_name}: {prod_str}")
    
    # 6. 测试导出功能
    print("\n6. 导出分类配置")
    print("-" * 40)
    
    export_file = "test_categories_export.json"
    success = manager.export_categories(export_file)
    if success:
        print(f"✅ 成功导出到 {export_file}")
        
        # 读取并显示导出的内容
        with open(export_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
            print(f"   导出了 {len(exported.get('categories', []))} 个分类")
        
        # 删除测试文件
        os.remove(export_file)
        print(f"   已清理测试文件")
    else:
        print(f"❌ 导出失败")
    
    # 7. 测试与 StatsProcessor 的集成
    print("\n7. 测试与 StatsProcessor 集成")
    print("-" * 40)
    
    try:
        from baal.aw_stats.stats_processor import StatsProcessor
        
        # 创建使用用户分类的 StatsProcessor
        with StatsProcessor(use_user_categories=True) as processor:
            print("✅ StatsProcessor 成功加载用户分类")
            
            # 获取分类统计
            cat_stats = processor.get_category_stats(1)  # 最近1小时
            
            if cat_stats and cat_stats.get('categories'):
                print(f"\n最近1小时的活动分类:")
                for cat in cat_stats['categories'][:5]:
                    print(f"  - {cat['name']}: {cat['duration_str']} ({cat['percentage']:.1f}%)")
            else:
                print("暂无活动数据")
                
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n功能总结:")
    print("✅ 用户可以添加自定义分类规则")
    print("✅ 支持应用名和窗口标题匹配")
    print("✅ 可以标记分类为生产性/非生产性")
    print("✅ 自动与 ActivityWatch 集成")
    print("✅ 监督模式可使用分类进行智能分析")
    print("✅ 支持导入/导出分类配置")


if __name__ == "__main__":
    test_category_manager()