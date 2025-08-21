#!/usr/bin/env python3
"""
简单测试应用名称标准化功能
"""

def normalize_app_name(app_name: str) -> str:
    """
    标准化应用名称，处理特殊应用
    
    Args:
        app_name: 原始应用名称
        
    Returns:
        标准化后的应用名称
    """
    if not app_name:
        return "未知应用"
        
    # 转换为小写进行比较
    app_lower = app_name.lower()
    
    # 将 WatchCats 或 Watch Cats 识别为巴利自己
    if "watchcats" in app_lower.replace(" ", "") or "watch cats" in app_lower:
        return "巴利桌面宠物（与主人互动）"
    
    # 将 Baal 相关应用识别为巴利自己
    if "baal" in app_lower or "desktop pet" in app_lower or "桌面宠物" in app_name:
        return "巴利桌面宠物（与主人互动）"
        
    # 移除常见的文件扩展名
    if app_name.endswith(".exe"):
        app_name = app_name[:-4]
    elif app_name.endswith(".app"):
        app_name = app_name[:-4]
        
    return app_name


def test():
    """测试应用名称标准化"""
    
    print("=" * 60)
    print("测试应用名称标准化")
    print("=" * 60)
    
    # 测试不同的应用名称
    test_cases = [
        "WatchCats.exe",
        "watchcats",
        "WATCHCATS",
        "Baal Desktop Pet",
        "baal",
        "Desktop Pet",
        "Chrome.exe",
        "微信",
        "飞书",
        "Visual Studio Code",
        "Watch Cats.app",
        "WatchCats"
    ]
    
    print("\n应用名称映射测试:")
    print("-" * 40)
    
    for app_name in test_cases:
        normalized = normalize_app_name(app_name)
        if normalized == "巴利桌面宠物（与主人互动）":
            print(f"✅ {app_name:30} -> {normalized}")
        else:
            print(f"   {app_name:30} -> {normalized}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test()