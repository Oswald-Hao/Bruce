#!/usr/bin/env python3
"""
Resource Monitor 测试脚本
测试所有核心功能
"""

import subprocess
import json
import time
import os
import sys


def run_command(cmd: str) -> tuple[int, str, str]:
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def test_1_basic_monitor():
    """测试1：基础监控功能"""
    print("\n[测试1] 基础监控功能")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        print(f"错误: {stderr}")
        return False

    # 检查输出包含关键信息
    required_keywords = ["CPU", "内存", "磁盘", "网络"]
    for keyword in required_keywords:
        if keyword not in stdout:
            print(f"❌ 失败: 输出中缺少 '{keyword}'")
            return False

    print("✅ 通过: 基础监控功能正常")
    print(stdout[:200] + "..." if len(stdout) > 200 else stdout)
    return True


def test_2_cpu_monitor():
    """测试2：CPU监控详细信息"""
    print("\n[测试2] CPU监控详细信息")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py --format json")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        return False

    try:
        data = json.loads(stdout)
        cpu = data.get("cpu", {})

        # 检查CPU字段
        required_fields = ["percent", "count_physical", "count_logical"]
        for field in required_fields:
            if field not in cpu:
                print(f"❌ 失败: CPU数据中缺少字段 '{field}'")
                return False

        print(f"✅ 通过: CPU使用率 {cpu['percent']:.1f}%, 核心数 {cpu['count_physical']}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ 失败: JSON解析错误 - {e}")
        return False


def test_3_memory_monitor():
    """测试3：内存监控详细信息"""
    print("\n[测试3] 内存监控详细信息")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py --format json")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        return False

    try:
        data = json.loads(stdout)
        memory = data.get("memory", {})

        # 检查内存字段
        required_fields = ["total", "used", "available", "percent"]
        for field in required_fields:
            if field not in memory:
                print(f"❌ 失败: 内存数据中缺少字段 '{field}'")
                return False

        total_gb = memory["total"] / (1024**3)
        used_gb = memory["used"] / (1024**3)
        print(f"✅ 通过: 内存使用率 {memory['percent']:.1f}% ({used_gb:.2f}GB / {total_gb:.2f}GB)")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ 失败: JSON解析错误 - {e}")
        return False


def test_4_disk_monitor():
    """测试4：磁盘监控详细信息"""
    print("\n[测试4] 磁盘监控详细信息")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py --format json")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        return False

    try:
        data = json.loads(stdout)
        disk = data.get("disk", {})

        # 检查磁盘字段
        if "partitions" not in disk or not disk["partitions"]:
            print(f"❌ 失败: 磁盘分区数据为空")
            return False

        if "io" not in disk:
            print(f"❌ 失败: 磁盘IO数据缺失")
            return False

        partitions = disk["partitions"]
        print(f"✅ 通过: 检测到 {len(partitions)} 个磁盘分区")
        for p in partitions[:3]:  # 显示前3个
            mount = p.get("mountpoint", "")
            percent = p.get("percent", 0)
            print(f"    {mount}: {percent:.0f}%")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ 失败: JSON解析错误 - {e}")
        return False


def test_5_network_monitor():
    """测试5：网络监控详细信息"""
    print("\n[测试5] 网络监控详细信息")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py --format json")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        return False

    try:
        data = json.loads(stdout)
        network = data.get("network", {})

        # 检查网络字段
        required_fields = ["bytes_sent", "bytes_recv", "upload_speed", "download_speed"]
        for field in required_fields:
            if field not in network:
                print(f"❌ 失败: 网络数据中缺少字段 '{field}'")
                return False

        print(f"✅ 通过: 上传速度 {network['upload_speed']:.0f} B/s, 下载速度 {network['download_speed']:.0f} B/s")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ 失败: JSON解析错误 - {e}")
        return False


def test_6_threshold_check():
    """测试6：阈值检查功能"""
    print("\n[测试6] 阈值检查功能")
    print("-" * 50)

    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py check --type cpu --threshold 99")

    if code != 0:
        print(f"❌ 失败: 退出码 {code}")
        return False

    # 检查输出
    if "cpu" not in stdout.lower():
        print(f"❌ 失败: 输出中未包含CPU检查结果")
        return False

    if "正常" not in stdout and "超限" not in stdout:
        print(f"❌ 失败: 输出中未包含检查状态")
        return False

    print("✅ 通过: 阈值检查功能正常")
    print(stdout)
    return True


def test_7_output_formats():
    """测试7：多种输出格式"""
    print("\n[测试7] 多种输出格式")
    print("-" * 50)

    formats = ["text", "json", "csv"]
    for fmt in formats:
        code, stdout, stderr = run_command(f"cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py --format {fmt}")

        if code != 0:
            print(f"❌ 失败: 格式 '{fmt}' 退出码 {code}")
            return False

        if not stdout:
            print(f"❌ 失败: 格式 '{fmt}' 输出为空")
            return False

        print(f"  ✅ {fmt} 格式正常")

    print("✅ 通过: 所有输出格式正常")
    return True


def test_8_history_save_and_load():
    """测试8：历史数据保存和加载"""
    print("\n[测试8] 历史数据保存和加载")
    print("-" * 50)

    # 保存历史数据（通过monitor子命令，立即退出）
    history_path = os.path.expanduser("~/.monitor_history.json")
    if os.path.exists(history_path):
        os.remove(history_path)

    # 使用一次监控并保存（不使用monitor子命令，因为它会持续运行）
    # 我们直接调用Python代码来保存
    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 -c \"from monitor import ResourceMonitor; m = ResourceMonitor(); m.save_history(m.get_all_resources())\"")

    if code != 0:
        print(f"❌ 失败: 保存历史数据退出码 {code}")
        print(f"错误: {stderr}")
        return False

    # 检查文件是否创建
    if not os.path.exists(history_path):
        print(f"❌ 失败: 历史数据文件未创建")
        return False

    # 加载历史数据
    code, stdout, stderr = run_command("cd /home/lejurobot/clawd/skills/resource-monitor && python3 monitor.py history --hours 1")

    if code != 0:
        print(f"❌ 失败: 加载历史数据退出码 {code}")
        return False

    if "历史数据" not in stdout:
        print(f"❌ 失败: 历史数据输出异常")
        return False

    print("✅ 通过: 历史数据保存和加载正常")
    print(stdout[:150] + "..." if len(stdout) > 150 else stdout)
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Resource Monitor 测试开始")
    print("=" * 60)

    tests = [
        ("基础监控功能", test_1_basic_monitor),
        ("CPU监控", test_2_cpu_monitor),
        ("内存监控", test_3_memory_monitor),
        ("磁盘监控", test_4_disk_monitor),
        ("网络监控", test_5_network_monitor),
        ("阈值检查", test_6_threshold_check),
        ("输出格式", test_7_output_formats),
        ("历史数据", test_8_history_save_and_load),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 异常: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)

    if failed == 0:
        print("🎉 所有测试通过!")
        return True
    else:
        print(f"⚠️  有 {failed} 个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
