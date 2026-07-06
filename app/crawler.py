import requests
from datetime import datetime
import json
from bs4 import BeautifulSoup

def fetch_dongmai_articles():
    url = "https://www.vbdata.cn/articleList?category=166"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 提取文章标题（根据页面结构调整选择器）
        articles = []
        
        # 方法1：找所有 <a> 标签，标题在 <h2> 或 <h3> 里
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href = link["href"]
            if title and len(title) > 10 and "/article/" in href:
                articles.append({
                    "title": title,
                    "url": href if href.startswith("http") else "https://www.vbdata.cn" + href
                })
        
        # 如果上面的方法没找到，用这个方法：找所有带标题样式的元素
        if len(articles) == 0:
            for h2 in soup.find_all(["h2", "h3"]):
                title = h2.get_text(strip=True)
                if title and len(title) > 10:
                    # 找这个标题下面的链接
                    link = h2.find("a")
                    if link and link.get("href"):
                        href = link["href"]
                        articles.append({
                            "title": title,
                            "url": href if href.startswith("http") else "https://www.vbdata.cn" + href
                        })
        
        return {
            "source": "动脉网",
            "status": resp.status_code,
            "article_count": len(articles),
            "articles": articles[:10],  # 只取前10条
            "fetched_at": datetime.now().isoformat()
        }
    except Exception as e:
        return {"source": "动脉网", "error": str(e)}

if __name__ == "__main__":
    result = fetch_dongmai_articles()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 保存到文件
    filename = f"dongmai_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到: {filename}")