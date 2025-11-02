"""
MCP Server with Streamable HTTP
================================

A basic MCP server with 2-3 tools including internet search capability.
Uses Google Custom Search API for web searches.

Author: Team
Version: 1.0.0
License: MIT
"""

import os
import sys
import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import httpx

# ------------------------------------------------------------------------------
# Boot
# ------------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s  %(message)s"
)
logger = logging.getLogger("mcp-server")

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
def _env_required(name: str) -> str:
    """Get required environment variable or raise error"""
    val = os.getenv(name, "").strip()
    if not val:
        raise RuntimeError(f"Missing required env var: {name}")
    return val

# ------------------------------------------------------------------------------
# Initialize FastMCP
# ------------------------------------------------------------------------------
mcp = FastMCP("Basic MCP Server (streamable-http)")

# ------------------------------------------------------------------------------
# TOOLS
# ------------------------------------------------------------------------------

@mcp.tool()
def get_time() -> Dict[str, Any]:
    """
    Get the current date and time.
    
    Returns:
        Dictionary with current date and time in ISO format.
    """
    try:
        now = datetime.now()
        return {
            "status": "success",
            "datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": str(now.astimezone().tzinfo)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
    
    Returns:
        Dictionary with the calculated result.
    """
    try:
        # Only allow basic math operations for safety
        allowed_chars = set("0123456789+-*/()., ")
        if not all(c in allowed_chars for c in expression):
            return {
                "status": "error",
                "error": "Expression contains invalid characters. Only basic math operations are allowed."
            }
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "status": "success",
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {"status": "error", "error": f"Calculation failed: {str(e)}"}


@mcp.tool()
async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the internet using Google Custom Search API.
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 5, max: 10)
    
    Returns:
        Dictionary with search results including title, link, and snippet for each result.
    """
    try:
        api_key = _env_required("GOOGLE_API_KEY")
        cse_id = _env_required("GOOGLE_CSE_ID")
    except RuntimeError as e:
        return {"status": "error", "error": str(e)}

    # Validate and limit num_results
    num_results = max(1, min(10, num_results))
    
    results: list = []
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": num_results
        }
        
        try:
            response = await client.get("https://www.googleapis.com/customsearch/v1", params=params)
            
            if response.status_code >= 300:
                return {
                    "status": "error",
                    "error": f"Google API returned {response.status_code}: {response.text[:400]}"
                }
            
            data = response.json()
            items = data.get("items", [])
            
            for item in items:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "displayLink": item.get("displayLink", "")
                })
            
            return {
                "status": "success",
                "query": query,
                "total": len(results),
                "results": results
            }
            
        except httpx.TimeoutException:
            return {"status": "error", "error": "Request timeout"}
        except Exception as e:
            return {"status": "error", "error": f"Search failed: {str(e)}"}


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Validate required environment variables
        try:
            _env_required("GOOGLE_API_KEY")
            _env_required("GOOGLE_CSE_ID")
            logger.info("✅ Environment variables validated")
        except RuntimeError as e:
            logger.warning(f"⚠️  {e}. Web search will not work without these.")
        
        logger.info("🚀 Starting MCP server (streamable-http)")
        logger.info("📡 Transport: streamable-http")
        logger.info("🔧 Available tools: get_time, calculate, web_search")
        
        mcp.run(transport="streamable-http")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

