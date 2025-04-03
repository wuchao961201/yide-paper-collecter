#!/bin/bash

# 获取脚本的绝对路径
SCRIPT_PATH=$(realpath run.py)
WORKSPACE_PATH=$(dirname "$SCRIPT_PATH")

# 创建临时crontab文件
echo "# 每天上午10点执行论文收集器脚本" > /tmp/paper_collector_cron
echo "0 10 * * * cd $WORKSPACE_PATH && /usr/bin/python3 $SCRIPT_PATH collect >> $WORKSPACE_PATH/logs/cron_execution.log 2>&1" >> /tmp/paper_collector_cron

# 安装新的crontab
echo "正在安装cron作业..."
crontab /tmp/paper_collector_cron
rm /tmp/paper_collector_cron

echo "cron作业已安装。论文收集器将在每天上午10点执行。"
echo "您可以使用 'crontab -l' 命令查看当前的cron作业。" 