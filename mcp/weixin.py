import requests
from bs4 import BeautifulSoup

# 设置搜索关键词和公众号名称
search_url = "https://weixin.sogou.com/weixin?type=2&query=刘润"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 获取搜索结果页面
response = requests.get(search_url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# 提取文章链接
articles = []
for item in soup.select(".news-item"):
    title = item.select_one("h3").text.strip()
    link = item.select_one("a")["href"]
    articles.append({"title": title, "link": link})

# 输出最近的 100 篇文章
print(f"找到 {len(articles)} 篇文章")
for i, article in enumerate(articles[:100]):
    print(f"{i+1}. {article['title']} - {article['link']}")
