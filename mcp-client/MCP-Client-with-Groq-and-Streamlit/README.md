# MCP Client with Groq and Streamlit

A powerful Model Context Protocol (MCP) client built with LangChain, LangGraph, and Groq, featuring real-time execution tracing, internet search capabilities, and an interactive Streamlit interface.

## 🚀 Features

- **MCP Server Integration**: Streamable HTTP MCP server with customizable tools
- **Groq LLM Integration**: Fast inference using Groq's API with LangChain   
- **Real-time Execution Tracing**: Comprehensive verbose logging showing:
  - Agent reasoning and decision-making process 
  - Tool calls with inputs and outputs
  - LLM thinking steps
  - Chain execution flow
- **Internet Search**: Google Custom Search API integration for web searches
- **Interactive UI**: Streamlit-based web interface for easy interaction
- **Tool Management**: Modular tool system for easy extension

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key ([Get one here](https://console.groq.com/))
- Google API Key and Custom Search Engine ID (for web search functionality)
  - [Google Cloud Console](https://console.cloud.google.com/)
  - [Custom Search Engine Setup](https://developers.google.com/custom-search/v1/overview)

## 🔧 Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd MCPclientwithgroq
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   # Required: Groq API Key
   GROQ_API_KEY=your_groq_api_key_here
   
   # Optional: Custom Groq model (default: llama-3.3-70b-versatile)
   GROQ_MODEL=llama-3.3-70b-versatile
   
   # Required for web search: Google API credentials
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_custom_search_engine_id_here
   
   # Optional: MCP Server URL (default: http://127.0.0.1:8000/mcp)
   MCP_URL=http://127.0.0.1:8000/mcp
   
   # Optional: Agent configuration
   AGENT_MAX_ITERATIONS=6
   AGENT_TIMEOUT_SECONDS=90
   MEMORY_WINDOW_SIZE=8
   MCP_CONNECT_TIMEOUT=12
   
   # Optional: Enable/disable verbose logging (default: true)
   VERBOSE_LOGGING=true
   ```

## 🏗️ Project Structure

```
.
├── client.py              # Main MCP client with Groq integration
├── mcp_server.py         # MCP server with streamable HTTP transport
├── streamlit_app.py      # Streamlit web interface
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables (create this)
```

## 🎯 Usage

### 1. Start the MCP Server

In one terminal, start the MCP server:

```bash
python mcp_server.py
```

The server will start on `http://127.0.0.1:8000/mcp` by default. You should see:
```
🚀 Starting MCP server (streamable-http)
📡 Transport: streamable-http
🔧 Available tools: get_time, calculate, web_search
```

### 2. Run the Client (CLI Mode)

In another terminal, run the client:

```bash
python client.py
```

This will start an interactive CLI where you can chat with the agent:
```
================================================================================
MCP Client (Groq)
================================================================================
Connecting to services...
Connected successfully!
Tools available: 3

Assistant Ready!
Type 'exit' to quit
================================================================================

You: What's the current time?
```

### 3. Run the Streamlit Web Interface

For a better user experience, use the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

**Important**: Use `streamlit run`, NOT `python streamlit_app.py`

The app will open in your browser at `http://localhost:8501`

## 🛠️ Available Tools

The MCP server provides the following tools:

### 1. `get_time`
Returns the current date and time in ISO format.

**Usage Example**:
- User: "What time is it?"
- Agent: Calls `get_time()` → Returns current datetime

### 2. `calculate`
Safely evaluates mathematical expressions.

**Usage Example**:
- User: "What's 15 * 23 + 45?"
- Agent: Calls `calculate("15 * 23 + 45")` → Returns result

### 3. `web_search`
Searches the internet using Google Custom Search API.

**Parameters**:
- `query` (required): Search query string
- `num_results` (optional, default: 5): Number of results to return (max: 10)

**Usage Example**:
- User: "What are the latest AI trends?"
- Agent: Calls `web_search({"query": "latest AI trends", "num_results": 5})` → Returns search results

## 📊 Verbose Logging

The client features comprehensive real-time execution tracing. When `VERBOSE_LOGGING=true`, you'll see:

### Example Log Output

```
🚀================================================================================
📝 USER QUERY: What are the current news trends in AI?
🚀================================================================================

🤖 Starting agent execution...

================================================================================
🤔 STEP 1: LLM Thinking...
================================================================================

💡 Agent Reasoning: I need to search the internet for current AI news trends...

🔧 Agent decided to call: web_search
   with args: {'query': 'current AI news trends', 'num_results': 5}

--------------------------------------------------------------------------------
🔧 TOOL CALL: web_search
📥 Input:
{
  "query": "current AI news trends",
  "num_results": 5
}
--------------------------------------------------------------------------------

✅ Tool 'web_search' returned result
   Result preview: {'status': 'success', 'query': 'current AI news trends'...

✅================================================================================
📤 FINAL RESPONSE:
--------------------------------------------------------------------------------
Based on the latest search results, here are the current AI trends...
✅================================================================================
```

### Logging Features

- **Step Numbers**: Each LLM reasoning step is numbered
- **Tool Calls**: Shows which tools are called and with what arguments
- **Tool Outputs**: Displays tool results (truncated for readability)
- **Chain Execution**: Tracks the execution flow through the agent chain
- **Error Logging**: Comprehensive error messages with context

## ⚙️ Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | Your Groq API key |
| `GOOGLE_API_KEY` | ✅ Yes* | - | Google API key for web search |
| `GOOGLE_CSE_ID` | ✅ Yes* | - | Google Custom Search Engine ID |
| `GROQ_MODEL` | ❌ No | `llama-3.3-70b-versatile` | Groq model to use |
| `MCP_URL` | ❌ No | `http://127.0.0.1:8000/mcp` | MCP server URL |
| `AGENT_MAX_ITERATIONS` | ❌ No | `6` | Maximum agent iterations |
| `AGENT_TIMEOUT_SECONDS` | ❌ No | `90` | Agent timeout in seconds |
| `MEMORY_WINDOW_SIZE` | ❌ No | `8` | Conversation memory window size |
| `MCP_CONNECT_TIMEOUT` | ❌ No | `12` | MCP connection timeout |
| `VERBOSE_LOGGING` | ❌ No | `true` | Enable/disable verbose logging |

\* Required only if using `web_search` tool

## 🐛 Troubleshooting

### Connection Errors

**Problem**: "Failed to connect to MCP server"
- **Solution**: Ensure the MCP server is running on the expected port (default: 8000)
- Check `MCP_URL` in your `.env` file matches the server address

### Missing API Keys

**Problem**: "GROQ_API_KEY is missing"
- **Solution**: Add your Groq API key to the `.env` file
- Ensure the `.env` file is in the project root directory

### Web Search Not Working

**Problem**: Web search returns errors
- **Solution**: 
  1. Verify `GOOGLE_API_KEY` and `GOOGLE_CSE_ID` are set correctly
  2. Ensure your Google API key has Custom Search API enabled
  3. Check your Custom Search Engine is configured properly

### Streamlit Warnings

**Problem**: "missing ScriptRunContext" warnings
- **Solution**: Always use `streamlit run streamlit_app.py`, not `python streamlit_app.py`

### Tool Schema Errors

**Problem**: "tool call validation failed" errors
- **Solution**: This may occur with Groq's API. Ensure you're using compatible tool schemas
- Check that tools are properly defined in `mcp_server.py`

## 🔌 Adding New Tools

To add a new tool to the MCP server, edit `mcp_server.py`:

```python
@mcp.tool()
def your_new_tool(param1: str, param2: int = 5) -> Dict[str, Any]:
    """
    Description of what your tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)
    
    Returns:
        Dictionary with results
    """
    try:
        # Your tool logic here
        result = do_something(param1, param2)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

The tool will automatically be available to the client after restarting the server.

## 📝 Example Queries

Here are some example queries you can try:

**Time Queries**:
- "What time is it?"
- "Get the current date and time"

**Calculation Queries**:
- "Calculate 125 * 342"
- "What's 15% of 850?"
- "Solve: (100 + 50) / 2"

**Web Search Queries**:
- "Search for latest Python updates"
- "What are the current trends in machine learning?"
- "Find information about LangChain"

**Combined Queries**:
- "What time is it and search for today's news?"
- "Calculate 100 * 50 and then search for calculator tools"

## 🏛️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │
│  streamlit_app  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Client    │
│   client.py     │◄─── LangGraph Agent
│                 │     + Groq LLM
└────────┬────────┘
         │
         │ (Streamable HTTP)
         ▼
┌─────────────────┐
│   MCP Server    │
│  mcp_server.py  │
│                 │
│  Tools:         │
│  - get_time     │
│  - calculate    │
│  - web_search   │
└─────────────────┘
```

## 🧪 Testing

Test the basic functionality:

1. **Start the server**:
   ```bash
   python mcp_server.py
   ```

2. **In another terminal, test the client**:
   ```bash
   python client.py
   ```

3. **Try these queries**:
   - "What's the time?"
   - "Calculate 2 + 2"
   - "Search for Python documentation"

## 📚 Dependencies

Key dependencies include:
- **LangChain**: Framework for building LLM applications
- **LangGraph**: For agent orchestration and workflows
- **Groq**: Fast LLM inference
- **MCP**: Model Context Protocol for tool integration
- **Streamlit**: Web UI framework
- **FastMCP**: MCP server implementation
- **httpx**: Async HTTP client

See `requirements.txt` for the complete list.

## 🤝 Contributing

Feel free to:
- Add new tools to `mcp_server.py`
- Enhance the Streamlit UI
- Improve verbose logging
- Add new features to the client

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) for the framework
- [Groq](https://groq.com/) for fast LLM inference
- [Streamlit](https://streamlit.io/) for the UI framework
- [MCP](https://modelcontextprotocol.io/) for the protocol specification

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs (with verbose logging enabled)
3. Verify all environment variables are set correctly

---







