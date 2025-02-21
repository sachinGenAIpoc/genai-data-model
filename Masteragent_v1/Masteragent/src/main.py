import os
import asyncio
async def main():
    # Initialize VertexDB client
    vertex_db_client = vertex_db_client(
        connection_string=os.getenv("VERTEX_DB_CONNECTION")
    )
    
    # Create multi-agent system
    multi_agent = multi_agent(vertex_db_client)
    
    # Process data
    result = await multi_agent.process()
    
    print("Processing complete")
    return result

if __name__ == "__main__":
    asyncio.run(main())