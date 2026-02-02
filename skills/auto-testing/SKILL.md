# Auto Testing Skill

自动化测试框架 - 为代码质量保驾护航

## 功能说明

- 单元测试（函数/类级别）
- 集成测试（模块/服务级别）
- 性能测试（响应时间、吞吐量）
- 测试覆盖率报告
- 自动测试发现和运行

## 使用方式

```bash
# 生成测试框架
cd /home/lejurobot/clawd/skills/auto-testing
python3 auto_testing.py --init <project_path>

# 运行所有测试
python3 auto_testing.py --run <project_path>

# 运行单个测试文件
python3 auto_testing.py --run <test_file.py>

# 生成覆盖率报告
python3 auto_testing.py --coverage <project_path>
```

## 测试用例

```bash
# 运行测试
cd /home/lejurobot/clawd/skills/auto-testing
python3 test_auto_testing.py
```

## 实现方式

Python 3 + unittest（标准库） + coverage（测试覆盖率） + pytest（可选）
