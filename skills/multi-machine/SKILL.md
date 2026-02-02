# Multi-Machine Controller

多机器控制能力，支持SSH远程执行、集群管理、并行任务。

## 功能特性

- 多机器SSH连接管理（密钥/密码认证）
- 单机/多机并行命令执行
- 文件上传/下载（单机/批量）
- 集群状态监控（在线/离线/负载）
- 统一命令分发
- 任务超时控制和错误处理

## 使用方法

### 1. 配置机器列表

编辑 `machines.json`：

```json
{
  "machines": [
    {
      "name": "server1",
      "host": "192.168.1.100",
      "port": 22,
      "username": "user",
      "auth": {
        "type": "key",
        "key_path": "/home/user/.ssh/id_rsa"
      }
    },
    {
      "name": "server2",
      "host": "192.168.1.101",
      "port": 22,
      "username": "user",
      "auth": {
        "type": "password",
        "password": "your_password"
      }
    }
  ]
}
```

### 2. 执行单机命令

```bash
python3 multi-machine.py run <machine_name> "<command>"
```

### 3. 并行执行多机命令

```bash
python3 multi-machine.py parallel "<command>"
```

### 4. 查看集群状态

```bash
python3 multi-machine.py status
```

### 5. 上传文件到单机

```bash
python3 multi-machine.py upload <machine_name> <local_file> <remote_path>
```

### 6. 下载文件从单机

```bash
python3 multi-machine.py download <machine_name> <remote_file> <local_path>
```

## 测试

运行测试用例：

```bash
python3 test_multi-machine.py
```

## 实现方式

- Python 3 + paramiko（SSH客户端）
- 多线程并行执行
- JSON配置文件
- 实时状态反馈
