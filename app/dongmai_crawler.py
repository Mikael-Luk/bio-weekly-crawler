import requests
import json
import time

def fetch_dongmai_intel():
    url = "https://app.vbdata.cn/api/mi/list"
    
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.vbdata.cn",
        "Referer": "https://www.vbdata.cn/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.2 Safari/605.1.15",
        "platform": "PC",
        "timestamp": str(int(time.time() * 1000)),
    }
    
    payload = {
        "itrackTags": [],
        "contentTags": [],
        "domestic": None,
        "days": None,
        "groupAllTags": "",
        "groupAllComps": "",
        "groupAllOrgs": "",
        "yzGroup1": "",
        "yzGroup2": "",
        "yzGroup3": "",
        "yzGroup4": "",
        "yzGroup5": "",
        "myGroupId": "",
        "page": 1,
        "topCreateTime": "",
        "size": 10,
        "getCount": False,
        "startTime": "",
        "endTime": "",
        "selected": None,
        "keyword": "",
        "uUserId": None,
        "uUid": "EDAC505F-D30D-4B2F-9C36-AA53B59F0A93-1782703765049"
    }
    
    try:
        headers["sign"] = "56a8161dc02e0401aa36d904fefd7a05"
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        print("状态码:", resp.status_code)
        print("返回内容:", resp.text[:500])
        if resp.status_code == 200:
            data = resp.json()
            return {
                "source": "动脉网-情报",
                "code": data.get("code"),
                "msg": data.get("msg"),
                "data": data.get("data"),
                "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {"source": "动脉网-情报", "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"source": "动脉网-情报", "error": str(e)}

if __name__ == "__main__":
    result = fetch_dongmai_intel()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    filename = f"dongmai_intel_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到: {filename}")