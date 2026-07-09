#!/usr/bin/env python3
"""
动脉网文章详情爬虫 - 主文章
输出到: data/reports/动脉网/主文章/
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright
import os

OUTPUT_DIR = "data/reports/动脉网/主文章"

async def fetch_dongmai_full(limit=5):
    print(f"🚀 启动动脉网文章爬虫（抓取 {limit} 条详情）...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    articles = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        list_url = "https://www.vbdata.cn/articleList?category=166"
        await page.goto(list_url, wait_until="networkidle", timeout=90000)
        await asyncio.sleep(5)
        
        for _ in range(4):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
        
        links = await page.evaluate("""
            () => {
                const links = [];
                const seen = new Set();
                document.querySelectorAll('a').forEach(a => {
                    const href = a.href;
                    const text = a.innerText.trim();
                    if (href && href.includes('vbdata.cn') && text.length > 15 && !seen.has(href)) {
                        seen.add(href);
                        links.push({title: text, href: href});
                    }
                });
                return links.slice(0, 15);
            }
        """)
        print(f"找到 {len(links)} 条潜在文章链接")
        
        for i, item in enumerate(links[:limit], 1):
            print(f"[{i}/{limit}] 抓取: {item['title'][:50]}...")
            try:
                await page.goto(item['href'], wait_until="networkidle", timeout=30000)
                await asyncio.sleep(5)
                
                content = await page.evaluate("""
                    () => {
                        const selectors = [
                            'article', '.article-content', '.content',
                            '.rich-text', '.richText', '.main-content',
                            '.post-content', 'main'
                        ];
                        for (let sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) {
                                const text = el.innerText.trim();
                                if (text.length > 100) return text;
                            }
                        }
                        let bodyText = document.body.innerText.trim();
                        // 移除页脚
                        const footerKeywords = ['©', '渝ICP备', '友情链接', '关于我们', '联系电话'];
                        for (const kw of footerKeywords) {
                            if (bodyText.includes(kw)) {
                                bodyText = bodyText.split(kw)[0].trim();
                            }
                        }
                        return bodyText;
                    }
                """)

                articles.append({
                    "title": item['title'],
                    "link": item['href'],
                    "content": content.strip(),
                    "source": "动脉网"
                })
                print(f"   ✅ 成功，内容长度: {len(articles[-1]['content'])} 字符")

            except Exception as e:
                print(f"   ❌ 抓取失败: {e}")
                continue

        await browser.close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"dongmai_full_{timestamp}"
    
    md_path = f"{OUTPUT_DIR}/{filename}.md"
    json_path = f"{OUTPUT_DIR}/{filename}.json"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 🏥 动脉网文章详情\n\n")
        f.write(f"> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        f.write(f"> 共 {len(articles)} 篇文章\n\n")
        f.write("---\n\n")
        
        for i, a in enumerate(articles, 1):
            f.write(f"## {i}. {a['title']}\n\n")
            f.write(f"🔗 {a['link']}\n\n")
            f.write(f"{a['content']}\n\n")
            f.write("---\n\n")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 完成！共抓取 {len(articles)} 条完整文章")
    print(f"📄 Markdown: {md_path}")
    print(f"📁 JSON: {json_path}")
    return articles

async def main():
    await fetch_dongmai_full(limit=5)

if __name__ == "__main__":
    asyncio.run(main())
