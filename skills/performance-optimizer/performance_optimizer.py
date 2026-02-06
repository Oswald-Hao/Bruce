#!/usr/bin/env python3
"""
性能优化工具 - 核心实现
提供代码性能分析、瓶颈定位、优化建议和资源监控
"""

import time
import psutil
import json
import subprocess
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FunctionProfile:
    """函数性能分析结果"""
    name: str
    file: str
    line: int
    time: float
    calls: int
    avg_time: float
    memory_peak: float


@dataclass
class Bottleneck:
    """性能瓶颈"""
    type: str
    location: str
    time: float
    suggestion: str


@dataclass
class AnalysisResult:
    """分析结果"""
    script: str
    total_time: float
    functions: List[FunctionProfile]
    bottlenecks: List[Bottleneck]
    optimization_suggestions: List[str]
    timestamp: str


@dataclass
class MonitorData:
    """监控数据"""
    cpu_usage: List[float]
    memory_usage: List[float]
    disk_io: List[Dict]
    network_io: List[Dict]
    duration: float
    interval: float


class PerformanceOptimizer:
    """性能优化工具"""

    def __init__(self):
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)

    def analyze_script(self, script_path: str) -> AnalysisResult:
        """
        分析Python脚本性能

        Args:
            script_path: 脚本路径

        Returns:
            AnalysisResult: 分析结果
        """
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")

        # 1. 使用cProfile分析执行时间
        profile_file = self._run_cprofile(script_path)

        # 2. 解析profile结果
        functions = self._parse_profile(profile_file)

        # 3. 使用memory_profiler分析内存使用
        memory_data = self._run_memory_profiler(script_path)

        # 4. 识别瓶颈
        bottlenecks = self._identify_bottlenecks(functions, memory_data)

        # 5. 生成优化建议
        suggestions = self._generate_optimization_suggestions(
            functions, bottlenecks
        )

        # 6. 计算总时间
        total_time = sum(f.time for f in functions) if functions else 0

        result = AnalysisResult(
            script=script_path,
            total_time=total_time,
            functions=functions,
            bottlenecks=bottlenecks,
            optimization_suggestions=suggestions,
            timestamp=datetime.now().isoformat()
        )

        # 清理临时文件
        self._cleanup_temp_files()

        return result

    def _run_cprofile(self, script_path: str) -> str:
        """运行cProfile分析"""
        profile_file = os.path.join(self.temp_dir, "profile.stats")
        # 先尝试python3，再尝试python
        for py_cmd in ["python3", "python"]:
            cmd = [
                py_cmd, "-m", "cProfile", "-o", profile_file, script_path
            ]

            try:
                subprocess.run(cmd, capture_output=True, timeout=300, check=True)
                break
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"Warning: cProfile with {py_cmd} failed: {e}")
                if py_cmd == "python":  # 最后一个尝试也失败
                    pass
                continue

        return profile_file

    def _parse_profile(self, profile_file: str) -> List[FunctionProfile]:
        """解析profile结果"""
        functions = []

        if not os.path.exists(profile_file):
            return functions

        try:
            import pstats
            stats = pstats.Stats(profile_file)
            stats.sort_stats('cumulative')

            # 使用stats.get_stats_profile()获取函数信息
            try:
                profile_data = stats.get_stats_profile()
                if hasattr(profile_data, 'func_profiles'):
                    func_profiles = profile_data.func_profiles
                else:
                    # 降级：直接使用stats.stats
                    func_profiles = stats.stats

                # 获取前20个函数
                count = 0
                for func_info in func_profiles:
                    if count >= 20:
                        break

                    try:
                        if isinstance(func_info, tuple):
                            # pstats格式: (file, line, name), (ncalls, ncalls, tottime, cumtime, callers)
                            file_path = func_info[0]
                            line_num = func_info[1]
                            func_name = func_info[2]

                            # 获取统计数据
                            stats_info = func_profiles[func_info]
                            call_count = stats_info[0] if isinstance(stats_info[0], int) else stats_info[0].calls
                            tot_time = stats_info[2]
                            cum_time = stats_info[3]
                        else:
                            # 新版本pstats的格式
                            if hasattr(func_info, 'name'):
                                func_name = func_info.name
                                file_path = str(func_info.file) if hasattr(func_info, 'file') else "unknown"
                                line_num = func_info.line if hasattr(func_info, 'line') else 0
                                call_count = func_info.ncalls if hasattr(func_info, 'ncalls') else 0
                                cum_time = func_info.cumtime if hasattr(func_info, 'cumtime') else 0
                            else:
                                continue

                        functions.append(FunctionProfile(
                            name=func_name,
                            file=file_path,
                            line=line_num,
                            time=cum_time,
                            calls=call_count,
                            avg_time=cum_time / call_count if call_count > 0 else 0,
                            memory_peak=0
                        ))

                        count += 1

                    except (IndexError, KeyError, AttributeError) as e:
                        continue

            except Exception as e:
                print(f"Warning: Failed to get profile data: {e}")

        except Exception as e:
            print(f"Warning: Failed to parse profile: {e}")

        return functions

    def _run_memory_profiler(self, script_path: str) -> Dict:
        """运行memory_profiler分析内存使用"""
        try:
            from memory_profiler import memory_usage

            # 记录内存使用
            mem_usage = memory_usage((exec, (open(script_path).read(), {})),
                                     interval=0.1, timeout=300)

            max_memory = max(mem_usage) if mem_usage else 0

            return {
                "max_memory_mb": max_memory,
                "min_memory_mb": min(mem_usage) if mem_usage else 0,
                "avg_memory_mb": sum(mem_usage) / len(mem_usage) if mem_usage else 0,
                "samples": mem_usage
            }
        except ImportError:
            print("Warning: memory_profiler not installed, skipping memory analysis")
            # 返回默认值以便测试继续
            return {
                "max_memory_mb": 0,
                "min_memory_mb": 0,
                "avg_memory_mb": 0,
                "samples": []
            }
        except Exception as e:
            print(f"Warning: Memory profiler failed: {e}")
            return {
                "max_memory_mb": 0,
                "min_memory_mb": 0,
                "avg_memory_mb": 0,
                "samples": []
            }

    def _identify_bottlenecks(
        self,
        functions: List[FunctionProfile],
        memory_data: Dict
    ) -> List[Bottleneck]:
        """识别性能瓶颈"""
        bottlenecks = []

        if not functions:
            return bottlenecks

        # 找出最慢的函数（占总时间>10%）
        total_time = sum(f.time for f in functions)
        slow_threshold = total_time * 0.1

        for func in functions:
            if func.time > slow_threshold:
                bottlenecks.append(Bottleneck(
                    type="slow_function",
                    location=f"{func.file}:{func.line}",
                    time=func.time,
                    suggestion=(
                        f"函数'{func.name}'执行时间过长({func.time:.2f}s)。"
                        "建议：1) 检查算法复杂度 2) 使用缓存 3) 异步处理"
                    )
                ))

        # 检查内存问题
        if memory_data:
            max_memory = memory_data.get("max_memory_mb", 0)
            if max_memory > 500:  # 超过500MB
                bottlenecks.append(Bottleneck(
                    type="high_memory",
                    location="script",
                    time=max_memory,
                    suggestion=(
                        f"内存使用过高({max_memory:.2f}MB)。"
                        "建议：1) 检查内存泄漏 2) 使用生成器 3) 优化数据结构"
                    )
                ))

        # 检查函数调用次数
        for func in functions:
            if func.calls > 10000:
                bottlenecks.append(Bottleneck(
                    type="excessive_calls",
                    location=f"{func.file}:{func.line}",
                    time=func.time * func.calls,
                    suggestion=(
                        f"函数'{func.name}'调用次数过多({func.calls})。"
                        "建议：1) 批量处理 2) 缓存结果 3) 检查循环逻辑"
                    )
                ))

        return bottlenecks[:10]  # 限制返回数量

    def _generate_optimization_suggestions(
        self,
        functions: List[FunctionProfile],
        bottlenecks: List[Bottleneck]
    ) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if bottlenecks:
            for bottleneck in bottlenecks:
                suggestions.append(f"⚠️ {bottleneck.suggestion}")

        # 通用建议
        if functions:
            suggestions.extend([
                "💡 使用内置函数和库（如itertools, collections）替代手动实现",
                "💡 考虑使用@lru_cache装饰器缓存函数结果",
                "💡 对大列表使用生成器表达式替代列表推导式",
                "💡 使用set/dict进行O(1)查找，避免在列表中线性搜索",
                "💡 对于I/O密集型操作，考虑使用asyncio或多线程"
            ])

        return suggestions[:20]  # 限制返回数量

    def start_monitor(
        self,
        duration: float = 60,
        interval: float = 1
    ) -> MonitorData:
        """
        启动资源监控

        Args:
            duration: 监控时长（秒）
            interval: 采样间隔（秒）

        Returns:
            MonitorData: 监控数据
        """
        cpu_usage = []
        memory_usage = []
        disk_io = []
        network_io = []

        start_time = time.time()

        while time.time() - start_time < duration:
            # CPU使用率
            cpu = psutil.cpu_percent(interval=interval)
            cpu_usage.append(cpu)

            # 内存使用
            memory = psutil.virtual_memory()
            memory_usage.append(memory.used / (1024 ** 3))  # GB

            # 磁盘I/O
            disk = psutil.disk_io_counters()
            if disk:
                disk_io.append({
                    "read_mb": disk.read_bytes / (1024 ** 2),
                    "write_mb": disk.write_bytes / (1024 ** 2)
                })

            # 网络I/O
            network = psutil.net_io_counters()
            if network:
                network_io.append({
                    "sent_mb": network.bytes_sent / (1024 ** 2),
                    "recv_mb": network.bytes_recv / (1024 ** 2)
                })

        return MonitorData(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_io=disk_io,
            network_io=network_io,
            duration=duration,
            interval=interval
        )

    def generate_html_report(
        self,
        result: AnalysisResult,
        output_path: str
    ) -> str:
        """生成HTML性能报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>性能分析报告 - {result.script}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #4CAF50; color: white; padding: 20px; }}
        .section {{ margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .bottleneck {{ background: #ffdddd; border-left: 4px solid #f44336; }}
        .suggestion {{ background: #ffffdd; border-left: 4px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>性能分析报告</h1>
        <p>脚本: {result.script}</p>
        <p>总执行时间: {result.total_time:.2f}s</p>
        <p>分析时间: {result.timestamp}</p>
    </div>

    <div class="section">
        <h2>函数性能</h2>
        <table>
            <tr>
                <th>函数名</th>
                <th>文件</th>
                <th>行号</th>
                <th>总时间(s)</th>
                <th>调用次数</th>
                <th>平均时间(s)</th>
            </tr>
"""

        for func in result.functions[:20]:
            html += f"""
            <tr>
                <td>{func.name}</td>
                <td>{func.file}</td>
                <td>{func.line}</td>
                <td>{func.time:.4f}</td>
                <td>{func.calls}</td>
                <td>{func.avg_time:.6f}</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="section">
        <h2>性能瓶颈</h2>
"""

        if result.bottlenecks:
            for bottleneck in result.bottlenecks:
                html += f"""
        <div class="bottleneck">
            <p><strong>类型:</strong> {bottleneck.type}</p>
            <p><strong>位置:</strong> {bottleneck.location}</p>
            <p><strong>影响:</strong> {bottleneck.time:.2f}</p>
            <p><strong>建议:</strong> {bottleneck.suggestion}</p>
        </div>
"""
        else:
            html += "<p>未发现明显的性能瓶颈</p>"

        html += """
    </div>

    <div class="section">
        <h2>优化建议</h2>
"""

        for suggestion in result.optimization_suggestions:
            html += f"""
        <div class="suggestion">
            <p>{suggestion}</p>
        </div>
"""

        html += """
    </div>
</body>
</html>
"""

        # 写入文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path

    def generate_markdown_report(
        self,
        result: AnalysisResult,
        output_path: str
    ) -> str:
        """生成Markdown性能报告"""
        md = f"""# 性能分析报告

**脚本:** {result.script}
**总执行时间:** {result.total_time:.2f}s
**分析时间:** {result.timestamp}

## 函数性能

| 函数名 | 文件 | 行号 | 总时间(s) | 调用次数 | 平均时间(s) |
|--------|------|------|-----------|----------|-------------|
"""

        for func in result.functions[:20]:
            md += f"| {func.name} | {func.file} | {func.line} | {func.time:.4f} | {func.calls} | {func.avg_time:.6f} |\n"

        md += "\n## 性能瓶颈\n\n"

        if result.bottlenecks:
            for i, bottleneck in enumerate(result.bottlenecks, 1):
                md += f"""### {i}. {bottleneck.type}

- **位置:** {bottleneck.location}
- **影响:** {bottleneck.time:.2f}
- **建议:** {bottleneck.suggestion}

"""
        else:
            md += "✅ 未发现明显的性能瓶颈\n"

        md += "\n## 优化建议\n\n"

        for suggestion in result.optimization_suggestions:
            md += f"- {suggestion}\n"

        # 写入文件
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        return output_path

    def batch_analyze(self, scripts: List[str]) -> List[AnalysisResult]:
        """批量分析多个脚本"""
        results = []
        for script in scripts:
            try:
                result = self.analyze_script(script)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {script}: {e}")
        return results

    def _cleanup_temp_files(self):
        """清理临时文件"""
        import shutil
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
            except Exception as e:
                print(f"Warning: Failed to cleanup temp files: {e}")


# 装饰器：函数性能分析
def profile_function(func):
    """函数性能分析装饰器"""
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"[PROFILE] {func.__name__} executed in {elapsed:.4f}s")

        return result

    return wrapper
