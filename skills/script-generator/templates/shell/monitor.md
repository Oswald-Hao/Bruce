#!/bin/bash
# 自动生成的Shell脚本 - 监控脚本
# 生成时间: {{timestamp}}
# 需求: {{prompt}}

set -e

# 配置变量
PROCESS_NAME="{{process_name|app}}"
CPU_THRESHOLD="{{cpu_threshold|80}}"
MEMORY_THRESHOLD="{{memory_threshold|80}}"
LOG_FILE="{{log_file|/var/log/monitor.log}}"

while true; do
    # 获取进程信息
    PID=$(pgrep "$PROCESS_NAME" | head -n 1)

    if [ -z "$PID" ]; then
        echo "$(date): 进程 $PROCESS_NAME 未运行" >> "$LOG_FILE"
    else
        CPU=$(ps -p $PID -o %cpu --no-headers)
        MEMORY=$(ps -p $PID -o %mem --no-headers)

        echo "$(date): $PROCESS_NAME (PID: $PID) CPU: $CPU% MEM: $MEMORY%" >> "$LOG_FILE"

        # 检查阈值
        if (( $(echo "$CPU > $CPU_THRESHOLD" | bc -l) )); then
            echo "$(date): ⚠️ CPU告警: $CPU% > $CPU_THRESHOLD%" >> "$LOG_FILE"
        fi

        if (( $(echo "$MEMORY > $MEMORY_THRESHOLD" | bc -l) )); then
            echo "$(date): ⚠️ 内存告警: $MEMORY% > $MEMORY_THRESHOLD%" >> "$LOG_FILE"
        fi
    fi

    sleep {{interval|60}}
done
