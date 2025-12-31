"""
MCP client for connecting to Logos MCP server.

This client makes HTTP requests to the Logos MCP server to access
memory and personality functionality.
"""

import json
from typing import Dict, Any, Optional
import httpx


class LogosMCPClient:
    """Client for connecting to Logos MCP server."""

    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.client = httpx.Client(timeout=30.0)

    def _call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call an MCP tool via HTTP."""
        url = f"{self.server_url}/tools/{tool_name}"

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs
            }
        }

        try:
            response = self.client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                return {"error": result["error"]["message"]}

            return result.get("result", {})

        except httpx.RequestError as e:
            return {"error": f"Request failed: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    def query_logos(self, question: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query Logos for relevant context.

        Args:
            question: The question to ask
            limit: Maximum results per collection

        Returns:
            Dictionary containing constitution, memories, and metadata
        """
        result = self._call_tool("query_logos", question=question, limit=limit)

        if "error" in result:
            return result

        # Parse the JSON response
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Invalid response format from Logos server"}

    def get_constitution(self) -> str:
        """
        Get Logos' personality constitution.

        Returns:
            Constitution text
        """
        result = self._call_tool("get_constitution")
        return result if isinstance(result, str) else str(result)

    def get_memory_context(self, question: str, collection: str = "both", limit: int = 5) -> Dict[str, Any]:
        """
        Get memory context for a question.

        Args:
            question: Question to search for
            collection: Collection to search ("essence", "project", or "both")
            limit: Maximum results

        Returns:
            Dictionary with memories and metadata
        """
        result = self._call_tool("get_memory_context",
                               question=question,
                               collection=collection,
                               limit=limit)

        if "error" in result:
            return result

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Invalid response format from Logos server"}

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory collections.

        Returns:
            Dictionary with collection statistics
        """
        result = self._call_tool("get_collection_stats")

        if "error" in result:
            return result

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Invalid response format from Logos server"}

    def __del__(self):
        """Clean up HTTP client."""
        if hasattr(self, 'client'):
            self.client.close()