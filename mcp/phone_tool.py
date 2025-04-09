import requests
import json
import sys
from contextlib import AsyncExitStack
from openai import OpenAI

class PhoneTool:
    def __init__(self):
        self.api_url = "https://www.iamwawa.cn/home/shouji/ajax"
    
    def get_tool_schema(self):
        return {   "type" : "function",
            "function":{
                "name": "get_phoneno_info",
                "description": "获取手机号信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "phone_number": {
                            "type": "string",
                            "description": "手机号"
                        }
                    },
                    "required": ["phone_number"]
                }
            }
        }

    def get_phoneno_info(self,phone_number):
        url = "https://www.iamwawa.cn/home/shouji/ajax"
        payload = {"mob": phone_number}
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

        try:
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=4))
            return data.get("data", {})
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    #从参数中获取手机号
    phone_number = sys.argv[1]
    phone_info_tool = PhoneTool()
    phone_info_tool.get_phoneno_info(phone_number)
