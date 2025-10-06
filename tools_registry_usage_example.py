"""
Example usage of the Tools Registry for the ReAct Agent

This demonstrates how to use the tools registry to access various
capabilities of the Synapse Chamber AutoDev system.
"""

import logging
from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_call_ai():
    """Example: Call an AI platform with a prompt"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        payload = {
            "platform": "gpt",
            "prompt": "What is the best way to implement error handling in Python?",
            "task_type": "coding",
            "subject": "Python Error Handling",
            "goal": "Learn error handling best practices"
        }
        
        result = registry.execute_tool("call_ai", payload)
        print(f"AI Response: {result}")


def example_recommend_platform():
    """Example: Get platform recommendation for a task"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        payload = {
            "prompt": "Write a creative story about AI",
            "task_type": "creative_writing"
        }
        
        result = registry.execute_tool("recommend_platform", payload)
        print(f"Platform Recommendation: {result}")


def example_memory_operations():
    """Example: Store and retrieve memories"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        # Store a memory
        store_payload = {
            "platform": "system",
            "content": "User prefers detailed code examples with explanations",
            "is_user": False,
            "subject": "User Preferences",
            "goal": "Track user preferences"
        }
        
        store_result = registry.execute_tool("memory_store", store_payload)
        print(f"Memory Store Result: {store_result}")
        
        # Retrieve memories
        if store_result.get("success"):
            conversation_id = store_result.get("conversation_id")
            
            retrieve_payload = {
                "conversation_id": conversation_id
            }
            
            retrieve_result = registry.execute_tool("memory_retrieve", retrieve_payload)
            print(f"Memory Retrieve Result: {retrieve_result}")


def example_code_operations():
    """Example: Run code and generate patches"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        # Run code in dry-run mode (validation only)
        code_payload = {
            "code_str": "print('Hello, Synapse Chamber!')",
            "timeout": 30,
            "dry_run": True
        }
        
        code_result = registry.execute_tool("run_code", code_payload)
        print(f"Code Execution Result: {code_result}")
        
        # Generate a code patch
        patch_payload = {
            "file_path": "test_tools_registry.py",
            "patch_hint": "Add a comment explaining the purpose of the test function"
        }
        
        patch_result = registry.execute_tool("propose_code_patch", patch_payload)
        print(f"Code Patch Result: {patch_result}")


def example_training_cycle():
    """Example: Start a training cycle"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        payload = {
            "topic": "api_handling",
            "mode": "all_ais_train",
            "platforms": ["gpt", "claude", "gemini"],
            "goal": "Learn best practices for API integration"
        }
        
        result = registry.execute_tool("run_training_cycle", payload)
        print(f"Training Cycle Result: {result}")


def example_browse_page():
    """Example: Browse a web page"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        payload = {
            "url": "https://example.com"
        }
        
        result = registry.execute_tool("browse_page", payload)
        print(f"Browse Page Result: {result}")


def example_get_tool_info():
    """Example: Get information about available tools"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        # Get info about all tools
        all_tools = registry.get_tool_info()
        print("\nAll Available Tools:")
        print(f"Total: {all_tools['count']}")
        for tool_name in all_tools['tools']:
            print(f"  - {tool_name}")
        
        # Get info about a specific tool
        specific_tool = registry.get_tool_info("call_ai")
        print(f"\nSpecific Tool Info: {specific_tool}")


def example_error_handling():
    """Example: Error handling in tool execution"""
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        # Try to execute a non-existent tool
        result = registry.execute_tool("non_existent_tool", {})
        print(f"Non-existent Tool Result: {result}")
        
        # Try to execute with missing required parameters
        result = registry.execute_tool("call_ai", {})
        print(f"Missing Parameters Result: {result}")


def example_react_agent_workflow():
    """
    Example: Complete ReAct agent workflow
    
    This demonstrates how a ReAct agent would use the tools registry:
    1. Think about the task
    2. Select appropriate tool
    3. Execute tool with payload
    4. Observe result
    5. Decide next action
    """
    from tools_registry import ToolsRegistry
    
    with app.app_context():
        registry = ToolsRegistry()
        
        # Task: "Help me understand the best AI platform for code generation"
        
        # Step 1: Recommend platform
        print("\n=== Step 1: Recommend Platform ===")
        recommend_result = registry.execute_tool("recommend_platform", {
            "prompt": "Generate Python code for a web scraper",
            "task_type": "code_generation"
        })
        print(f"Recommendation: {recommend_result}")
        
        if recommend_result.get("success"):
            best_platform = recommend_result.get("best_platform")
            
            # Step 2: Call the recommended AI
            print(f"\n=== Step 2: Call {best_platform} ===")
            ai_result = registry.execute_tool("call_ai", {
                "platform": best_platform,
                "prompt": "Write a Python function to scrape a website",
                "task_type": "code_generation",
                "subject": "Web Scraping",
                "goal": "Generate web scraping code"
            })
            print(f"AI Response: {ai_result}")
            
            # Step 3: Store the interaction in memory
            print("\n=== Step 3: Store in Memory ===")
            if ai_result.get("success"):
                memory_result = registry.execute_tool("memory_store", {
                    "platform": best_platform,
                    "content": f"Generated web scraping code using {best_platform}",
                    "is_user": False,
                    "subject": "Code Generation Session",
                    "goal": "Track AI interactions"
                })
                print(f"Memory Storage: {memory_result}")


if __name__ == "__main__":
    print("="*70)
    print("TOOLS REGISTRY USAGE EXAMPLES")
    print("="*70)
    
    # Run individual examples (comment out the ones you don't want to run)
    
    # example_recommend_platform()
    # example_memory_operations()
    # example_code_operations()
    # example_training_cycle()
    # example_browse_page()
    example_get_tool_info()
    # example_error_handling()
    # example_react_agent_workflow()
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)
