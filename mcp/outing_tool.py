import random

import json

class OutingTool:
    def __init__(self):
        with open('mcp/citycode.json', 'r') as f:
            city_data = json.load(f)
        self.cities = list(city_data['cities'].keys())

    def choose_cities(self, num=1):
        if num < 1:
            return []
        return random.choices(self.cities, k=num)

    def get_tool_schema(self):
        return { "type" : "function",
            "function":{
                "name": "choose_cities",
                "description": "获取随机的一个或多个城市去游玩",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num": {
                            "type": "integer",
                            "description": "Number of cities to choose"
                        }
                    },
                    "required": ["num"]
                }
            }
        }

if __name__ == "__main__":
    outing_tool = OutingTool()
    cities = outing_tool.choose_cities(3)  # Example usage of choose_cities method
    print(f"The chosen cities are: {', '.join(cities)}")
