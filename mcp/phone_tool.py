from mcp.server import FastMCP
import sys
import json
import requests
import httpx
import asyncio

app = FastMCP('phone-search', port=9000)


@app.tool()
async def get_phoneno_info(phone_number):
    """
    获取手机号信息

    Args:
        phone_number (str): 手机号

    Returns:
        dict: 手机号信息
    """
    api_url = "https://www.iamwawa.cn/home/shouji/ajax"
    payload = {"mob": phone_number}
    headers = {"Content-Type": "application/x-www-form-urlencoded",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    try:
        async with httpx.AsyncClient() as client:
            response = requests.post(api_url, data=payload, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=4))
            return data.get("data", {})
    except requests.exceptions.RequestException as e:
        return {"error": f"请求失败: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON解析失败: {e}"}
    except Exception as e:
        return {"error": f"发生错误: {e}"}
    
async def main():
    #从参数中获取手机号
    phone_number = sys.argv[1]
    result = await get_phoneno_info(phone_number)
    print(json.dumps(result, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    asyncio.run(main())
    app.run(transport='sse')