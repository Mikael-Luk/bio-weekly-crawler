#!/usr/bin/env python3
"""
动脉网情报爬虫 - Playwright 版（优化提取）
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

def save_as_markdown(articles, filename):
    """将文章列表保存为 Markdown 文件"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🏥 动脉网情报\n\n")
        f.write(f"> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        f.write(f"> 共 {len(articles)} 条情报\n\n")
        f.write("---\n\n")
        
        for i, item in enumerate(articles, 1):
            title = item.get("title", "无标题")
            time_str = item.get("time", "")
            content = item.get("content", "")
            
            f.write(f"## {i}. {title}\n\n")
            if time_str:
                f.write(f"🕐 {time_str}\n\n")
            if content:
                f.write(f"{content.strip()}\n\n")
            f.write("---\n\n")
        
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

async def fetch_dongmai_playwright():
    """使用 Playwright 加载页面并提取完整情报"""
    
    print("🔄 启动浏览器...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        url = "https://www.vbdata.cn/intelList"
        print(f"🔍 正在加载列表页: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            print("✅ 列表页加载完成")
            
            await asyncio.sleep(4)  # 增加等待时间
            
            print("🔍 提取情报内容...")
            
            articles_data = await page.evaluate("""
                () => {
                    const bodyText = document.body.innerText;
                    const lines = bodyText.split('\n').map(l => l.trim()).filter(l => l.length > 5);
                    const articles = [];
                    let current = null;
                    
                    for (const line of lines) {
                        // 匹配时间
                        if (/^\d{1,2}:\d{2}$/.test(line) || /^\d{4}年\d{2}月\d{2}日/.test(line)) {
                            if (current && current.title) {
                                articles.push(current);
                            }
                            current = { time: line, title: '', content: '' };
                        } 
                        else if (current) {
                            // 判断是否是标题
                            const isTitle = line.length < 85 && 
                                           !line.includes('。') && 
                                           !line.includes('，') && 
                                           !line.includes('、') && 
                                           !line.match(/^[a-zA-Z0-9?？�]+$/);
                            
                            if (isTitle && !current.title) {
                                current.title = line.replace(/^#\s*/, '').trim();
                            } else {
                                // 清理乱码和问号
                                const cleanLine = line.replace(/[?？�]+/g, ' ').trim();
                                if (cleanLine.length > 8) {
                                    current.content += cleanLine + '\n';
                                }
                            }
                        }
                    }
                    if (current && current.title) {
                        articles.push(current);
                    }
                    return articles;
                }
            """)
            
            print(f"📰 提取到 {len(articles_data)} 条情报")
            
            articles = []
            for item in articles_data:
                articles.append({
                    "title": item.get('title', '无标题')[:120],
                    "time": item.get('time', ''),
                    "content": item.get('content', ''),
                    "source": "动脉网"
                })
            
            # 保存文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            md_filename = f"dongmai_{timestamp}.md"
            json_filename = f"dongmai_{timestamp}.json"
            
            save_as_markdown(articles, md_filename)
            
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"📄 Markdown: {md_filename}")
            print(f"📁 JSON: {json_filename}")
            
            return articles
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()
            print("🔚 浏览器关闭")

async def main():
    print("=" * 60)
    print("🕷️ 动脉网情报爬虫")
    print("=" * 60)
    await fetch_dongmai_playwright()

if __name__ == "__main__":
    asyncio.run(main())