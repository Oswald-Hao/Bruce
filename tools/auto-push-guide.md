# 自动推送系统配置

## 已配置的两种自动推送方式

### ✅ 方案4：Git钩子推送（已启用）

**原理：** 每次执行`git commit`后，自动执行`git push`

**状态：** ✅ 已启用并测试通过

**使用方法：**
```bash
cd /home/lejurobot/clawd
git add .
git commit -m "提交信息"
# 推送会自动执行，无需手动push
```

**优点：**
- ✓ 最简单，无需额外配置
- ✓ 每次commit都自动推送
- ✓ 不占用后台资源

**适用场景：**
- 需要实时推送
- 代码更新频繁
- 希望每次commit都立即同步

---

### 📋 方案3：文件监听推送（已配置，待启动）

**原理：** 监听文件变化，自动提交并推送

**状态：** ⚠️  已配置，需要手动启动

**安装步骤：**

1. **复制systemd服务文件：**
```bash
sudo cp /home/lejurobot/clawd/tools/git-auto-pusher.service /etc/systemd/system/
sudo systemctl daemon-reload
```

2. **启动服务：**
```bash
sudo systemctl start git-auto-pusher
sudo systemctl enable git-auto-pusher  # 开机自启
```

3. **检查服务状态：**
```bash
sudo systemctl status git-auto-pusher
```

4. **查看日志：**
```bash
sudo journalctl -u git-auto-pusher -f
```

**停止服务：**
```bash
sudo systemctl stop git-auto-pusher
sudo systemctl disable git-auto-pusher
```

**手动启动（不使用systemd）：**
```bash
python3 /home/lejurobot/clawd/tools/file-watcher.py /home/lejurobot/clawd 30
# 最后的数字是检查间隔（秒）
```

**优点：**
- ✓ 完全自动化，无需手动操作
- ✓ 后台运行，不影响其他任务
- ✓ 支持冷却时间，避免频繁推送

**适用场景：**
- 完全自动化，不想手动commit
- 代码更新频繁且规律
- 需要持续监听文件变化

---

## 推送流程

### 使用Git钩子（方案4）

```
修改文件
  ↓
git add .
  ↓
git commit -m "信息"  ← 自动触发git push
  ↓
推送到GitHub
```

### 使用文件监听（方案3）

```
修改文件
  ↓
监听器检测到变化
  ↓
自动git add
  ↓
自动git commit  ← 自动触发git push
  ↓
推送到GitHub
```

---

## 同时启用两个方案

两个方案可以同时启用：
- **方案4（Git钩子）：** 手动commit时自动推送
- **方案3（文件监听）：** 自动检测变化并推送

这样无论你手动commit还是系统自动commit，都会自动推送到GitHub。

---

## 故障排查

### Git钩子不工作

1. 检查钩子权限：
```bash
ls -la .git/hooks/post-commit
```

应该显示：`-rwxrwxr-x`

2. 如果没有执行权限，添加：
```bash
chmod +x .git/hooks/post-commit
```

### 文件监听器不工作

1. 检查服务状态：
```bash
sudo systemctl status git-auto-pusher
```

2. 查看日志：
```bash
sudo journalctl -u git-auto-pusher -n 50
```

3. 重启服务：
```bash
sudo systemctl restart git-auto-pusher
```

---

## 当前状态

- ✅ Git钩子（post-commit）：已启用
- ⚠️  文件监听器：已配置，需要手动启动
- ✅ 推送脚本：git-push.sh
- ✅ GitHub仓库：https://github.com/Oswald-Hao/Bruce.git

---

## 测试

### 测试Git钩子
```bash
cd /home/lejurobot/clawd
echo "test" >> test.txt
git add test.txt
git commit -m "测试Git钩子"
# 应该会自动推送到GitHub
```

### 测试文件监听器
```bash
# 启动监听器后
cd /home/lejurobot/clawd/skills
echo "test" >> test.py
# 等待30-60秒，应该会自动提交并推送
```
