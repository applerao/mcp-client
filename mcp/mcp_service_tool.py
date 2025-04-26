import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import Tool,CallToolResult

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()  # load environment variables from .env

class MCPServiceTool:
    def __init__(self):
        with open('mcp/mcptool.json', 'r') as f:
            self.mcp_config = json.load(f)
        self.client_sessions = {}
        with open('mcp/mcptool.json', 'r') as f:
            self.mcp_config = json.load(f)
        self.client_sessions = {}
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.tools = []

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        if response.tools is None:
            raise ValueError("No tools available from the MCP service.")
        else:
            self.tools.extend(response.tools)

    def convert_to_function_format(self, tool: Tool):
        """
        将工具定义转换为指定的 JSON 格式。

        :param tool_name: 工具名称
        :param tool_description: 工具描述
        :param input_schema: 输入参数的 JSON Schema
        :return: 转换后的 JSON 格式
        """
        function_schema = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": json.loads(json.dumps(tool.inputSchema))
            }
        }
        return function_schema

    async def get_tool_schema(self):
        """Get the tool schema for the MCP service"""
        mcp_server = self.mcp_config.get('mcp_servers',None)
        if mcp_server is None:
            raise ValueError("No MCP server configuration found.")
        else:  
            print(mcp_server)
            for server_name,url_config in mcp_server.items():
                print(f"Connecting to {server_name} at {url_config['url']}")
                # Connect to the server
                await self.connect_to_sse_server(url_config['url'])
        # Iterate through the MCP servers and load their configurations
        
        if self.tools is None:
            raise ValueError("No tools available from the MCP service.")
        # Convert each tool to the function format
        function_schemas = []
        for tool in self.tools:
            function_schemas.append(self.convert_to_function_format(tool))
        return function_schemas

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None)

    async def call_tool(self, tool_name: str, arguments):
        """Call a tool using the MCP service"""
        print(f"Calling tool {tool_name} with arguments {arguments}")
        if tool_name not in [tool.name for tool in self.tools]:
            raise ValueError(f"Tool {tool_name} is not available.")
        
        # Call the tool with the provided arguments
        print(type(arguments))
        response = await self.session.call_tool(tool_name, arguments)
        print(f"Calling tool result is {response}")
        # Check for errors in the response
        if response.isError:
            raise ValueError(f"Error calling tool {tool_name}: {response.error}")
        if response.content is not None and response.content[0].type == 'text':
            print(f"Tool {tool_name} response: {response.content[0].text}")
            return response.content[0].text
        return '{}'

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                    "role": "assistant",
                    "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <URL of SSE MCP server (i.e. http://localhost:8080/sse)>")
        sys.exit(1)

    client = MCPServiceTool()
    try:
        await client.connect_to_sse_server(server_url=sys.argv[1])
        #await client.chat_loop()
        await client.call_tool('maps_ip_location',{'ip': '110.242.68.66'})
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    print(sys.argv[1])
    asyncio.run(main())
