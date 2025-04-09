from dotenv import load_dotenv
load_dotenv()

import asyncio
from mcp import ClientSession
from contextlib import AsyncExitStack
import os,sys
from openai import OpenAI
#导入mcp目录的phone-tool.py文件
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp'))
from phone_tool import PhoneTool
from weather_tool import WeatherTool
import json

class MPCClient:
    def __init__(self):
        '''init mcp client'''
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.api_key=os.getenv('api_key')
        phone_tool = PhoneTool()
        weather_tool = WeatherTool()
        self.tools = []
        self.tools.append(phone_tool.get_tool_schema())
        self.tools.append(weather_tool.get_tool_schema())
        self.tool_mapping={
            "get_phoneno_info": phone_tool.get_phoneno_info,
            "get_weather_info": weather_tool.get_weather_info
        }
        self.base_url = os.getenv('base_url')
        self.model = os.getenv('model')
        self.client = OpenAI(api_key=self.api_key,base_url=self.base_url)
        self.chat_history = []
        self.chat_history.append({"role": "system", "content": "You are a helpful assistant."})
    
    def connect_to_server(self):
        # Code to connect to server goes here
        '''connect to mcp server'''
        print("Connecting to server...")
        pass
    
    def chat_loop(self):
        print("Starting chat loop...")
        while True:
            # Simulate chat input
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting chat...")
                break
            else:
                response = self.query(user_input)
                print(f"Assistant: {response}")
        # Simulate server response
        # In a real implementation, this would be replaced with actual server communication
        pass

    def query(self, input_text):
        '''query mcp server'''
        answer = None
        if input_text:
            self.chat_history.append({"role": "user", "content": input_text})

        # Pass the tools to the chat completions create method
        response = self.client.chat.completions.create(
            model="qwen-plus",
            temperature=1.0,
            n=1,
            messages=self.chat_history,
            tools=self.tools
        )

        # Use the tool_calls from the response to determine which tool was called
        self.chat_history.append(response.choices[0].message)
        # Check if the response contains a tool call
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls != None:
            for tool_call in tool_calls:
                # 处理函数调用
                tool_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                print(f"Function arguments: {function_args}")

                # 自动选择并执行对应的函数
                if tool_name in self.tool_mapping:
                    function_response = self.tool_mapping[tool_name](**function_args)
                    # 将函数响应添加到消息中
                    self.chat_history.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(function_response),
                        }
                    )
                    print(f"Function response: {function_response}")
                else:
                    print(f"Unknown tool: {tool_name}")
            answer = self.query(None)
        else:
            answer = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": answer})
        return answer



def main():
    client = MPCClient()
    client.connect_to_server()
    client.chat_loop()
    print("Hello from mcp-client!")


if __name__ == "__main__":
    main()
