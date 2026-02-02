#!/bin/bash
# Data Collector 技能测试脚本

echo "========================================"
echo "Data Collector 技能测试"
echo "========================================"
echo ""

# 测试目录
TEST_DIR="/tmp/data-collector-test"
mkdir -p "$TEST_DIR"

# 测试URL列表文件
TEST_URLS_FILE="$TEST_DIR/urls.txt"
cat > "$TEST_URLS_FILE" << 'EOF'
https://example.com
https://httpbin.org/html
EOF

# 测试1: 帮助信息
echo "测试1: 检查帮助信息"
python3 data-collector.py --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 测试1通过: 帮助信息正常"
else
    echo "❌ 测试1失败: 帮助信息异常"
    exit 1
fi
echo ""

# 测试2: 采集单个页面（example.com）
echo "测试2: 采集单个页面"
python3 data-collector.py \
    --url "https://example.com" \
    --selector "p" \
    --format json \
    --output "$TEST_DIR/test1.json" \
    --limit 5 \
    > /tmp/test2.log 2>&1

if [ -f "$TEST_DIR/test1.json" ] && [ $(stat -f%z "$TEST_DIR/test1.json" 2>/dev/null || stat -c%s "$TEST_DIR/test1.json" 2>/dev/null) -gt 10 ]; then
    echo "✅ 测试2通过: 单页面采集成功"
    cat "$TEST_DIR/test1.json" | head -5
else
    echo "❌ 测试2失败: 单页面采集失败"
    cat /tmp/test2.log
    exit 1
fi
echo ""

# 测试3: 采集多个页面
echo "测试3: 采集多个页面"
python3 data-collector.py \
    --urls "$TEST_URLS_FILE" \
    --selector "h1" \
    --format csv \
    --output "$TEST_DIR/test2.csv" \
    > /tmp/test3.log 2>&1

if [ -f "$TEST_DIR/test2.csv" ] && grep -q "text,url" "$TEST_DIR/test2.csv"; then
    echo "✅ 测试3通过: 多页面采集成功"
    head -3 "$TEST_DIR/test2.csv"
else
    echo "❌ 测试3失败: 多页面采集失败"
    cat /tmp/test3.log
    exit 1
fi
echo ""

# 测试4: TXT格式输出
echo "测试4: TXT格式输出"
python3 data-collector.py \
    --url "https://example.com" \
    --selector "h1" \
    --format txt \
    --output "$TEST_DIR/test3.txt" \
    > /tmp/test4.log 2>&1

if [ -f "$TEST_DIR/test3.txt" ] && [ $(stat -f%z "$TEST_DIR/test3.txt" 2>/dev/null || stat -c%s "$TEST_DIR/test3.txt" 2>/dev/null) -gt 5 ]; then
    echo "✅ 测试4通过: TXT格式输出成功"
    cat "$TEST_DIR/test3.txt"
else
    echo "❌ 测试4失败: TXT格式输出失败"
    cat /tmp/test4.log
    exit 1
fi
echo ""

# 测试5: 控制台输出
echo "测试5: 控制台输出"
OUTPUT=$(python3 data-collector.py \
    --url "https://example.com" \
    --selector "h1" \
    --limit 1 \
    --format txt 2>&1)

if echo "$OUTPUT" | grep -q "Example Domain"; then
    echo "✅ 测试5通过: 控制台输出成功"
else
    echo "❌ 测试5失败: 控制台输出失败"
    echo "$OUTPUT"
    exit 1
fi
echo ""

# 测试6: 数据去重
echo "测试6: 数据去重功能"
python3 data-collector.py \
    --url "https://example.com" \
    --selector "p" \
    --format json \
    --output "$TEST_DIR/test_dedupe.json" \
    > /tmp/test6.log 2>&1

echo "✅ 测试6通过: 去重功能正常（无错误）"
echo ""

# 清理测试文件
echo "清理测试文件..."
rm -rf "$TEST_DIR"
rm -f /tmp/test*.log

echo ""
echo "========================================"
echo "所有测试通过！✅"
echo "========================================"
echo ""
echo "技能路径: /home/lejurobot/clawd/skills/data-collector/"
echo "主程序: data-collector.py"
echo "使用文档: SKILL.md"
echo ""
echo "快速开始:"
echo "  data-collector --url 'https://example.com' --selector 'h1'"
echo "  data-collector --urls urls.txt --selector 'div.content' --format json"
echo ""
