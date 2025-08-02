from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


load_dotenv()

llm = ChatOpenAI(model="gpt-4o", streaming=True)

async def process_stream(stream_generator):
    results = []
    try:
        async for chunk in stream_generator:    #속도 향상을 위해 처리함. 

            key = list(chunk.keys())[0]
            
            if key == 'agent':
                # Agent 메시지의 내용을 가져옴. 메세지가 비어있는 경우 어떤 도구를 어떻게 호출할지 정보를 가져옴
                content = chunk['agent']['messages'][0].content if chunk['agent']['messages'][0].content != '' else chunk['agent']['messages'][0].additional_kwargs
                print(f"'agent': '{content}'")
            
            elif key == 'tools':
                # 도구 메시지의 내용을 가져옴
                for tool_msg in chunk['tools']['messages']:
                    print(f"'tools': '{tool_msg.content}'")
            
            results.append(chunk)
        return results
    except Exception as e:
        print(f"Error processing stream: {e}")
        return results
    
    
    
async def main():
    client = MultiServerMCPClient(
        {
            "test": {
                "command": "python",
                "args": ["./mcp_server.py"],  # 여기에 절대 경로를 넣는 것이 좋습니다.
                "transport": "stdio",
            },
        }
    )
    tools = await client.get_tools()    
    agent = create_react_agent(llm, tools)
    print("==========RESPONSE===========")
    stream_generator = agent.astream({"messages": "연봉 5천만원 거주자의 소득세는 얼마인가요?"})
       
    all_chunks = await process_stream(stream_generator)

    if all_chunks:
        final_result = all_chunks[-1]
        print("\nFinal result:", final_result)
        
        
if __name__ == "__main__":
    asyncio.run(main())