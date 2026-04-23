#!/bin/bash
# Video-Gen GUI 启动脚本

# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( dirname "$SCRIPT_DIR" )"

# 设置环境变量
export VIDEO_GEN_ROOT_PATH="$PROJECT_ROOT"
export VIDEO_GEN_CLI_PATH="$PROJECT_ROOT/video-gen-cli"
export VIDEO_GEN_PYTHON="$PROJECT_ROOT/video-gen-cli/venv/bin/python"
export VIDEO_GEN_DATA_DIR="$PROJECT_ROOT/data"

echo "Starting Video-Gen GUI..."
echo "Project root: $PROJECT_ROOT"
echo "Python: $VIDEO_GEN_PYTHON"
echo "Data dir: $VIDEO_GEN_DATA_DIR"
echo ""

# 启动 GUI
npm run tauri dev
