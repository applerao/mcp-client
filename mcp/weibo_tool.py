import requests
import json

class WeiboTool:
    def get_weibo_hot_search(self):
        url = "https://weibo.com/ajax/statuses/mineBand"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
        }
        cookies = {
            "cookie": "XSRF-TOKEN=8FI1xYbMhlQDokqURjvJoCQF; SUB=_2AkMfUA1ff8NxqwFRmfETymPhaI5wyQHEieKpDPyEJRMxHRl-yT9kqndYtRB6NNAjsCSAfTHrdFA3F0OhQ6MeqDKAlJIv; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WW5RA8Nq4fRrolkUBIHO.4F; WBPSESS=voLfPs8eGy8pkyBjwwkfajA8taouxYxqW8dUf-qra-L49_wURVyWw2s1rHWzqRIHWZwTformLZ6BoGuT3fGFPfHzGrSPAo99baLekY3jNTFHiDr0f8tAEgjt1asJxvUZMR5hAaO9BWSZ6LmJe_tkx9xYml16blrDCprSlaEEI6o=" 
              # 替换为你的微博登录cookie
        }
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            result = response.json()
            if result['ok'] != 1:
                return {"error": "Failed to fetch data from Weibo"}
            # 提取热搜关键词
            words = []
            for item in result['data']['realtime']:
                words.append(item['word'])
            return words
        else:
            return {"error": f"Request failed with status code {response.status_code}"}

    def get_tool_schema(self):
        return {"type" : "function",
            "function":{
            "name": "get_weibo_hot_search",
            "description": "A tool to fetch Weibo hot search information.",
            "parameters": {
                    "type": "object",
                    "properties": {
                        
                    }
                }
        }}

if __name__ == "__main__":
    weibo_tool = WeiboTool()
    result = weibo_tool.get_weibo_hot_search()
    print(result)
