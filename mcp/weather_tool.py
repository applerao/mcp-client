import requests
import json
import sys

class WeatherTool:
    def __init__(self):
        # 从 citycode.json 文件加载城市代码和城市名称的字典
        with open('mcp/citycode.json', 'r', encoding='utf-8') as file:
            city_data = json.load(file)
            self.city_codes = city_data.get("cities", {})
            self.area_codes = city_data.get("areas", {})
            self.province_codes = city_data.get("provinces", {})
        self.api_url = "http://t.weather.sojson.com/api/weather/city/"
    def get_tool_schema(self):
        return {
            "type": "function",
            "function": {
                "name": "get_weather_info",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city_name": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city_name"]
                }
            }
        }

    def get_weather_info(self, city_name):
        city_code = self.city_codes.get(city_name)
        if city_code is None:
            # 如果城市名称不在 city_codes 中，则尝试在 area_codes 中查找
            city_code = self.area_codes.get(city_name)
        if city_code is None:
            # 如果城市名称不在 area_codes 中，则尝试在 province_codes 中查找
            city_code = self.province_codes.get(city_name)
        if city_code is None:
            # 如果城市名称不在 province_codes 中，则返回错误信息
            # 这里可以添加一些提示信息，告诉用户如何使用
            # 例如：print("请检查城市名称是否正确")
            print(f"未知的城市名称: {city_name}")
            return
        url = f"{self.api_url}{city_code}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=4))
            return data
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
        except Exception as e:
            print(f"发生错误: {e}")

if __name__ == "__main__":
    #从参数中获取城市名称
    city_name = sys.argv[1]
    weather_tool = WeatherTool()
    weather_tool.get_weather_info(city_name)
