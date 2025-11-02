"""
MCP Client using Groq
=====================

A LangChain ReAct client that connects to an MCP server using Groq LLM.

Author: Team
Version: 1.0.0
License: MIT
"""

import os
import asyncio
import json
import logging
import warnings
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime

from dotenv import load_dotenv

# LangChain core
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

# LangGraph for agents
from langgraph.prebuilt import create_react_agent

# Groq (LangChain integration)
from langchain_groq import ChatGroq

# MCP client
from langchain_mcp_adapters.client import MultiServerMCPClient

# --------------------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------------------
warnings.filterwarnings("ignore", category=DeprecationWarning)
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("mcp_client")

# Enable verbose logging for LangChain components
logging.getLogger("langchain").setLevel(logging.INFO)
logging.getLogger("langgraph").setLevel(logging.INFO)
logging.getLogger("langchain_core").setLevel(logging.INFO)

# --------------------------------------------------------------------------------------
# Custom Callback Handler for Real-time Logging
# --------------------------------------------------------------------------------------
class VerboseCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to log agent reasoning, tool calls, and decisions in real-time"""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
        self.step_count = 0
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts running"""
        if self.verbose:
            self.step_count += 1
            logger.info("=" * 80)
            logger.info(f"🤔 STEP {self.step_count}: LLM Thinking...")
            logger.info("=" * 80)
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM finishes running"""
        if self.verbose:
            logger.info("✅ LLM Response Complete")
            
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error"""
        if self.verbose:
            logger.error(f"❌ LLM Error: {error}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts running"""
        if self.verbose:
            tool_name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
            # Format input nicely - try to parse as dict if it's JSON-like
            input_display = input_str
            try:
                if isinstance(input_str, str) and (input_str.startswith("{") or input_str.startswith("[")):
                    parsed = json.loads(input_str)
                    input_display = json.dumps(parsed, indent=2)
            except:
                pass
            logger.info("-" * 80)
            logger.info(f"🔧 TOOL CALL: {tool_name}")
            logger.info(f"📥 Input:")
            logger.info(input_display)
            logger.info("-" * 80)
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes running"""
        if self.verbose:
            # Truncate long outputs for readability
            output_preview = output[:500] + "..." if len(output) > 500 else output
            logger.info(f"📤 Tool Output: {output_preview}")
            logger.info("-" * 80)
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when a tool encounters an error"""
        if self.verbose:
            logger.error(f"❌ Tool Error: {error}")
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain starts running"""
        if self.verbose:
            chain_name = serialized.get("name", serialized.get("id", ["unknown"])[-1])
            logger.info(f"🔄 Chain Started: {chain_name}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain ends"""
        if self.verbose:
            logger.info("✅ Chain Completed")
    
    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """Called when a chain encounters an error"""
        if self.verbose:
            logger.error(f"❌ Chain Error: {error}")


# --------------------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------------------
@dataclass
class ClientConfig:
    """Configuration for the MCP client (Groq + MCP)"""

    # Groq API Key
    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()

    # Groq model
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # MCP Server URL
    mcp_url: str = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

    # Agent settings
    max_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "6"))
    agent_timeout: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "90"))
    memory_window_size: int = int(os.getenv("MEMORY_WINDOW_SIZE", "8"))
    connect_timeout: int = int(os.getenv("MCP_CONNECT_TIMEOUT", "12"))
    verbose: bool = os.getenv("VERBOSE_LOGGING", "true").lower() == "true"


# --------------------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------------------
class MCPClient:
    """MCP client using Groq + LangChain ReAct + MCP tools"""

    def __init__(self, config: ClientConfig):
        self.config = config
        self.llm: Optional[ChatGroq] = None
        self.mcp: Optional[MultiServerMCPClient] = None
        self.agent = None
        self.memory: Optional[ConversationBufferWindowMemory] = None
        self.tools: List[Tool] = []
        self.callback_handler = VerboseCallbackHandler(verbose=config.verbose)

    async def connect(self):
        """Connect to Groq and MCP server, build agent + tools"""
        try:
            # Validate Groq config
            if not self.config.groq_api_key:
                raise RuntimeError(
                    "GROQ_API_KEY is missing. Set environment variable GROQ_API_KEY."
                )

            # Init Groq LLM with callbacks for verbose logging
            self.llm_base = ChatGroq(
                groq_api_key=self.config.groq_api_key,
                model=self.config.groq_model,
                temperature=0.1,
                max_tokens=None,
                timeout=self.config.agent_timeout,
                callbacks=[self.callback_handler] if self.config.verbose else None,
            )

            # Init memory
            self.memory = ConversationBufferWindowMemory(
                k=self.config.memory_window_size,
                memory_key="chat_history",
                return_messages=True,
                output_key="output",
            )

            # Init MCP client
            self.mcp = MultiServerMCPClient(
                {
                    "mcp-server": {
                        "url": self.config.mcp_url,
                        "transport": "streamable_http",
                    }
                }
            )

            if hasattr(self.mcp, "start"):
                await asyncio.wait_for(self.mcp.start(), timeout=self.config.connect_timeout)

            # Load MCP tools (they're already LangChain-compatible)
            base_tools = await asyncio.wait_for(
                self.mcp.get_tools(), timeout=self.config.connect_timeout
            )
            self.tools = list(base_tools)
            
            # Use the base LLM (LangGraph will handle tool binding internally)
            self.llm = self.llm_base

            # Custom system prompt
            system_prompt = f"""You are a helpful Assistant with access to tools.

Available tools: {', '.join([tool.name for tool in self.tools])}

Current date: {datetime.now().strftime("%Y-%m-%d")}

When using tools:
- For get_time: call with no arguments
- For calculate: provide the mathematical expression as a string
- For web_search: provide the search query as a string, optionally specify num_results (default: 5)

Use tools when needed to answer questions accurately."""

            # Create ReAct agent using LangGraph
            try:
                self.agent = create_react_agent(
                    self.llm, 
                    self.tools, 
                    messages_modifier=system_prompt
                )
            except TypeError:
                try:
                    self.agent = create_react_agent(
                        self.llm, 
                        self.tools, 
                        state_modifier=system_prompt
                    )
                except TypeError:
                    self.agent = create_react_agent(
                        self.llm, 
                        self.tools, 
                        prompt=system_prompt
                    )

            logger.info("MCP Client connected successfully!")
            logger.info(f"  - Tools loaded: {len(self.tools)}")
            if self.config.verbose:
                logger.info("  - Verbose logging: ENABLED")
                logger.info("  - Real-time execution tracing: ENABLED")
                logger.info("")
                logger.info("📋 Available Tools:")
                for tool in self.tools:
                    logger.info(f"   • {tool.name}: {getattr(tool, 'description', 'No description')[:80]}")
                logger.info("")

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise RuntimeError(f"Failed to connect client: {str(e)}")


    async def query(self, query: str) -> Dict[str, Any]:
        """Run a query through the agent with verbose logging"""
        if not self.agent:
            raise RuntimeError("Client not connected. Call connect() first.")

        try:
            # Quick guard for salutations
            if query.lower().strip() in {"hi", "hello", "hey", "hi there"}:
                return {
                    "status": "success",
                    "response": (
                        "Hello! I'm your Assistant. I can help you search the internet, "
                        "get the current time, perform calculations, and more. "
                        "What would you like to know?"
                    ),
                    "intermediate_steps": [],
                }

            # Log query start
            logger.info("")
            logger.info("🚀" + "=" * 79)
            logger.info(f"📝 USER QUERY: {query}")
            logger.info("🚀" + "=" * 79)
            logger.info("")

            # Build messages from memory and current query
            messages = []
            if self.memory and hasattr(self.memory, 'buffer') and self.memory.buffer:
                messages.extend(self.memory.buffer[-self.config.memory_window_size:])
                if self.config.verbose:
                    logger.info(f"💭 Using {len(messages)} previous messages from memory")
            messages.append(HumanMessage(content=query))

            # Invoke the agent with streaming to see intermediate steps
            if self.config.verbose:
                logger.info("🤖 Starting agent execution...")
                logger.info("")

            # Stream the agent execution to see intermediate steps in real-time
            intermediate_steps = []
            response_text = ""
            final_messages = []
            
            # Use astream for real-time streaming of agent execution
            async for chunk in self.agent.astream({"messages": messages}, config={"callbacks": [self.callback_handler]}):
                if self.config.verbose:
                    # Log each chunk as it comes
                    for node_name, node_output in chunk.items():
                        if node_name == "agent":
                            # Agent is thinking/deciding
                            agent_messages = node_output.get("messages", [])
                            final_messages.extend(agent_messages)
                            for msg in agent_messages:
                                if isinstance(msg, AIMessage):
                                    content = msg.content or ""
                                    if content and not hasattr(msg, 'tool_calls'):
                                        logger.info(f"💡 Agent Reasoning: {content[:200]}...")
                                    # Check for tool calls
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        for tool_call in msg.tool_calls:
                                            logger.info(f"🔧 Agent decided to call: {tool_call.get('name', 'unknown')}")
                                            logger.info(f"   with args: {tool_call.get('args', {})}")
                        elif node_name.startswith("tools"):
                            # Tool is executing
                            tool_messages = node_output.get("messages", [])
                            final_messages.extend(tool_messages)
                            for msg in tool_messages:
                                if isinstance(msg, ToolMessage):
                                    tool_result = str(msg.content)[:200]
                                    logger.info(f"✅ Tool '{msg.name}' returned result")
                                    logger.info(f"   Result preview: {tool_result}...")
                                    intermediate_steps.append({
                                        "tool": msg.name,
                                        "result": tool_result
                                    })
            
            # Extract final response from accumulated messages
            if final_messages:
                # Find the last AI message that's not a tool call
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage):
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            continue  # Skip tool call messages
                        response_text = msg.content or ""
                        break
                
                # If no non-tool-call message found, get the last message
                if not response_text:
                    last_msg = final_messages[-1]
                    if hasattr(last_msg, 'content'):
                        response_text = last_msg.content
                    else:
                        response_text = str(last_msg)
            
            # Log final response
            if self.config.verbose:
                logger.info("")
                logger.info("✅" + "=" * 79)
                logger.info("📤 FINAL RESPONSE:")
                logger.info("-" * 79)
                logger.info(response_text)
                logger.info("✅" + "=" * 79)
                logger.info("")
            
            # Update memory
            if self.memory:
                self.memory.save_context({"input": query}, {"output": response_text})

            return {
                "status": "success",
                "response": response_text,
                "intermediate_steps": intermediate_steps,
            }

        except Exception as e:
            logger.error("")
            logger.error("❌" + "=" * 79)
            logger.error(f"ERROR: {str(e)}")
            logger.error("❌" + "=" * 79)
            logger.error("")
            return {"status": "error", "message": f"Query failed: {str(e)}"}


# --------------------------------------------------------------------------------------
# CLI for quick testing
# --------------------------------------------------------------------------------------
async def main():
    """CLI interface for testing the MCP client"""
    config = ClientConfig()
    client = MCPClient(config)

    print("=" * 80)
    print("MCP Client (Groq)")
    print("=" * 80)

    try:
        print("Connecting to services...")
        await client.connect()
        print("Connected successfully!")
        print(f"Tools available: {len(client.tools)}")

        print("\n" + "=" * 80)
        print("Assistant Ready!")
        print("Type 'exit' to quit")
        print("=" * 80)

        while True:
            try:
                query = input("\nYou: ").strip()
                if not query:
                    continue

                if query.lower() in {"exit", "quit", "q"}:
                    print("Goodbye!")
                    break

                print("\nProcessing...")
                response = await client.query(query)

                if response["status"] == "success":
                    print(f"\nAssistant:\n{response['response']}")
                else:
                    print(f"\nError: {response['message']}")

            except KeyboardInterrupt:
                print("\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                logger.exception("CLI error")

    except Exception as e:
        print(f"\nFailed to start: {e}")
        logger.exception("Startup error")


if __name__ == "__main__":
    asyncio.run(main())
