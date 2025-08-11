#!/usr/bin/env python3
"""
修复 SSL 错误的辅助脚本
"""
import os
import sys
import ssl
import warnings

# 忽略 SSL 警告
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

# 设置环境变量来处理 SSL 问题
os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

# 创建未验证的 SSL 上下文
ssl._create_default_https_context = ssl._create_unverified_context

# 导入并运行主程序
if __name__ == "__main__":
    # 添加项目路径到系统路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # 导入并运行主程序
    from baal.desktop_pet import main
    main()