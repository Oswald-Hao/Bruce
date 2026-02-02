# Bruce HomeKit 配置完成指南

## 🎉 配置状态

✅ HomeKit服务代码已创建
✅ 依赖已安装
✅ systemd服务文件已准备
✅ 服务可以正常运行

---

## 📋 下一步：手动安装系统服务

由于需要sudo权限，请手动运行以下命令：

```bash
# 1. 复制服务文件到系统目录
sudo cp /tmp/homekit-bruce.service /etc/systemd/system/
sudo cp /tmp/cloudflared-homekit.service /etc/systemd/system/

# 2. 重载systemd
sudo systemctl daemon-reload

# 3. 启动HomeKit服务
sudo systemctl start homekit-bruce
sudo systemctl enable homekit-bruce

# 4. 启动Cloudflared隧道
sudo systemctl start cloudflared-homekit
sudo systemctl enable cloudflared-homekit
```

---

## 📱 iPhone配对步骤

1. **打开家庭App**
2. **点击右上角 +**
3. **选择【添加配件】**
4. **选择【我没有代码或无法扫描】**
5. **输入信息**：
   - 名称：Bruce AI Assistant
   - PIN码：`123-45-678`
6. **添加到家庭**

---

## 🗣️ 使用方法

### 方式1：通过家庭App

1. 打开家庭App
2. 找到 **Bruce AI** 配件
3. 修改 **Name** 字段输入问题
4. 打开 **Bruce AI** 开关触发AI

### 方式2：通过Siri（配对后设置）

1. 在家庭App中找到 **Bruce AI**
2. 点击设置图标
3. 配置Siri短语（如："问Bruce"）
4. 说："嘿Siri，问Bruce天气怎么样"

---

## 🔧 服务管理

```bash
# 查看服务状态
sudo systemctl status homekit-bruce
sudo systemctl status cloudflared-homekit

# 重启服务
sudo systemctl restart homekit-bruce
sudo systemctl restart cloudflared-homekit

# 查看日志
sudo journalctl -u homekit-bruce -f
```

---

## 📊 技术信息

- **服务端口**：18790
- **配对PIN**：123-45-678
- **配件名称**：Bruce AI Assistant
- **服务类型**：Lightbulb（触发器）

---

## 🌐 隧道信息

- **本地端口**：18790
- **隧道服务**：cloudflared-homekit
- **状态**：需要启动后查看cloudflare面板获取公网地址

---

## ❓ 常见问题

**Q: 服务启动失败？**
A: 检查18790端口是否被占用
```bash
sudo netstat -tulpn | grep 18790
```

**Q: 无法在家庭App中找到配件？**
A: 确保服务正在运行，且iPhone在同一网络（或隧道正常）

**Q: Siri无法调用？**
A: 需要先配对，然后在家庭App中设置Siri短语

---

## 🎯 快速测试

安装服务后，快速测试：

```bash
# 1. 检查服务状态
sudo systemctl status homekit-bruce

# 2. 检查端口监听
sudo netstat -tulpn | grep 18790

# 3. 查看日志
sudo journalctl -u homekit-bruce -n 20
```

一切正常后，就可以在iPhone上配对了！

---

**祝你使用愉快！🎉**
