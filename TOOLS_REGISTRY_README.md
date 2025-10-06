# Tools Registry for ReAct Agent

## Overview

The `tools_registry.py` module provides a clean, structured API for the ReAct agent to access all capabilities of the Synapse Chamber AutoDev system. It centralizes tool management, provides error handling, and ensures proper module initialization.

## Features

### ✅ Implemented Tools (10 total)

1. **call_ai** - Call an AI platform with a prompt
   - Parameters: `platform`, `prompt`, `task_type`, `subject`, `goal`
   - Approval Required: No

2. **recommend_platform** - Get the best AI platform recommendation
   - Parameters: `prompt`, `task_type`
   - Approval Required: No

3. **browse_page** - Navigate to URL and extract content
   - Parameters: `url`
   - Approval Required: No

4. **solve_captcha** - Solve CAPTCHA challenges
   - Parameters: `captcha_type`
   - Approval Required: No

5. **run_training_cycle** - Start an AI training session
   - Parameters: `topic`, `mode`, `platforms`, `goal`
   - Approval Required: No

6. **memory_store** - Store conversation/memory
   - Parameters: `conversation_id`, `content`, `is_user`, `screenshot_path`
   - Approval Required: No

7. **memory_retrieve** - Retrieve relevant memories
   - Parameters: `conversation_id`, `platform`, `subject`, `limit`
   - Approval Required: No

8. **propose_code_patch** - Generate code patch suggestions
   - Parameters: `file_path`, `patch_hint`
   - Approval Required: No

9. **run_code** - Execute Python code safely ⚠️
   - Parameters: `code_str`, `timeout`, `dry_run`
   - Approval Required: **YES**

10. **create_pr** - Create git branch and commit ⚠️
    - Parameters: `branch_name`, `title`, `diff_content`, `dry_run`
    - Approval Required: **YES**

### ❌ Not Implemented

- **search_web** - Web search capability not available in current browser_automation module

## Architecture

### Module Dependencies

```
ToolsRegistry
├── BrowserAutomation (initialized first)
├── CAPTCHASolver (initialized second)
├── MemorySystem (initialized third)
├── AIController (requires: browser_automation, captcha_solver, memory_system)
├── TrainingSessionManager (requires: ai_controller, memory_system)
└── FileOperations (standalone)
```

### Initialization

The tools registry uses lazy imports to avoid circular dependency issues with the Flask app:

```python
from tools_registry import ToolsRegistry
from app import app

with app.app_context():
    registry = ToolsRegistry()
```

## Usage Examples

### Basic Tool Execution

```python
from tools_registry import ToolsRegistry
from app import app

with app.app_context():
    registry = ToolsRegistry()
    
    # Execute a tool
    result = registry.execute_tool("call_ai", {
        "platform": "gpt",
        "prompt": "Explain async/await in Python",
        "task_type": "coding"
    })
    
    print(result)
```

### Get Tool Information

```python
# Get all tools
info = registry.get_tool_info()
print(f"Available tools: {info['tools']}")

# Get specific tool info
tool_info = registry.get_tool_info("call_ai")
print(f"Tool: {tool_info}")
```

### Error Handling

All tools return a standardized response format:

```python
{
    "success": bool,
    "error": str (optional),
    "traceback": str (optional),
    # ... tool-specific fields
}
```

### ReAct Agent Workflow

```python
from tools_registry import ToolsRegistry
from app import app

with app.app_context():
    registry = ToolsRegistry()
    
    # 1. Think: Determine what tool to use
    # 2. Act: Execute the tool
    result = registry.execute_tool("recommend_platform", {
        "prompt": "Write a web scraper",
        "task_type": "code_generation"
    })
    
    # 3. Observe: Check the result
    if result.get("success"):
        best_platform = result.get("best_platform")
        
        # 4. Think & Act again
        ai_result = registry.execute_tool("call_ai", {
            "platform": best_platform,
            "prompt": "Write a Python web scraper"
        })
```

## Tool Details

### call_ai

Calls an AI platform (GPT, Claude, Gemini, DeepSeek, or Grok) with a prompt.

**Payload:**
```python
{
    "platform": "gpt",  # or "claude", "gemini", "deepseek", "grok"
    "prompt": "Your question or task",
    "task_type": "coding",  # optional: coding, reasoning, creativity, etc.
    "subject": "Session topic",  # optional
    "goal": "Session objective"  # optional
}
```

**Response:**
```python
{
    "success": True/False,
    "result": {
        "status": "success",
        "response": "AI response text",
        "platform": "gpt",
        ...
    }
}
```

### recommend_platform

Gets the best AI platform recommendation for a given task.

**Payload:**
```python
{
    "prompt": "Your task description",
    "task_type": "coding"  # optional: will auto-detect from prompt
}
```

**Response:**
```python
{
    "success": True,
    "recommendations": ["deepseek", "gpt", "claude"],  # ranked list
    "best_platform": "deepseek"
}
```

### memory_store

Stores a message or memory entry in the memory system.

**Payload:**
```python
{
    "conversation_id": 123,  # optional: creates new if not provided
    "platform": "gpt",  # required if creating new conversation
    "content": "Memory content",
    "is_user": True,  # True for user messages, False for AI
    "screenshot_path": "/path/to/screenshot.png"  # optional
}
```

**Response:**
```python
{
    "success": True,
    "conversation_id": 123
}
```

### memory_retrieve

Retrieves conversation history or memories.

**Payload:**
```python
{
    "conversation_id": 123,  # optional: get specific conversation
    "platform": "gpt",  # optional: filter by platform
    "subject": "Python",  # optional: filter by subject
    "limit": 10  # optional: max results
}
```

**Response:**
```python
{
    "success": True,
    "conversations": [...],  # or "conversation": {...}
    "count": 10
}
```

### run_code ⚠️

Executes Python code safely in a subprocess. **Requires approval.**

**Payload:**
```python
{
    "code_str": "print('Hello')",
    "timeout": 30,  # optional: default 30 seconds
    "dry_run": False  # optional: True to validate only
}
```

**Response:**
```python
{
    "success": True,
    "execution": {
        "success": True,
        "output": "Hello\n",
        "error": "",
        "execution_time": 0.05,
        "return_code": 0
    }
}
```

### create_pr ⚠️

Creates a git branch and commits changes. **Requires approval.**

**Payload:**
```python
{
    "branch_name": "feature/new-tool",
    "title": "Add new tool functionality",
    "diff_content": "Description of changes",
    "dry_run": True  # optional: default True
}
```

**Response:**
```python
{
    "success": True,
    "pr": {
        "success": True,
        "branch": "feature/new-tool",
        "message": "Branch created successfully",
        "commit_hash": "abc123..."  # if not dry_run
    }
}
```

## Files

- `tools_registry.py` - Main tools registry implementation
- `test_tools_registry.py` - Test script for registry initialization
- `tools_registry_usage_example.py` - Comprehensive usage examples
- `TOOLS_REGISTRY_README.md` - This documentation

## Integration with ReAct Agent

The tools registry is designed to work seamlessly with a ReAct (Reasoning + Acting) agent:

1. **Reasoning Phase**: Agent analyzes the task and determines which tool to use
2. **Action Phase**: Agent calls `registry.execute_tool(tool_name, payload)`
3. **Observation Phase**: Agent examines the result
4. **Iteration**: Agent repeats until task is complete

### Example ReAct Loop

```python
def react_agent_loop(task, max_iterations=5):
    registry = ToolsRegistry()
    
    for i in range(max_iterations):
        # THINK: Determine next action
        action = determine_next_action(task, previous_results)
        
        # ACT: Execute the tool
        result = registry.execute_tool(action["tool"], action["payload"])
        
        # OBSERVE: Check if task is complete
        if is_task_complete(task, result):
            return result
    
    return {"error": "Max iterations reached"}
```

## Error Handling

All tools implement comprehensive error handling:

1. **Parameter Validation**: Missing or invalid parameters return structured errors
2. **Exception Catching**: All exceptions are caught and returned in standardized format
3. **Logging**: All errors are logged with full tracebacks
4. **Graceful Degradation**: Tools fail safely without crashing the system

## Security

- **Approval Required**: Destructive operations (run_code, create_pr) require approval
- **Path Validation**: File operations validate paths to prevent directory traversal
- **Subprocess Isolation**: Code execution runs in isolated subprocess with timeout
- **Dry Run Mode**: Dangerous operations support dry-run for safety

## Testing

Run the test suite:

```bash
python test_tools_registry.py
```

Run usage examples:

```bash
python tools_registry_usage_example.py
```

## Future Enhancements

1. **search_web** - Add web search capability to browser_automation
2. **RAG Integration** - Enhance memory_retrieve with semantic search
3. **Tool Chaining** - Support for executing multiple tools in sequence
4. **Async Support** - Add async tool execution for better performance
5. **Tool Analytics** - Track tool usage and performance metrics
