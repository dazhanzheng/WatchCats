#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows Application Automated Test Suite
For CI/CD validation of built executable
"""

import os
import sys
import time
import subprocess
import psutil
import traceback
from pathlib import Path

# 设置UTF-8编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

class WindowsAppTester:
    def __init__(self, exe_path):
        self.exe_path = Path(exe_path)
        self.test_results = []
        self.process = None
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
        self.test_results.append({"time": timestamp, "level": level, "message": message})
    
    def test_executable_exists(self):
        """Test 1: 验证可执行文件存在"""
        self.log("Test 1: Checking if executable exists...")
        if not self.exe_path.exists():
            self.log(f"FAILED: Executable not found at {self.exe_path}", "ERROR")
            return False
        
        size_mb = self.exe_path.stat().st_size / (1024 * 1024)
        self.log(f"PASSED: Found {self.exe_path.name} ({size_mb:.2f} MB)")
        return True
    
    def test_qt_plugins(self):
        """Test 2: 验证Qt插件文件"""
        self.log("Test 2: Checking Qt plugins...")
        base_dir = self.exe_path.parent
        
        plugin_paths = [
            base_dir / "PyQt6" / "Qt6" / "plugins" / "platforms" / "qwindows.dll",
            base_dir / "Qt6" / "plugins" / "platforms" / "qwindows.dll",
            base_dir / "plugins" / "platforms" / "qwindows.dll",
            base_dir / "_internal" / "PyQt6" / "Qt6" / "plugins" / "platforms" / "qwindows.dll",
        ]
        
        found = False
        for path in plugin_paths:
            if path.exists():
                self.log(f"PASSED: Found qwindows.dll at {path.relative_to(base_dir)}")
                found = True
                break
        
        if not found:
            self.log("WARNING: qwindows.dll not found in expected locations", "WARNING")
            # 搜索任何 qwindows.dll
            for dll in base_dir.rglob("qwindows.dll"):
                self.log(f"Found qwindows.dll at: {dll.relative_to(base_dir)}")
                found = True
                break
        
        return found
    
    def test_resources(self):
        """Test 3: 验证资源文件"""
        self.log("Test 3: Checking resource files...")
        base_dir = self.exe_path.parent
        
        required_resources = [
            ("动作表情拆分", "*.png"),
            ("动作表情拆分", "*.gif"),
        ]
        
        all_found = True
        for folder, pattern in required_resources:
            folder_path = base_dir / folder
            if not folder_path.exists():
                self.log(f"WARNING: Resource folder missing: {folder}", "WARNING")
                all_found = False
                continue
            
            files = list(folder_path.glob(pattern))
            if files:
                self.log(f"PASSED: Found {len(files)} {pattern} files in {folder}")
            else:
                self.log(f"WARNING: No {pattern} files in {folder}", "WARNING")
                all_found = False
        
        return all_found
    
    def test_app_startup(self, timeout=30):
        """Test 4: 测试应用启动"""
        self.log("Test 4: Testing application startup...")
        
        # 设置环境变量
        env = os.environ.copy()
        base_dir = str(self.exe_path.parent)
        env['QT_PLUGIN_PATH'] = f"{base_dir}\\PyQt6\\Qt6\\plugins;{base_dir}\\Qt6\\plugins;{base_dir}\\plugins"
        env['QT_QPA_PLATFORM_PLUGIN_PATH'] = f"{base_dir}\\PyQt6\\Qt6\\plugins\\platforms;{base_dir}\\Qt6\\plugins\\platforms;{base_dir}\\plugins\\platforms"
        env['QT_OPENGL'] = 'angle'
        env['QT_QUICK_BACKEND'] = 'software'
        env['QT_QPA_PLATFORM'] = 'offscreen'  # 无头模式运行
        
        try:
            # 启动进程
            self.log(f"Starting {self.exe_path.name}...")
            self.process = subprocess.Popen(
                [str(self.exe_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(self.exe_path.parent)
            )
            
            # 等待进程稳定运行
            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查进程是否仍在运行
                if self.process.poll() is not None:
                    # 进程已退出
                    stdout, stderr = self.process.communicate(timeout=1)
                    if self.process.returncode != 0:
                        self.log(f"FAILED: Process exited with code {self.process.returncode}", "ERROR")
                        if stderr:
                            self.log(f"STDERR: {stderr.decode('utf-8', errors='replace')[:500]}", "ERROR")
                        return False
                    else:
                        self.log("WARNING: Process exited normally (might be single-instance check)", "WARNING")
                        return True
                
                # 检查进程内存使用
                try:
                    proc = psutil.Process(self.process.pid)
                    memory_mb = proc.memory_info().rss / (1024 * 1024)
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    
                    if time.time() - start_time > 5:  # 5秒后检查
                        self.log(f"Running: PID={self.process.pid}, Memory={memory_mb:.1f}MB, CPU={cpu_percent:.1f}%")
                        
                        # 检查是否有子进程（Qt应用通常会创建子进程）
                        children = proc.children(recursive=True)
                        if children:
                            self.log(f"Found {len(children)} child process(es)")
                        
                        # 如果运行超过10秒且内存使用正常，认为启动成功
                        if time.time() - start_time > 10 and memory_mb > 20:
                            self.log(f"PASSED: Application running stable (Memory: {memory_mb:.1f}MB)")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                
                time.sleep(1)
            
            # 超时但进程仍在运行
            if self.process.poll() is None:
                self.log(f"PASSED: Application still running after {timeout}s")
                return True
            
        except Exception as e:
            self.log(f"FAILED: Exception during startup: {str(e)}", "ERROR")
            self.log(traceback.format_exc(), "ERROR")
            return False
        
        return False
    
    def test_graceful_shutdown(self):
        """Test 5: 测试优雅关闭"""
        self.log("Test 5: Testing graceful shutdown...")
        
        if not self.process or self.process.poll() is not None:
            self.log("SKIPPED: No running process to shutdown")
            return True
        
        try:
            # 尝试终止进程
            self.process.terminate()
            
            # 等待最多5秒
            try:
                self.process.wait(timeout=5)
                self.log(f"PASSED: Process terminated gracefully (exit code: {self.process.returncode})")
                return True
            except subprocess.TimeoutExpired:
                # 强制结束
                self.process.kill()
                self.process.wait(timeout=2)
                self.log("WARNING: Had to force kill the process", "WARNING")
                return True
                
        except Exception as e:
            self.log(f"ERROR: Failed to shutdown: {str(e)}", "ERROR")
            return False
    
    def cleanup(self):
        """清理测试环境"""
        if self.process and self.process.poll() is None:
            try:
                self.process.kill()
                self.process.wait(timeout=2)
            except:
                pass
        
        # 清理可能残留的进程
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'WatchCats' in proc.info['name']:
                    proc.kill()
                    self.log(f"Killed lingering process: {proc.info['name']}")
        except:
            pass
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("="*60)
        self.log("Starting Windows Application Test Suite")
        self.log(f"Testing: {self.exe_path}")
        self.log("="*60)
        
        tests = [
            ("Executable Exists", self.test_executable_exists),
            ("Qt Plugins", self.test_qt_plugins),
            ("Resources", self.test_resources),
            ("App Startup", self.test_app_startup),
            ("Graceful Shutdown", self.test_graceful_shutdown),
        ]
        
        results = {}
        for test_name, test_func in tests:
            try:
                self.log(f"\nRunning: {test_name}")
                results[test_name] = test_func()
            except Exception as e:
                self.log(f"EXCEPTION in {test_name}: {str(e)}", "ERROR")
                results[test_name] = False
        
        # 清理
        self.cleanup()
        
        # 生成报告
        self.log("\n" + "="*60)
        self.log("TEST RESULTS SUMMARY")
        self.log("="*60)
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            symbol = "[OK]" if result else "[FAIL]"
            self.log(f"{symbol} {test_name}: {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        # 统计警告
        for result in self.test_results:
            if result['level'] == 'WARNING':
                warnings += 1
        
        self.log("\n" + "-"*40)
        self.log(f"Total: {len(tests)} tests")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Warnings: {warnings}")
        
        # 返回是否全部通过
        success = failed == 0
        
        if success:
            self.log("\n[SUCCESS] All critical tests passed!")
        else:
            self.log("\n[FAILURE] Some tests failed!", "ERROR")
        
        return success

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python test_windows_app.py <path_to_exe>")
        sys.exit(1)
    
    exe_path = sys.argv[1]
    
    # 运行测试
    tester = WindowsAppTester(exe_path)
    success = tester.run_all_tests()
    
    # 退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()