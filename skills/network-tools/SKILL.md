# 网络工具集 - SKILL.md

## 技能描述

提供全面的网络工具，包括端口扫描、网络诊断、流量分析和网络监控能力。

## 核心功能

- 端口扫描（TCP/UDP、服务识别、端口状态）
- 网络诊断（ping、traceroute、DNS查询）
- 流量分析（协议统计、连接分析）
- 网络监控（带宽监控、连接数监控）
- HTTP/HTTPS测试（响应时间、状态码检查）
- WebSocket测试
- 网络拓扑发现
- 网络性能测试（吞吐量、延迟）

## 安装依赖

```bash
pip install scapy requests python-nmap
```

## 使用方法

### 1. 端口扫描

```python
from network_tools import NetworkTools

tools = NetworkTools()

# 扫描单个主机
result = tools.scan_ports("192.168.1.1", ports=[22, 80, 443, 8080])
print(result.open_ports)

# 扫描常用端口
result = tools.scan_common_ports("192.168.1.1")
```

### 2. 网络诊断

```python
# Ping测试
ping_result = tools.ping("google.com", count=4)
print(f"延迟: {ping_result.avg_latency}ms")

# DNS查询
dns_result = tools.dns_lookup("google.com")
print(dns_result.records)

# Traceroute
trace_result = tools.traceroute("google.com", max_hops=30)
print(trace_result.hops)
```

### 3. HTTP/HTTPS测试

```python
# HTTP测试
http_result = tools.http_test("https://api.example.com")
print(f"状态码: {http_result.status_code}")
print(f"响应时间: {http_result.response_time}ms")

# 批量HTTP测试
results = tools.batch_http_test([
    "https://api1.example.com",
    "https://api2.example.com"
])
```

### 4. 网络监控

```python
# 启动网络监控
monitor = tools.start_network_monitor(duration=60, interval=1)
print(f"带宽: {monitor.bandwidth}")
print(f"连接数: {monitor.connections}")
```

### 5. 网络性能测试

```python
# 测试吞吐量
throughput = tools.test_throughput(
    host="example.com",
    port=80,
    duration=10
)

print(f"吞吐量: {throughput} KB/s")
```

## 命令行工具

```bash
# 端口扫描
python skills/network-tools/scan.py --host 192.168.1.1 --ports 22,80,443

# 网络诊断
python skills/network-tools/diagnose.py ping google.com
python skills/network-tools/diagnose.py dns google.com
python skills/network-tools/diagnose.py trace google.com

# HTTP测试
python skills/network-tools/http-test.py https://api.example.com

# 网络监控
python skills/network-tools/monitor.py --duration 60
```

## 输出示例

### 端口扫描结果

```json
{
  "host": "192.168.1.1",
  "scanned_ports": [22, 80, 443, 8080],
  "open_ports": [
    {"port": 22, "service": "ssh", "state": "open"},
    {"port": 80, "service": "http", "state": "open"}
  ],
  "closed_ports": [443, 8080]
}
```

### Ping结果

```json
{
  "host": "google.com",
  "packets_sent": 4,
  "packets_received": 4,
  "packet_loss": 0,
  "min_latency": 12.3,
  "max_latency": 18.7,
  "avg_latency": 15.2,
  "jitter": 2.5
}
```

### HTTP测试结果

```json
{
  "url": "https://api.example.com",
  "status_code": 200,
  "response_time": 45.2,
  "size": 1024,
  "headers": {...},
  "success": true
}
```

## 核心价值

- **网络诊断：** 快速诊断网络问题
- **服务发现：** 发现网络中的服务和设备
- **性能监控：** 监控网络性能和带宽使用
- **安全检查：** 检查开放端口和服务安全
- **自动化：** 自动化网络测试和监控

## 测试

```bash
# 运行所有测试
python skills/network-tools/test.py

# 运行特定测试
python skills/network-tools/test.py --test scan
python skills/network-tools/test.py --test diagnose
python skills/network-tools/test.py --test http
```

## 注意事项

- 端口扫描需要root权限
- 部分网络操作可能需要管理员权限
- 大规模扫描可能被目标主机检测
- 请遵守网络使用规范和法律法规
