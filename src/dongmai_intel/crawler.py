#!/usr/bin/env python3
"""
动脉网情报列表爬虫 - 过滤页脚版
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def fetch_dongmai_intel():
    print("🚀 启动动脉网情报列表爬虫...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://www.vbdata.cn/intelList"
        print(f"🔍 加载: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=90000)
            print("✅ 页面加载完成")
            await asyncio.sleep(5)
            
            # 滚动加载更多
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(3)
            
            # 提取情报（按行解析 + 过滤页脚）
            items = await page.evaluate("""
                () => {
                    // 1. 先移除页脚和导航等无关区域
                    const excludeSelectors = [
                        'footer', '.footer', '.page-footer',
                        '.header', '.navigation', '.nav', '.menu',
                        '.sidebar', '.copyright',
                        '.footer-links', '.friend-links',
                        '.友情链接', '.关于我们', '.产品服务'
                    ];
                    excludeSelectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => el.remove());
                    });
                    
                    // 2. 获取剩余文本
                    const bodyText = document.body.innerText;
                    const lines = bodyText.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    
                    // 3. 定义要过滤的页脚关键词
                    const footerKeywords = [
                        '©', '渝ICP备', '渝公网安备', '互联网药品信息服务资格证书',
                        '友情链接', '关于我们', '联系我们', '加入我们', '意见反馈',
                        '产品服务', '商务合作', '动脉网APP', '全球产业链接平台',
                        '联系电话', '重庆市渝北区', '版权所有', 'ICP备案',
                        '用户协议', '隐私政策', '免责声明', '技术支持'
                    ];
                    
                    const items = [];
                    let current = null;
                    
                    for (const line of lines) {
                        // 跳过页脚行
                        let isFooter = false;
                        for (const keyword of footerKeywords) {
                            if (line.includes(keyword)) {
                                isFooter = true;
                                break;
                            }
                        }
                        if (isFooter) continue;
                        
                        // 检测时间标记
                        if (/^\\d{1,2}:\\d{2}$/.test(line) || /^\\d{4}年\\d{2}月\\d{2}日/.test(line)) {
                            if (current && current.title) {
                                items.push(current);
                            }
                            current = {
                                time: line,
                                title: '',
                                content: ''
                            };
                        } else if (current) {
                            // 判断标题
                            const isTitle = line.startsWith('#') || 
                                (line.length > 10 && line.length < 80 && 
                                 !line.includes('，') && !line.includes('。') && 
                                 !line.includes('、') && !line.includes('：') &&
                                 !line.includes('来源') && !line.includes('发布') &&
                                 !line.includes('等信源发布'));
                            
                            if (isTitle && !current.title) {
                                current.title = line.replace(/^#\\s*/, '').trim();
                            } else {
                                current.content += line + '\\n';
                            }
                        }
                    }
                    
                    if (current && current.title) {
                        items.push(current);
                    }
                    
                    return items;
                }
            """)
            
            print(f"📰 提取到 {len(items)} 条情报")
            
            # 保存 Markdown
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dongmai_intel_{timestamp}"
            
            with open(f"data/reports/{filename}.md", "w", encoding="utf-8") as f:
                f.write(f"# 🏥 动脉网情报列表\n\n")
                f.write(f"> 抓取时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
                f.write(f"> 共 {len(items)} 条情报\n\n")
                f.write("---\n\n")
                
                for i, item in enumerate(items, 1):
                    f.write(f"## {i}. {item['title']}\n\n")
                    if item['time']:
                        f.write(f"🕐 {item['time']}\n\n")
                    # 清理内容中的多余空白
                    content = item['content'].strip()
                    # 删除内容末尾可能残留的页脚
                    for keyword in ['©', '渝ICP备', '友情链接', '关于我们', '联系电话']:
                        if keyword in content:
                            content = content.split(keyword)[0].strip()
                    f.write(f"{content}\n\n")
                    f.write("---\n\n")
            
            print(f"✅ 保存成功: data/reports/{filename}.md")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

async def main():
    await fetch_dongmai_intel()

if __name__ == "__main__":
    asyncio.run(main())