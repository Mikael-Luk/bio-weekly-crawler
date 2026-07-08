#!/bin/bash
# =============================================
# bio-weekly-crawler - 一键运行 + 分类同步到 NAS ‘动脉网’ 文件夹
# =============================================

set -e

echo "🚀 开始执行 bio-weekly-crawler..."

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📂 项目目录: $PROJECT_ROOT"

# 激活虚拟环境
source "$HOME/news_scraper/venv/bin/activate" || { echo "❌ 虚拟环境激活失败"; exit 1; }

# 确保本地 reports 目录存在
mkdir -p data/reports

# 运行爬虫
echo "🕷️ 1. 运行动脉网文章列表爬虫..."
python -m src.dongmai.crawler

echo "🕷️ 2. 运行动脉网情报列表爬虫..."
python -m src.dongmai_intel.crawler

echo "✅ 爬虫执行完成！"

# 同步并分类到 NAS
echo "📤 同步并分类到 NAS ‘动脉网’ 文件夹..."

# 创建 NAS 目录结构
ssh jichangtao@192.168.0.69 "mkdir -p /docker/bio-weekly/data/reports/动脉网/情报页 /docker/bio-weekly/data/reports/动脉网/主页面"

# 同步情报页文件
scp data/reports/dongmai_intel_* jichangtao@192.168.0.69:/docker/bio-weekly/data/reports/动脉网/情报页/ 2>/dev/null || echo "⚠️ 无情报文件"

# 同步文章页文件
scp data/reports/dongmai_article_* data/reports/dongmai_full_* jichangtao@192.168.0.69:/docker/bio-weekly/data/reports/动脉网/主页面/ 2>/dev/null || echo "⚠️ 无文章文件"

echo "🎉 同步完成！文件已分类到 NAS ‘动脉网’ 文件夹"
echo "   $(date '+%Y-%m-%d %H:%M:%S')"