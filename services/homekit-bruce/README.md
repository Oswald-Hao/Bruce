# Bruce HomeKit Accessory - Siri Integration

让Bruce可以通过Siri语音控制。

## 功能特性

- **Siri语音交互**：通过HomeKit配件与Siri集成
- **AI助手能力**：完整的Moltbot功能
- **远程访问**：通过cloudflared隧道实现远程Siri控制
- **状态监控**：实时查看Bruce的运行状态

## 🚀 快速开始

### 第一步：安装系统服务（需要sudo）

服务文件已准备在 `/tmp/` 目录，请手动运行：

```bash
# 复制服务文件
sudo cp /tmp/homekit-bruce.service /etc/systemd/system/
sudo cp /tmp/cloudflared-homekit.service /etc/systemd/system/

# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start homekit-bruce
sudo systemctl enable homekit-bruce

# 启动cloudflared隧道
sudo systemctl start cloudflared-homekit
sudo systemctl enable cloudflared-homekit
```

**详细指南请查看：** `SETUP_GUIDE.md`

---

## 📱 配对Siri

### 在iPhone上：

1. 打开**家庭** App
2. 点击右上角 **+** 按钮
3. 选择 **添加配件**
4. 选择 **我没有代码或无法扫描**
5. 输入设备名称：`Bruce AI Assistant`
6. 输入配对PIN码：`123-45-678`
7. 完成配对

### 配置Siri短语（可选）

配对后：
1. 在家庭App中找到 **Bruce AI**
2. 点击右上角设置图标
3. 设置 **Siri短语**（如："问Bruce"）

---

## 🎮 使用方法

### 方式1：通过家庭App操作

1. 打开家庭App
2. 点击 **Bruce AI** 配件
3. 在 **Name** 字段输入问题（如："今天天气怎么样"）
4. 打开 **Bruce AI** 开关触发AI
5. Name字段会显示回复

### 方式2：通过Siri语音

设置Siri短语后，可以说：
```
嘿Siri，问Bruce今天天气怎么样
嘿Siri，让Bruce检查服务器状态
嘿Siri，Bruce给我生成一个备份脚本
```

### 3. 配对Siri

**在iPhone上：**

1. 打开**家庭** App
2. 点击右上角 **+** 按钮
3. 选择 **添加配件**
4. 选择 **我没有代码或无法扫描**
5. 输入设备名称：`Bruce AI Assistant`
6. 输入配对PIN码：`123-45-678`
7. 完成配对

### 4. 配置Siri短语（可选）

1. 在家庭App中找到 **Bruce AI Assistant**
2. 点击右上角设置图标
3. 设置 **Siri短语**（如："问Bruce"）

## 使用方法

### 方式1：通过家庭App操作

1. 打开家庭App
2. 点击 **Bruce AI Assistant**
3. 在 **Question** 字段输入问题
4. 开启 **Bruce AI** 开关
5. 在 **Response** 中查看回复

### 方式2：通过Siri语音

设置Siri短语后，可以说：

```
嘿Siri，问Bruce今天天气怎么样
嘿Siri，让Bruce检查服务器状态
嘿Siri，Bruce给我生成一个备份脚本
```

## 配对信息

- **设备名称**：Bruce AI Assistant
- **PIN码**：123-45-678
- **服务端口**：18790
- **云端访问**：通过cloudflared隧道

## 隧道配置

### 远程访问隧道

通过cloudflared隧道实现远程Siri访问：

```bash
cloudflared tunnel --url http://localhost:18790 --name bruce-homekit
```

systemd服务已配置：`cloudflared-homekit.service`

### 本地访问

如果只在局域网使用，不需要隧道，确保iPhone和服务器在同一WiFi即可。

## 特征说明

### On（电源开关）
- 表示Bruce是否在线
- 开启：Bruce准备就绪
- 关闭：Bruce离线

### Question（问题）
- 输入字段，用于向Bruce提问
- 最大1000字符

### Response（回复）
- 只读字段，显示Bruce的回答
- 最大2000字符

### Status（状态）
- 只读字段，显示当前状态
- 可能值：Ready, Thinking..., Error, Offline

## 故障排除

### 问题：无法找到配件
- 确保服务正在运行
- 确保iPhone和服务器在同一网络（或隧道正常）
- 重启服务：`systemctl restart homekit-bruce`

### 问题：Siri无法调用Bruce
- 检查Moltbot网关是否运行：`systemctl status moltbot-gateway`
- 检查HomeKit服务是否运行：`systemctl status homekit-bruce`
- 检查隧道是否运行：`systemctl status cloudflared-homekit`

### 问题：回复超时
- 检查网络连接
- 查看服务日志：`journalctl -u homekit-bruce -f`

## 技术细节

- **HomeKit协议**：HAP-Node.js
- **服务类型**：Speaker（智能音箱）
- **通信方式**：HTTP API调用Moltbot网关
- **端口**：18790（与Moltbot网关18789分离）

## 服务管理

```bash
# 启动服务
sudo systemctl start homekit-bruce

# 停止服务
sudo systemctl stop homekit-bruce

# 重启服务
sudo systemctl restart homekit-bruce

# 查看状态
sudo systemctl status homekit-bruce

# 查看日志
sudo journalctl -u homekit-bruce -f
```

## 安全建议

1. **更改PIN码**：修改index.js中的pincode配置
2. **网络隔离**：建议只在局域网使用
3. **定期更新**：保持依赖库更新

## 许可证

MIT
