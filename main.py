from dotenv import load_dotenv
load_dotenv()

import asyncio
from mcp import ClientSession
from contextlib import AsyncExitStack
import os
from openai import OpenAI

class MPCClient:
    def __init__(self):
        '''init mcp client'''
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.api_key=os.getenv('api_key')
        print(self.api_key)
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
        # Chat loop implementation goes here
        '''chat loop'''
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

    def query(self,input_text):
        '''query mcp server'''
        self.chat_history.append({"role": "user", "content": input_text})
        response = self.client.chat.completions.create(model="qwen-plus",
        temperature=1.0,
        n=1,
        messages=self.chat_history)
        answer = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": answer})
        return answer



def main():
    client = MPCClient()
    client.connect_to_server()
    client.chat_loop()
    print("Hello from mcp-client!")


if __name__ == "__main__":
    asyncio.run(main())
