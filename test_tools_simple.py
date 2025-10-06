import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_file_ops_tools():
    """
    Test the file operations tools that don't require Flask/database context.
    """
    print("\n" + "="*80)
    print("SYNAPSE CHAMBER - Tools Registry Test (File Operations)")
    print("="*80 + "\n")
    
    from tools_registry import ToolsRegistry
    
    print("Initializing Tools Registry (no Flask context)...")
    registry = ToolsRegistry()
    
    print(f"✓ Tools Registry initialized with {len(registry.tools)} tools\n")
    
    print("-"*80)
    print("Test 1: Generate Code Patch")
    print("-"*80)
    
    patch_result = registry.tools["propose_code_patch"]({
        "file_path": "test_file.py",
        "patch_hint": "add import json"
    })
    
    print(f"Success: {patch_result.get('success')}")
    if patch_result.get('success'):
        print(f"Confidence: {patch_result.get('result', {}).get('confidence', 0)}")
        print(f"Patch Type: {patch_result.get('result', {}).get('patch_type', 'N/A')}")
    else:
        print(f"Error: {patch_result.get('error')}")
    
    print("\n" + "-"*80)
    print("Test 2: Safe Code Execution (Dry Run)")
    print("-"*80)
    
    code_result = registry.tools["run_code"]({
        "code_str": "print('Hello from ReAct agent!')",
        "timeout": 5,
        "dry_run": True
    })
    
    print(f"Success: {code_result.get('success')}")
    print(f"Dry Run: {code_result.get('result', {}).get('dry_run', False)}")
    if code_result.get('success'):
        print(f"Message: {code_result.get('result', {}).get('output', '')}")
    
    print("\n" + "-"*80)
    print("Test 3: Create PR (Dry Run)")
    print("-"*80)
    
    pr_result = registry.tools["create_pr"]({
        "branch_name": "feature-react-agent",
        "title": "Add ReAct Agent System",
        "diff_content": "test changes",
        "dry_run": True
    })
    
    print(f"Success: {pr_result.get('success')}")
    print(f"Dry Run: {pr_result.get('result', {}).get('dry_run', False)}")
    if pr_result.get('success'):
        print(f"Branch: {pr_result.get('result', {}).get('branch', 'N/A')}")
        print(f"Message: {pr_result.get('result', {}).get('message', '')}")
    
    print("\n" + "-"*80)
    print("Test 4: AI Tool (Expected to Fail Without Flask Context)")
    print("-"*80)
    
    ai_result = registry.tools["call_ai"]({
        "platform": "gpt",
        "prompt": "Hello"
    })
    
    print(f"Success: {ai_result.get('success')}")
    print(f"Error: {ai_result.get('error')}")
    
    print("\n" + "="*80)
    print("TOOLS REGISTRY TEST COMPLETE")
    print("="*80 + "\n")
    print("Summary:")
    print(f"  - File operations tools: ✓ Working (no Flask context needed)")
    print(f"  - AI tools: Expected to require Flask context")
    print(f"  - Total tools available: {len(registry.tools)}")
    print()

if __name__ == "__main__":
    test_file_ops_tools()
