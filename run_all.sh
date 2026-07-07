#!/bin/bash
# ============================================================
# 生物经济投融资周报 - 统一运行脚本
# 打包上传版
# ============================================================

echo "=========================================="
echo "🚀 生物经济投融资周报 - 数据采集"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

source ~/news_scraper/venv/bin/activate

# ============================================================
# 1. 动脉网 (P1)
# ============================================================
echo ""
echo "📰 [1/5] 正在采集: 动脉网 (P1)..."
cd ~/bio-weekly/src/dongmai
python3 crawler.py

# ============================================================
# 后续源...
# ============================================================

# ============================================================
# 打包并上传
# ============================================================
echo ""
echo "📦 打包并上传所有报告到 NAS..."

cd ~/bio-weekly

# 检查是否有文件
if find src -name "dongmai_*.md" -o -name "dongmai_*.json" | grep -q .; then
    # 收集文件
    mkdir -p temp_reports
    find src -name "dongmai_*.md" -exec cp {} temp_reports/ \;
    find src -name "dongmai_*.json" -exec cp {} temp_reports/ \;
    
    # 压缩
    cd temp_reports
    tar -czf ../reports.tar.gz *
    cd ..
    
    # 上传压缩包
    scp reports.tar.gz jichangtao@192.168.0.69:/volume1/docker/bio-weekly/data/reports/
    
    # 在 NAS 上解压并清理
    ssh jichangtao@192.168.0.69 "cd /volume1/docker/bio-weekly/data/reports/ && tar -xzf reports.tar.gz && rm reports.tar.gz"
    
    # 清理本地
    rm -rf temp_reports reports.tar.gz
    find src -name "dongmai_*.md" -delete
    find src -name "dongmai_*.json" -delete
    
    echo "✅ 上传完成"
else
    echo "⚠️ 没有文件需要上传"
fi

echo ""
echo "=========================================="
echo "✅ 采集完成！"
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="