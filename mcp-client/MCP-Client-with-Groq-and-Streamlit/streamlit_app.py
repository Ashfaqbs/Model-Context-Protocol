"""
Streamlit App for MCP Client Interaction
=========================================

A basic Streamlit interface to interact with the MCP client using Groq.

USAGE:
    Run with: streamlit run streamlit_app.py
    NOT with: python streamlit_app.py

Author: Team
Version: 1.0.0
License: MIT
"""

import os
import sys
import asyncio
import streamlit as st
from typing import Optional
import logging

# Check if running directly (should use streamlit run instead)
if __name__ == "__main__" and "streamlit" not in sys.modules:
    print("\n" + "=" * 80)
    print("ERROR: This script must be run with Streamlit!")
    print("=" * 80)
    print("\nPlease use the following command:")
    print("  streamlit run streamlit_app.py")
    print("\nNOT:")
    print("  python streamlit_app.py")
    print("=" * 80 + "\n")
    sys.exit(1)

from dotenv import load_dotenv
from client import MCPClient, ClientConfig

# ------------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("streamlit_app")

# Page configuration
st.set_page_config(
    page_title="MCP Client Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------------------------
# Session State Initialization
# ------------------------------------------------------------------------------
if "client" not in st.session_state:
    st.session_state.client: Optional[MCPClient] = None
    st.session_state.connected = False
    st.session_state.messages = []
    st.session_state.tools_available = []

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
async def connect_client():
    """Connect to the MCP client"""
    if st.session_state.client is None:
        config = ClientConfig()
        client = MCPClient(config)
        try:
            with st.spinner("Connecting to MCP server and Groq..."):
                await client.connect()
            st.session_state.client = client
            st.session_state.connected = True
            st.session_state.tools_available = [tool.name for tool in client.tools]
            return True
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            return False
    return st.session_state.connected


async def get_response(query: str) -> dict:
    """Get response from the client"""
    if not st.session_state.connected:
        return {"status": "error", "message": "Client not connected"}
    
    try:
        response = await st.session_state.client.query(query)
        return response
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Configuration")
    
    st.subheader("Connection Status")
    if st.session_state.connected:
        st.success("✅ Connected")
        if st.session_state.tools_available:
            st.write("**Available Tools:**")
            for tool in st.session_state.tools_available:
                st.write(f"- {tool}")
    else:
        st.warning("❌ Not Connected")
    
    st.divider()
    
    # Connection button
    if st.button("🔄 Connect", use_container_width=True):
        if st.session_state.client is None or not st.session_state.connected:
            result = asyncio.run(connect_client())
            if result:
                st.success("Connected successfully!")
                st.rerun()
        else:
            st.info("Already connected")
    
    # Disconnect button
    if st.button("🔌 Disconnect", use_container_width=True):
        st.session_state.client = None
        st.session_state.connected = False
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.caption("**Environment Variables:**")
    st.caption("GROQ_API_KEY: " + ("✅ Set" if os.getenv("GROQ_API_KEY") else "❌ Missing"))
    st.caption("MCP_URL: " + (os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp") or "Not set"))
    st.caption("GOOGLE_API_KEY: " + ("✅ Set" if os.getenv("GOOGLE_API_KEY") else "❌ Missing"))
    st.caption("GOOGLE_CSE_ID: " + ("✅ Set" if os.getenv("GOOGLE_CSE_ID") else "❌ Missing"))
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------------------------
# Main Content
# ------------------------------------------------------------------------------
st.title("🤖 MCP Client Assistant")
st.markdown("Chat with your MCP-powered assistant using Groq LLM")

# Initialize connection on first load
if not st.session_state.connected:
    st.info("👆 Click 'Connect' in the sidebar to start chatting")
    if st.session_state.client is None:
        # Try to auto-connect
        with st.spinner("Attempting to connect..."):
            result = asyncio.run(connect_client())
            if result:
                st.success("Connected! You can start chatting now.")
                st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("steps"):
            with st.expander("🔍 View agent steps"):
                for i, step in enumerate(message["steps"], 1):
                    st.write(f"**Step {i}:**")
                    st.json(step)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    if not st.session_state.connected:
        st.warning("Please connect to the MCP server first!")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = asyncio.run(get_response(prompt))
            
            if response["status"] == "success":
                assistant_response = response.get("response", "No response received")
                st.markdown(assistant_response)
                
                # Show intermediate steps if available
                intermediate_steps = response.get("intermediate_steps", [])
                if intermediate_steps:
                    with st.expander("🔍 View agent steps"):
                        for i, step in enumerate(intermediate_steps, 1):
                            st.write(f"**Step {i}:**")
                            st.json(step)
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "steps": intermediate_steps
                })
            else:
                error_msg = response.get("message", "Unknown error occurred")
                st.error(f"Error: {error_msg}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {error_msg}"
                })

# Footer
st.divider()
st.caption("💡 **Tips:**")
st.caption("- Make sure the MCP server is running before connecting")
st.caption("- Use 'web_search' to search the internet")
st.caption("- Use 'get_time' to get current time")
st.caption("- Use 'calculate' for math operations")

