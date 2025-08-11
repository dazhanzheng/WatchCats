#!/usr/bin/env python
"""
SSL 修复加载器 - 在导入任何库之前设置 SSL 环境
"""
import os
import sys
import ssl
import warnings

# 立即设置环境变量
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_CERT_FILE'] = ''
os.environ['SSL_CERT_DIR'] = ''

# 修改 SSL 上下文
try:
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # 修补 ssl 模块
    old_match_hostname = ssl.match_hostname
    def new_match_hostname(cert, hostname):
        pass
    ssl.match_hostname = new_match_hostname
except:
    pass

# 忽略所有警告
warnings.filterwarnings('ignore')

# 现在导入并运行主程序
if __name__ == "__main__":
    from baal.desktop_pet import main
    main()