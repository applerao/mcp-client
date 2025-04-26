from dotenv import load_dotenv
load_dotenv()

import asyncio
from mcp import ClientSession
from contextlib import AsyncExitStack
import os,sys
from openai import OpenAI
#导入mcp目录的phone-tool.py文件
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp'))
from local_phone_tool import PhoneTool
from weather_tool import WeatherTool
from outing_tool import OutingTool
from budget_tool import BudgetTool
from weibo_tool import WeiboTool  # 导入WeiboTool类
from mcp_service_tool import MCPServiceTool
import json

class MPCClient:
    def __init__(self):
        '''init mcp client'''
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.api_key=os.getenv('api_key')
        phone_tool = PhoneTool()
        weather_tool = WeatherTool()
        outing_tool = OutingTool()

        budget_tool = BudgetTool()
        weibo_tool = WeiboTool()  # 实例化WeiboTool类

        self.tools = []
        self.tools.append(phone_tool.get_tool_schema())
        self.tools.append(weather_tool.get_tool_schema())
        self.tools.append(outing_tool.get_tool_schema())
        self.tools.append(budget_tool.get_tool_schema())
        self.tools.append(weibo_tool.get_tool_schema())  # 添加WeiboTool的schema
        
        self.tool_mapping={
            "get_phoneno_info": phone_tool.get_phoneno_info,
            "get_weather_info": weather_tool.get_weather_info,
            "choose_cities": outing_tool.choose_cities,
            "gaussian_budget_allocation": budget_tool.gaussian_budget_allocation,
            "get_weibo_hot_search": weibo_tool.get_weibo_hot_search,  # 添加WeiboTool的方法映射
        }

        self.mcp_service_tool = MCPServiceTool()
        self.mcp_tool_mapping = {}
        self.base_url = os.getenv('base_url')
        self.model = os.getenv('model')
        self.client = OpenAI(api_key=self.api_key,base_url=self.base_url)
        self.chat_history = []
        self.chat_history.append({"role": "system", "content": "You are a helpful assistant."})

    def call_mcp_service(self, service_name, **kwargs):
        # Simulate calling an MCP service
        print(f"Calling MCP service {service_name} with arguments {kwargs}")
        return {"status": "success", "response": "Simulated MCP service response"}

    def summarize_chat_history(self, chat_history):
        # Simple summarization: Keep only the last 3 messages
        return chat_history[-3:]

    async def connect_to_server(self):
        # Code to connect to server goes here
        '''connect to mcp server'''
        print("Connecting to server...")
        
        tools = await self.mcp_service_tool.get_tool_schema()
        for tool in tools:
            # Convert each tool to the function format
            self.mcp_tool_mapping[tool['function']['name']] = self.mcp_service_tool.call_tool
        self.tools.extend(tools)
        print(self.tools)
        print(self.mcp_tool_mapping)
        pass
    
    async def chat_loop(self):
        print("Starting chat loop...")
        while True:
            # Simulate chat input
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Exiting chat...")
                break
            else:
                response = await self.query(user_input)
                print(f"Assistant: {response}")
        # Simulate server response
        # In a real implementation, this would be replaced with actual server communication
        pass

    async def query(self, input_text):
        '''query mcp server'''
        answer = None
        if input_text:
            self.chat_history.append({"role": "user", "content": input_text})
        
        # Summarize chat history to reduce token usage
        #summarized_chat_history = self.summarize_chat_history(self.chat_history)
        
        # Pass the tools and summarized chat history to the chat completions create method
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
                print(f"Tool name: {tool_name}")
                print(f"Function arguments: {function_args}")

                # 自动选择并执行对应的函数
                function_response = None
                if tool_name in self.tool_mapping:
                    function_response = self.tool_mapping[tool_name](**function_args)
                elif tool_name in self.mcp_tool_mapping:
                    function_response = await self.mcp_service_tool.call_tool(tool_name,function_args)
                else:
                    print(f"Unknown tool: {tool_name}")
                if function_response is not None:
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
            answer = await self.query(None)
        else:
            answer = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": answer})
        return answer



async def main():
    mcp_client = MPCClient()
    await mcp_client.connect_to_server()
    await mcp_client.chat_loop()
    print("Hello from mcp-client!")


if __name__ == "__main__":
    asyncio.run(main())
