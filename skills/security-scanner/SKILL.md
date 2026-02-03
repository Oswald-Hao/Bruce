# 安全扫描技能

提供漏洞检测、安全加固和入侵检测的安全扫描工具。

## 功能

- 端口扫描和开放端口检测
- 服务版本识别
- 常见漏洞检测
- 弱密码检测
- 安全配置检查
- 入侵检测日志分析
- 安全报告生成
- 自动化安全加固建议

## 工具

### port_scanner.py
端口扫描工具，快速发现开放端口和服务。

**用法：**
```bash
python port_scanner.py --target 192.168.1.1 --ports 1-1000
```

**选项：**
- `--target`: 目标IP或域名
- `--ports`: 端口范围（默认1-1024）
- `--timeout`: 超时时间（秒）
- `--threads`: 并发线程数
- `--output`: 输出文件（JSON/TXT）
- `--service-detection`: 启用服务识别

### vuln_scanner.py
常见漏洞扫描器，检测已知安全问题。

**用法：**
```bash
python vuln_scanner.py --target 192.168.1.1
```

**选项：**
- `--target`: 目标IP
- `--scan-type`: 扫描类型（basic/full）
- `--output`: 输出文件
- `--format`: 输出格式（json/html）

### security_auditor.py
安全配置审计工具，检查系统安全设置。

**用法：**
```bash
python security_auditor.py --mode local
```

**选项：**
- `--mode`: 模式（local/remote）
- `--target`: 目标（远程模式）
- `--checks`: 检查类别（all/network/auth/files）

### password_checker.py
弱密码检测工具。

**用法：**
```bash
python password_checker.py --check user@192.168.1.1
```

**选项：**
- `--check`: 检查目标
- `--dictionary`: 字典文件
- `--complexity`: 密码复杂度检查

## 技术规格

- 扫描速度：1000端口/秒（默认）
- 支持的协议：TCP/UDP
- 漏洞数据库：常见CVE
- 输出格式：JSON, TXT, HTML
- 并发扫描：支持多线程

## 安全策略

1. **端口扫描** - 发现潜在攻击面
2. **服务识别** - 了解目标服务
3. **漏洞检测** - 识别已知漏洞
4. **配置审计** - 检查安全配置
5. **入侵检测** - 分析日志异常

## 核心价值

**对系统安全的贡献：**
1. **主动防御：** 提前发现安全隐患
2. **漏洞管理：** 及时修复安全问题
3. **合规性：** 满足安全审计要求
4. **自动化：** 自动化安全检查

**应用场景：**
- 定期安全审计
- 渗透测试辅助
- 入侵检测
- 安全加固
