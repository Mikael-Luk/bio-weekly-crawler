#!/bin/bash
# =============================================
# bio-weekly-crawler - 一键运行 + 分类同步到 NAS ‘动脉网’ 文件夹
# =============================================

# 不要 set -e，避免 scp 无文件时脚本退出
# set -e

echo "🚀 开始执行 bio-weekly-crawler..."

# =============================================
# 1. 确定项目路径
# =============================================
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📂 项目目录: $PROJECT_ROOT"

# =============================================
# 2. 激活虚拟环境（使用项目内的 venv）
# =============================================
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$HOME/news_scraper/venv/bin/activate" ]; then
    source "$HOME/news_scraper/venv/bin/activate"
else
    echo "❌ 找不到虚拟环境"
    exit 1
fi

# =============================================
# 3. 确保本地目录存在
# =============================================
mkdir -p data/reports

# =============================================
# 4. 运行爬虫（检查文件是否存在）
# =============================================
echo "🕷️ 1. 运行动脉网情报列表爬虫..."
if [ -f "src/dongmai/crawler.py" ]; then
    python src/dongmai/crawler.py
else
    echo "⚠️ 找不到 src/dongmai/crawler.py"
fi

# =============================================
# 5. 同步到 NAS（只传存在的文件）
# =============================================
echo "📤 同步到 NAS..."

# NAS 基础路径（确认实际路径）
NAS_BASE="/volume1/docker/bio-weekly/data/reports"
NAS_USER="jichangtao"
NAS_HOST="192.168.0.69"

# 创建 NAS 目录结构
echo "📁 创建 NAS 目录..."
ssh ${NAS_USER}@${NAS_HOST} "mkdir -p ${NAS_BASE}/动脉网/情报页 ${NAS_BASE}/动脉网/主页面"

# 同步情报页文件
echo "📄 同步情报页..."
if ls data/reports/dongmai_intel_*.md 1> /dev/null 2>&1; then
    scp data/reports/dongmai_intel_*.md ${NAS_USER}@${NAS_HOST}:${NAS_BASE}/动脉网/情报页/
    echo "✅ 情报页上传完成"
else
    echo "⚠️ 没有情报页文件"
fi

# 同步文章页文件
echo "📄 同步文章页..."
if ls data/reports/dongmai_*.md 2>/dev/null | grep -v "dongmai_intel_" > /dev/null; then
    scp data/reports/dongmai_*.md ${NAS_USER}@${NAS_HOST}:${NAS_BASE}/动脉网/主页面/ 2>/dev/null
    echo "✅ 文章页上传完成"
else
    echo "⚠️ 没有文章页文件"
fi

# 同步 JSON 文件（可选）
echo "📄 同步 JSON 备份..."
if ls data/reports/dongmai_*.json 1> /dev/null 2>&1; then
    scp data/reports/dongmai_*.json ${NAS_USER}@${NAS_HOST}:${NAS_BASE}/动脉网/ 2>/dev/null
    echo "✅ JSON 备份上传完成"
else
    echo "⚠️ 没有 JSON 文件"
fi

echo ""
echo "🎉 完成！"
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
