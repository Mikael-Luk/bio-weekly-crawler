#!/usr/bin/env python3
"""
动脉网文章爬虫 - 可靠版（优化内容提取）
"""
import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_dongmai_full(limit=5):
    print(f"🚀 启动动脉网爬虫（抓取 {limit} 条完整文章）...")
    articles = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        list_url = "https://www.vbdata.cn/articleList?category=166"
        await page.goto(list_url, wait_until="networkidle", timeout=90000)
        await asyncio.sleep(5)

        # 滚动加载更多文章
        for _ in range(4):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)

        # 提取文章链接（去重）
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

        # 进入每篇文章详情页
        for i, item in enumerate(links[:limit], 1):
            print(f"[{i}/{limit}] 抓取: {item['title'][:50]}...")

            try:
                # 打开详情页
                await page.goto(item['href'], wait_until="networkidle", timeout=30000)
                
                # 等待正文内容加载（增加等待时间，确保动态内容渲染）
                await asyncio.sleep(5) 

                # 提取正文，优先使用更精确的选择器
                content = await page.evaluate("""
                    () => {
                        // 更完善的选择器列表
                        const selectors = [
                            'article', 
                            '.article-content', 
                            '.content', 
                            '.rich-text', 
                            '.richText', 
                            '.main-content',
                            '.post-content',
                            'main'
                        ];
                        for (let sel of selectors) {
                            const el = document.querySelector(sel);
                            if (el) {
                                const text = el.innerText.trim();
                                if (text.length > 100) return text;
                            }
                        }
                        // 若特定容器未命中，则返回 body 文本，并尽可能去除杂音
                        let bodyText = document.body.innerText.trim();
                        return bodyText;
                    }
                """)

                articles.append({
                    "title": item['title'],
                    "link": item['href'],
                    "content": content.strip(),  # 全文保存，不做长度限制
                    "source": "动脉网"
                })
                print(f"   ✅ 成功，内容长度: {len(articles[-1]['content'])} 字符")

            except Exception as e:
                print(f"   ❌ 抓取失败: {e}")
                continue

        await browser.close()

    # 保存为 JSON 和 Markdown（全文）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"dongmai_full_{timestamp}"

    # 保存 JSON
    with open(f"data/reports/{filename}.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    # 保存 Markdown（取消截断限制）
    with open(f"data/reports/{filename}.md", "w", encoding="utf-8") as f:
        f.write(f"# 🏥 动脉网文章详情\n\n> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
        for i, a in enumerate(articles, 1):
            f.write(f"## {i}. {a['title']}\n\n")
            f.write(f"🔗 {a['link']}\n\n")
            f.write(f"{a['content']}\n\n")  # ✅ 此处不再截断，完整写入
            f.write("---\n\n")

    print(f"✅ 完成！共抓取 {len(articles)} 条完整文章（已保存全文）")
    return articles

async def main():
    await fetch_dongmai_full(limit=5)

if __name__ == "__main__":
    asyncio.run(main())