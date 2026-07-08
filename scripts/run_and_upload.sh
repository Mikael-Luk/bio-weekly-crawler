#!/bin/bash
# =============================================
# bio-weekly-crawler - 一键运行两个爬虫 + 传 NAS
# =============================================

set -e

echo "🚀 开始执行 bio-weekly-crawler..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📂 项目目录: $PROJECT_ROOT"

# 激活虚拟环境
source "$HOME/news_scraper/venv/bin/activate" || { echo "❌ 虚拟环境激活失败"; exit 1; }

# 确保 reports 目录存在
mkdir -p data/reports

echo "🕷️ 1. 运行动脉网文章列表爬虫 (category=166)..."
python -m src.dongmai.crawler

echo "🕷️ 2. 运行动脉网情报列表爬虫..."
python -m src.dongmai_intel.crawler

echo "✅ 所有爬虫执行完成！"

# 复制所有结果到 NAS
echo "📤 同步到 NAS reports 目录..."
scp -r data/reports/* jichangtao@192.168.0.69:/docker/bio-weekly/data/reports/ 2>/dev/null || echo "⚠️ 同步跳过或无新文件"

echo "🎉 全部完成！$(date '+%Y-%m-%d %H:%M:%S')"