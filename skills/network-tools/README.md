# 网络工具集

提供全面的网络工具，包括端口扫描、网络诊断、流量分析和网络监控。

## 功能

- 端口扫描（TCP/UDP、服务识别、端口状态）
- 网络诊断（ping、traceroute、DNS查询）
- 流量分析（协议统计、连接分析）
- 网络监控（带宽监控、连接数监控）
- HTTP/HTTPS测试（响应时间、状态码检查）
- 网络性能测试（吞吐量、延迟）

## 安装依赖

```bash
pip install requests
```

## 快速开始

### 1. 端口扫描

```python
from network_tools import NetworkTools

tools = NetworkTools()

# 扫描常用端口
result = tools.scan_common_ports("192.168.1.1")
print(f"开放端口: {[p.port for p in result.open_ports]}")
```

### 2. Ping测试

```python
result = tools.ping("google.com", count=4)
print(f"平均延迟: {result.avg_latency}ms")
print(f"丢包率: {result.packet_loss}%")
```

### 3. HTTP测试

```python
result = tools.http_test("https://api.example.com")
print(f"状态码: {result.status_code}")
print(f"响应时间: {result.response_time}ms")
```

### 4. 网络监控

```python
monitor = tools.start_network_monitor(duration=60, interval=1)
print(f"下行带宽: {monitor.bandwidth_in} KB/s")
print(f"上行带宽: {monitor.bandwidth_out} KB/s")
```

## 测试

```bash
python test.py
```

## 输出示例

### 端口扫描

```json
{
  "host": "127.0.0.1",
  "open_ports": [
    {"port": 22, "service": "ssh", "state": "open"},
    {"port": 8000, "service": "http-alt", "state": "open"}
  ],
  "scan_duration": 0.52
}
```

### Ping结果

```json
{
  "host": "google.com",
  "packets_received": 4,
  "packet_loss": 0.0,
  "avg_latency": 15.2,
  "jitter": 2.5
}
```

## 技术栈

- Python 3.x
- socket（网络连接）
- requests（HTTP测试）
- subprocess（系统命令）
