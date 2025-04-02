#!/bin/bash

# 论文收集器启动脚本
# 作者: Liu Yide

# 进入脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 确保Python环境正确配置
# 如果使用虚拟环境，取消下面的注释并修改路径
# source /path/to/your/venv/bin/activate

# 安装必要的依赖
echo "正在检查并安装必要的依赖..."
pip install -q feedparser requests

# 确保配置文件存在且权限正确
if [ -f config.py ]; then
    # 确保配置文件权限安全 (只有用户可读写)
    chmod 600 config.py
    echo "已设置config.py的安全权限"
else
    echo "警告: 未找到config.py配置文件，将使用脚本中的默认值"
fi

# 运行论文收集器
echo "启动论文收集器..."
python3 demo_PaperCollector_Yide.py

echo "论文收集器执行完成" 