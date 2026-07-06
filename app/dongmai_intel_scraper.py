#!/usr/bin/env python3
"""
动脉网情报列表爬虫
从 https://www.vbdata.cn/intelList 提取情报数据
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_intel_list():
    """获取动脉网情报列表"""
    url = "https://www.vbdata.cn/intelList"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.vbdata.cn/"
    }
    
    print(f"🔍 正在请求: {url}")
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"✅ 状态码: {resp.status_code}")
    
    html = resp.text
    
    # ============================================================
    # 方法1：从 __NUXT__ 提取数据
    # ============================================================
    pattern = r'window\.__NUXT__\s*=\s*\((function\(.*?\)\s*\{.*?\})\)\s*;'
    match = re.search(pattern, html, re.DOTALL)
    
    if match:
        print("✅ 找到 __NUXT__ 数据")
        with open("nuxt_debug.js", "w") as f:
            f.write(match.group(1))
        print("📁 原始数据已保存到 nuxt_debug.js")
        
        nuxt_content = match.group(1)
        
        titles = re.findall(r'"title":"([^"]+)"', nuxt_content)
        urls = re.findall(r'"url":"([^"]+)"', nuxt_content)
        times = re.findall(r'"time":"([^"]+)"', nuxt_content)
        
        if titles:
            print(f"📰 找到 {len(titles)} 条文章标题")
            articles = []
            for i, title in enumerate(titles[:20]):
                articles.append({
                    "title": title,
                    "url": urls[i] if i < len(urls) else "",
                    "time": times[i] if i < len(times) else "",
                    "source": "动脉网"
                })
            return {
                "source": "动脉网",
                "fetched_at": datetime.now().isoformat(),
                "count": len(articles),
                "articles": articles
            }
    
    # ============================================================
    # 方法2：从 HTML 中解析文章列表
    # ============================================================
    print("⚠️ __NUXT__ 提取失败，尝试 HTML 解析...")
    soup = BeautifulSoup(html, "html.parser")
    
    articles = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if "/intel/" in href and len(text) > 10:
            articles.append({
                "title": text,
                "url": "https://www.vbdata.cn" + href if href.startswith("/") else href,
                "time": "",
                "source": "动脉网"
            })
    
    if articles:
        print(f"📰 通过 HTML 解析找到 {len(articles)} 条文章")
        return {
            "source": "动脉网",
            "fetched_at": datetime.now().isoformat(),
            "count": len(articles),
            "articles": articles[:20]
        }
    
    print("⚠️ 未能提取文章列表，返回页面基本信息")
    return {
        "source": "动脉网",
        "fetched_at": datetime.now().isoformat(),
        "count": 0,
        "articles": [],
        "page_info": {
            "status": resp.status_code,
            "content_length": len(html),
            "sample": html[:500]
        }
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🕷️ 动脉网情报列表爬虫")
    print("=" * 60)
    
    result = fetch_intel_list()
    
    print("\n📊 结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    filename = f"dongmai_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n📁 结果已保存到: {filename}")