#!/usr/bin/env python3
"""
调试profile解析 - 不清理临时文件
"""

import os
import pstats
from performance_optimizer import PerformanceOptimizer

optimizer = PerformanceOptimizer()

# 创建测试脚本
script_content = """
import time

def fast_function():
    return 1 + 1

def slow_function():
    time.sleep(0.1)
    return sum(range(1000))

if __name__ == "__main__":
    fast_function()
    slow_function()
"""

script_dir = os.path.join(os.path.dirname(__file__), "test_scripts")
os.makedirs(script_dir, exist_ok=True)
script_path = os.path.join(script_dir, "debug_test.py")

with open(script_path, 'w') as f:
    f.write(script_content)

print(f"脚本路径: {script_path}")
print(f"临时目录: {optimizer.temp_dir}")

# 运行cProfile
profile_file = optimizer._run_cprofile(script_path)
print(f"Profile文件: {profile_file}")
print(f"文件存在: {os.path.exists(profile_file)}")
print(f"文件大小: {os.path.getsize(profile_file)} bytes")

# 打印profile内容
print("\nProfile内容:")
stats = pstats.Stats(profile_file)
stats.sort_stats('cumulative')
stats.print_stats(20)

# 解析profile
functions = optimizer._parse_profile(profile_file)
print(f"\n识别到函数数量: {len(functions)}")
for func in functions[:5]:
    print(f"  - {func.name}: {func.time:.4f}s")
