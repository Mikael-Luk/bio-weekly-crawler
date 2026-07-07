#!/usr/bin/env python3
"""
动脉网情报爬虫 - Playwright 版（最终优化版）
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

def clean_content(text):
    """清理内容中的页脚和垃圾信息"""
    if not text:
        return ""
    # 移除常见页脚
    text = re.sub(r'(关于我们|联系我们|友情链接|©|ICP备|公网安备|客服|意见反馈|全球产业链接|企业对接|在线|7x24H).*?$', '', text, flags=re.DOTALL | re.MULTILINE)
    # 移除链接和多余符号
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def save_as_markdown(articles, filename):
    """保存 Markdown"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# 🏥 动脉网情报\n\n")
        f.write(f"> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        f.write(f"> 共 {len(articles)} 条情报\n\n")
        f.write("---\n\n")
        
        for i, item in enumerate(articles, 1):
            title = item.get("title", "无标题").strip()
            time_str = item.get("time", "").strip()
            content = clean_content(item.get("content", ""))
            
            if len(title) < 5:
                continue
                
            f.write(f"## {i}. {title}\n\n")
            if time_str:
                f.write(f"🕐 {time_str}\n\n")
            if content:
                f.write(f"{content}\n\n")
            f.write("---\n\n")
        
        f.write(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

async def fetch_dongmai_playwright():
    print("🔄 启动浏览器...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        page = await context.new_page()
        
        url = "https://www.vbdata.cn/intelList"
        print(f"🔍 加载: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(4)
            
            articles_data = await page.evaluate("""
                () => {
                    const bodyText = document.body.innerText;
                    const lines = bodyText.split('\n').map(l => l.trim()).filter(l => l.length > 5);
                    const articles = [];
                    let current = null;
                    for (const line of lines) {
                        if (/^\d{1,2}:\d{2}$/.test(line) || /^\d{4}年\d{2}月\d{2}日/.test(line)) {
                            if (current && current.title) articles.push(current);
                            current = { time: line, title: '', content: '' };
                        } else if (current) {
                            const isTitle = line.length < 85 && !line.includes('。') && !line.includes('，') && !line.includes('、');
                            if (isTitle && !current.title) {
                                current.title = line.replace(/^#\s*/, '').trim();
                            } else {
                                current.content += line + '\n';
                            }
                        }
                    }
                    if (current && current.title) articles.push(current);
                    return articles;
                }
            """)
            
            print(f"📰 提取到 {len(articles_data)} 条情报")
            
            articles = [{"title": item.get('title', '无标题')[:120], "time": item.get('time', ''), "content": item.get('content', ''), "source": "动脉网"} for item in articles_data]
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_as_markdown(articles, f"dongmai_{timestamp}.md")
            
            with open(f"dongmai_{timestamp}.json", "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 文件已生成: dongmai_{timestamp}.md / .json")
            return articles
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()

async def main():
    print("=" * 60)
    print("🕷️ 动脉网情报爬虫")
    print("=" * 60)
    await fetch_dongmai_playwright()

if __name__ == "__main__":
    asyncio.run(main())