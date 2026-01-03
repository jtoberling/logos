"""
Simple MCP Integration Test - KISS Edition

The most basic integration test possible:
1. Connect to running MCP server in Docker
2. Call get_constitution tool
3. Verify response is not empty

That's it. Simple validation that the system works end-to-end.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, '/usr/src/logos/src')

async def simple_mcp_test():
    """Simplest possible MCP integration test."""
    print("🧪 SIMPLE MCP INTEGRATION TEST")
    print("=" * 30)

    try:
        # Import FastMCP client
        from fastmcp import Client
        print("✅ FastMCP client imported")

        # Connect to MCP server (using Docker service name)
        async with Client('http://logos-mcp:6335/mcp') as client:
            print("✅ Connected to MCP server")

            # Call simplest tool
            result = await client.call_tool('get_constitution', {})
            print("✅ get_constitution tool called successfully")

            # Basic validation
            if result and len(str(result)) > 50:
                print("✅ Constitution received (length > 50 chars)")
                print(f"   Preview: {str(result)[:100]}...")
                return True
            else:
                print(f"❌ Constitution too short or empty: {result}")
                return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Running simple MCP integration test...")
    success = asyncio.run(simple_mcp_test())

    if success:
        print("\n🎉 SUCCESS: MCP integration test passed!")
        print("✅ System is working end-to-end")
        exit(0)
    else:
        print("\n❌ FAILED: MCP integration test failed")
        exit(1)