#!/usr/bin/env python
"""
日志查看工具脚本

提供便捷的日志查看、搜索、过滤和实时监控功能
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# 日志目录
LOG_DIR = Path.home() / '.baal_pet' / 'logs'

# 日志文件映射
LOG_FILES = {
    'main': 'baal_*.log',
    'error': 'errors.log',
    'performance': 'performance.log',
    'api': 'api_calls.log',
    'ui': 'ui_events.log',
    'schedule': 'schedule.log',
    'aw': 'activity_watch.log'
}

# 颜色代码
COLORS = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'GRAY': '\033[90m'
}

# 日志级别颜色
LEVEL_COLORS = {
    'DEBUG': COLORS['GRAY'],
    'INFO': COLORS['GREEN'],
    'WARNING': COLORS['YELLOW'],
    'ERROR': COLORS['RED'],
    'CRITICAL': COLORS['MAGENTA']
}


def colorize(text: str, color: str) -> str:
    """为文本添加颜色"""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{COLORS['RESET']}"


def format_timestamp(timestamp: str) -> str:
    """格式化时间戳"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S.%f')[:-3]
    except:
        return timestamp


def parse_json_log(line: str) -> Optional[Dict[str, Any]]:
    """解析JSON格式的日志行"""
    try:
        return json.loads(line)
    except:
        return None


def parse_text_log(line: str) -> Optional[Dict[str, Any]]:
    """解析文本格式的日志行"""
    # 尝试匹配标准格式: 2025-08-10 15:30:45 - module - [LEVEL] - message
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?) - ([\w\.]+) - \[(\w+)\] - (.*)$'
    match = re.match(pattern, line)
    
    if match:
        return {
            'timestamp': match.group(1),
            'logger': match.group(2),
            'level': match.group(3),
            'message': match.group(4)
        }
    
    # 尝试简单格式: 15:30:45 - module - LEVEL - message
    pattern = r'^(\d{2}:\d{2}:\d{2}(?:\.\d+)?) - ([\w\.]+) - (\w+) - (.*)$'
    match = re.match(pattern, line)
    
    if match:
        return {
            'timestamp': match.group(1),
            'logger': match.group(2),
            'level': match.group(3),
            'message': match.group(4)
        }
    
    return None


def format_log_entry(entry: Dict[str, Any], verbose: bool = False) -> str:
    """格式化日志条目"""
    level = entry.get('level', 'INFO')
    level_color = LEVEL_COLORS.get(level, COLORS['WHITE'])
    
    timestamp = format_timestamp(entry.get('timestamp', ''))
    logger = entry.get('logger', 'unknown')
    message = entry.get('message', '')
    
    # 基本格式
    output = f"{colorize(timestamp, COLORS['GRAY'])} "
    output += f"{colorize(f'[{level:8}]', level_color)} "
    output += f"{colorize(logger, COLORS['CYAN'])} - "
    output += message
    
    # 详细模式
    if verbose:
        if 'function' in entry:
            output += f"\n  {colorize('Function:', COLORS['GRAY'])} {entry['function']}"
        if 'line' in entry:
            output += f" (line {entry['line']})"
        if 'extra' in entry and isinstance(entry['extra'], dict):
            output += f"\n  {colorize('Extra:', COLORS['GRAY'])} {json.dumps(entry['extra'], ensure_ascii=False)}"
        if 'exception' in entry:
            output += f"\n  {colorize('Exception:', COLORS['RED'])} {entry['exception'].get('type', '')} - {entry['exception'].get('message', '')}"
            if 'traceback' in entry['exception']:
                for line in entry['exception']['traceback']:
                    output += f"\n    {colorize(line.rstrip(), COLORS['GRAY'])}"
    
    return output


def read_log_file(file_path: Path, lines: int = 0, follow: bool = False) -> List[str]:
    """读取日志文件"""
    if not file_path.exists():
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        if lines > 0:
            # 读取最后n行
            all_lines = f.readlines()
            return all_lines[-lines:]
        else:
            return f.readlines()


def search_logs(pattern: str, log_type: str = 'main', lines: int = 100) -> List[Dict[str, Any]]:
    """搜索日志"""
    results = []
    
    # 获取日志文件
    if log_type in LOG_FILES:
        log_pattern = LOG_FILES[log_type]
        log_files = sorted(LOG_DIR.glob(log_pattern))
    else:
        log_files = LOG_DIR.glob('*.log')
    
    regex = re.compile(pattern, re.IGNORECASE)
    
    for log_file in log_files:
        log_lines = read_log_file(log_file, lines=lines)
        
        for line in log_lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试解析日志
            entry = parse_json_log(line) or parse_text_log(line)
            
            if entry:
                # 搜索所有字段
                searchable = json.dumps(entry, ensure_ascii=False)
                if regex.search(searchable):
                    entry['_file'] = log_file.name
                    results.append(entry)
            elif regex.search(line):
                # 未解析的行，直接匹配
                results.append({
                    'message': line,
                    '_file': log_file.name
                })
    
    return results


def tail_log(log_type: str = 'main', follow: bool = False):
    """实时查看日志（类似tail -f）"""
    # 获取最新的日志文件
    if log_type in LOG_FILES:
        log_pattern = LOG_FILES[log_type]
        log_files = sorted(LOG_DIR.glob(log_pattern))
        if not log_files:
            print(f"No log files found for type: {log_type}")
            return
        log_file = log_files[-1]  # 最新的文件
    else:
        print(f"Unknown log type: {log_type}")
        return
    
    print(colorize(f"Tailing {log_file.name}...", COLORS['CYAN']))
    print(colorize("-" * 80, COLORS['GRAY']))
    
    if follow:
        # 使用系统的tail命令
        try:
            subprocess.run(['tail', '-f', str(log_file)])
        except KeyboardInterrupt:
            print("\nStopped tailing.")
    else:
        # 只显示最后20行
        lines = read_log_file(log_file, lines=20)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            entry = parse_json_log(line) or parse_text_log(line)
            if entry:
                print(format_log_entry(entry))
            else:
                print(line)


def show_stats(log_type: str = 'main', hours: int = 24):
    """显示日志统计信息"""
    print(colorize(f"Log Statistics (last {hours} hours)", COLORS['BOLD']))
    print(colorize("=" * 80, COLORS['GRAY']))
    
    # 获取日志文件
    if log_type in LOG_FILES:
        log_pattern = LOG_FILES[log_type]
        log_files = sorted(LOG_DIR.glob(log_pattern))
    else:
        log_files = LOG_DIR.glob('*.log')
    
    # 统计数据
    level_counts = {}
    logger_counts = {}
    error_types = {}
    total_lines = 0
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for log_file in log_files:
        # 检查文件修改时间
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_time:
            continue
        
        lines = read_log_file(log_file)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            total_lines += 1
            entry = parse_json_log(line) or parse_text_log(line)
            
            if entry:
                # 统计级别
                level = entry.get('level', 'UNKNOWN')
                level_counts[level] = level_counts.get(level, 0) + 1
                
                # 统计模块
                logger = entry.get('logger', 'unknown')
                logger_counts[logger] = logger_counts.get(logger, 0) + 1
                
                # 统计错误类型
                if level in ['ERROR', 'CRITICAL'] and 'exception' in entry:
                    error_type = entry['exception'].get('type', 'Unknown')
                    error_types[error_type] = error_types.get(error_type, 0) + 1
    
    # 显示统计结果
    print(f"\n{colorize('Total Log Lines:', COLORS['CYAN'])} {total_lines}")
    
    print(f"\n{colorize('Log Levels:', COLORS['CYAN'])}")
    for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True):
        level_color = LEVEL_COLORS.get(level, COLORS['WHITE'])
        bar = '█' * min(50, int(count * 50 / max(level_counts.values())))
        print(f"  {colorize(f'{level:8}', level_color)} {count:6} {colorize(bar, level_color)}")
    
    print(f"\n{colorize('Top Loggers:', COLORS['CYAN'])}")
    for logger, count in sorted(logger_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {logger:40} {count:6}")
    
    if error_types:
        print(f"\n{colorize('Error Types:', COLORS['RED'])}")
        for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {error_type:30} {count:6}")


def clean_old_logs(days: int = 7):
    """清理旧日志文件"""
    print(colorize(f"Cleaning logs older than {days} days...", COLORS['YELLOW']))
    
    cutoff_time = time.time() - (days * 86400)
    deleted_count = 0
    deleted_size = 0
    
    for log_file in LOG_DIR.glob('*.log*'):
        if log_file.stat().st_mtime < cutoff_time:
            size = log_file.stat().st_size
            print(f"  Deleting: {log_file.name} ({size // 1024} KB)")
            log_file.unlink()
            deleted_count += 1
            deleted_size += size
    
    print(colorize(f"Deleted {deleted_count} files, freed {deleted_size // (1024*1024)} MB", COLORS['GREEN']))


def list_logs():
    """列出所有日志文件"""
    print(colorize("Available Log Files:", COLORS['BOLD']))
    print(colorize("=" * 80, COLORS['GRAY']))
    
    total_size = 0
    
    for log_type, pattern in LOG_FILES.items():
        log_files = sorted(LOG_DIR.glob(pattern))
        
        if log_files:
            print(f"\n{colorize(log_type.upper(), COLORS['CYAN'])}")
            for log_file in log_files:
                size = log_file.stat().st_size
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                total_size += size
                
                size_str = f"{size // 1024} KB" if size < 1024*1024 else f"{size // (1024*1024)} MB"
                print(f"  {log_file.name:40} {size_str:10} {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n{colorize('Total Size:', COLORS['CYAN'])} {total_size // (1024*1024)} MB")
    print(f"{colorize('Log Directory:', COLORS['CYAN'])} {LOG_DIR}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Baal Desktop Pet 日志查看工具')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # tail命令
    tail_parser = subparsers.add_parser('tail', help='查看日志尾部')
    tail_parser.add_argument('type', nargs='?', default='main', 
                            choices=list(LOG_FILES.keys()),
                            help='日志类型 (默认: main)')
    tail_parser.add_argument('-f', '--follow', action='store_true',
                            help='实时跟踪日志')
    
    # search命令
    search_parser = subparsers.add_parser('search', help='搜索日志')
    search_parser.add_argument('pattern', help='搜索模式（正则表达式）')
    search_parser.add_argument('-t', '--type', default='main',
                              choices=list(LOG_FILES.keys()),
                              help='日志类型 (默认: main)')
    search_parser.add_argument('-n', '--lines', type=int, default=1000,
                              help='搜索最近n行 (默认: 1000)')
    search_parser.add_argument('-v', '--verbose', action='store_true',
                              help='显示详细信息')
    
    # stats命令
    stats_parser = subparsers.add_parser('stats', help='显示日志统计')
    stats_parser.add_argument('-t', '--type', default='main',
                             choices=list(LOG_FILES.keys()) + ['all'],
                             help='日志类型 (默认: main)')
    stats_parser.add_argument('-H', '--hours', type=int, default=24,
                             help='统计最近n小时 (默认: 24)')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出所有日志文件')
    
    # clean命令
    clean_parser = subparsers.add_parser('clean', help='清理旧日志')
    clean_parser.add_argument('-d', '--days', type=int, default=7,
                             help='清理n天前的日志 (默认: 7)')
    
    # errors命令（快捷方式）
    errors_parser = subparsers.add_parser('errors', help='查看错误日志')
    errors_parser.add_argument('-n', '--lines', type=int, default=50,
                              help='显示最近n个错误 (默认: 50)')
    errors_parser.add_argument('-v', '--verbose', action='store_true',
                              help='显示详细错误信息')
    
    # performance命令（快捷方式）
    perf_parser = subparsers.add_parser('perf', help='查看性能日志')
    perf_parser.add_argument('-n', '--lines', type=int, default=50,
                            help='显示最近n条性能记录 (默认: 50)')
    
    args = parser.parse_args()
    
    # 确保日志目录存在
    if not LOG_DIR.exists():
        print(colorize(f"Log directory does not exist: {LOG_DIR}", COLORS['RED']))
        return 1
    
    # 执行命令
    if args.command == 'tail':
        tail_log(args.type, args.follow)
    
    elif args.command == 'search':
        results = search_logs(args.pattern, args.type, args.lines)
        
        if results:
            print(colorize(f"Found {len(results)} matches:", COLORS['GREEN']))
            print(colorize("-" * 80, COLORS['GRAY']))
            
            for entry in results:
                print(format_log_entry(entry, args.verbose))
                if args.verbose:
                    print(colorize("-" * 40, COLORS['GRAY']))
        else:
            print(colorize("No matches found.", COLORS['YELLOW']))
    
    elif args.command == 'stats':
        show_stats(args.type, args.hours)
    
    elif args.command == 'list':
        list_logs()
    
    elif args.command == 'clean':
        clean_old_logs(args.days)
    
    elif args.command == 'errors':
        # 快捷方式：查看错误日志
        results = search_logs('ERROR|CRITICAL', 'error', args.lines)
        
        if results:
            print(colorize(f"Recent Errors ({len(results)} found):", COLORS['RED']))
            print(colorize("-" * 80, COLORS['GRAY']))
            
            for entry in results:
                print(format_log_entry(entry, args.verbose))
                if args.verbose:
                    print(colorize("-" * 40, COLORS['GRAY']))
        else:
            print(colorize("No errors found.", COLORS['GREEN']))
    
    elif args.command == 'perf':
        # 快捷方式：查看性能日志
        tail_log('performance', False)
    
    else:
        # 默认：显示帮助
        parser.print_help()
        print(f"\n{colorize('Examples:', COLORS['CYAN'])}")
        print("  python view_logs.py tail main -f         # 实时查看主日志")
        print("  python view_logs.py search 'ERROR'        # 搜索错误")
        print("  python view_logs.py errors -v             # 查看详细错误信息")
        print("  python view_logs.py stats -H 1            # 查看最近1小时统计")
        print("  python view_logs.py clean -d 3            # 清理3天前的日志")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())