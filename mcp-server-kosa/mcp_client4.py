import time
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
llm = ChatOpenAI(model="gpt-4o", streaming=True)

# ✅ MCP 클라이언트 초기화
async def setup_tools():
    client = MultiServerMCPClient({
        "test": {
            "command": "python",
            "args": ["./mcp_server.py"],
            "transport": "stdio",
        }
    })
    return await client.get_tools()

# ✅ 스트림 처리 with 타이밍 출력
async def process_stream(stream_generator):
    results = []
    try:
        start_time = time.time()

        async for chunk in stream_generator:
            elapsed = time.time() - start_time
            print(f"⏱️ {elapsed:.2f}s - received chunk")

            key = list(chunk.keys())[0]

            if key == 'agent':
                msg = chunk['agent']['messages'][0]
                content = msg.content if msg.content else msg.additional_kwargs
                print(f"[agent] {content}")

            elif key == 'tools':
                for msg in chunk['tools']['messages']:
                    print(f"[tools] {msg.content}")

            results.append(chunk)

        total = time.time() - start_time
        print(f"\n✅ Total processing time: {total:.2f} seconds")
        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return results

# ✅ 에이전트 구성
def create_agent(tools):
    return create_react_agent(llm, tools)

# ✅ 메인 실행 함수
async def main():
    tools = await setup_tools()
    agent = create_agent(tools)

    print("==========RESPONSE===========")
    stream = agent.astream(
        {"messages": [HumanMessage(content="연봉 5천만원 거주자의 소득세는 얼마인가요?")]},
        config={"step_limit": 3}  # ✅ 반복 제한
    )

    chunks = await process_stream(stream)

    if chunks:
        final_result = chunks[-1]
        print("\n📌 Final result:", final_result)

if __name__ == "__main__":
    asyncio.run(main())
