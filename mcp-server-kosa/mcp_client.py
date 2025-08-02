from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio 
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", streaming=True)

async def main():
    client = MultiServerMCPClient(
    {
        "math": {       #remote로 tool에(server) 접근해서 읽어옴
            "command": "python",
            "args": ["./mcp_server.py"],
            "transport": "stdio",
        },
    }
    )       
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    response = await agent.ainvoke({"messages": "연봉 5천만원 거주자의 소득세는 얼마인가요?"})
    print(response)
    
    # final_message = response['messages'][-1]
    # print(f"Final messages: {final_message.content}")
    
if __name__ == "__main__":
    asyncio.run(main())
# This code is a client that connects to a server running the MCP (Multi-Client Protocol