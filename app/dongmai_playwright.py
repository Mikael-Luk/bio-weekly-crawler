cat > dongmai_playwright.py << 'EOF'
#!/usr/bin/env python3
"""
动脉网情报爬虫 - pyppeteer 版（兼容旧系统）
"""

import asyncio
import json
import re
from datetime import datetime
from pyppeteer import launch

async def fetch_dongmai_pyppeteer():
    print("🔄 启动浏览器...")
    
    try:
        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process'
            ],
            handleSIGINT=False,
            handleSIGTERM=False,
            handleSIGHUP=False
        )
        page = await browser.newPage()
        
        url = "https://www.vbdata.cn/intelList"
        print(f"🔍 正在加载: {url}")
        
        await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 60000})
        print("✅ 页面加载完成")
        await asyncio.sleep(3)
        
        articles_data = await page.evaluate("""
            () => {
                const bodyText = document.body.innerText;
                const lines = bodyText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                const articles = [];
                let current = null;
                for (const line of lines) {
                    if (/^\\d{1,2}:\\d{2}$/.test(line) || /^\\d{4}年\\d{2}月\\d{2}日/.test(line)) {
                        if (current && current.title) {
                            articles.push(current);
                        }
                        current = {
                            time: line,
                            title: '',
                            content: ''
                        };
                    } else if (current) {
                        const isTitle = line.startsWith('#') || 
                            (line.length > 10 && line.length < 80 && 
                             !line.includes('，') && !line.includes('。') && 
                             !line.includes('、') && !line.includes('：'));
                        if (isTitle && !current.title) {
                            current.title = line.replace(/^#\\s*/, '').trim();
                        } else {
                            current.content += line + '\\n';
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
        
        if articles:
            md_filename = f"dongmai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(md_filename, "w", encoding="utf-8") as f:
                f.write(f"# 🏥 动脉网情报\n\n")
                f.write(f"> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
                f.write(f"> 共 {len(articles)} 条情报\n\n---\n\n")
                for i, item in enumerate(articles, 1):
                    f.write(f"## {i}. {item['title']}\n\n")
                    if item['time']:
                        f.write(f"🕐 {item['time']}\n\n")
                    if item['content']:
                        f.write(f"{item['content']}\n\n")
                    f.write("---\n\n")
            print(f"📄 Markdown 已保存: {md_filename}")
        
        await browser.close()
        return articles
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        print("🔚 关闭")

async def main():
    print("=" * 60)
    print("🕷️ 动脉网情报爬虫 (pyppeteer 版)")
    print("=" * 60)
    await fetch_dongmai_pyppeteer()

if __name__ == "__main__":
    asyncio.run(main())
EOF