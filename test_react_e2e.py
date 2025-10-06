import logging
import json
from react_agent import ReActAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_simple_task():
    """
    End-to-end test of the ReAct agent system.
    Tests: task execution, audit logging, memory storage.
    """
    print("\n" + "="*80)
    print("SYNAPSE CHAMBER - ReAct Agent End-to-End Test")
    print("="*80 + "\n")
    
    agent = ReActAgent(max_steps=6)
    
    task = "Recommend the best AI platform for writing Python code to implement a web scraper"
    
    print(f"Task: {task}")
    print(f"Dry Run: True (safe testing mode)")
    print("\n" + "-"*80 + "\n")
    
    result = agent.run_task(
        task=task,
        initial_context_query="python coding web scraping",
        dry_run=True
    )
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    print(f"Status: {result.get('status')}")
    print(f"Steps Executed: {len(result.get('history', []))}")
    print(f"Audit Log Entries: {len(result.get('audit_log', []))}")
    
    if result.get('status') == 'finished':
        print(f"\nFinal Result:")
        print(json.dumps(result.get('result'), indent=2))
        
        if result.get('reflection'):
            print(f"\nPost-Task Reflection:")
            print(json.dumps(result.get('reflection'), indent=2))
    
    print("\n" + "-"*80)
    print("EXECUTION HISTORY")
    print("-"*80 + "\n")
    
    for i, entry in enumerate(result.get('history', []), 1):
        print(f"Step {i}:")
        print(f"  Action: {entry.get('action', {}).get('action')}")
        if entry.get('action', {}).get('comment'):
            print(f"  Comment: {entry.get('action', {}).get('comment')}")
        result_data = entry.get('result', {})
        if result_data.get('done'):
            print(f"  Result: Task finished")
        elif result_data.get('need_approval'):
            print(f"  Result: Approval required")
        else:
            obs = result_data.get('observation', {})
            if isinstance(obs, dict):
                print(f"  Observation: {obs.get('success', 'N/A')}")
            else:
                print(f"  Observation: {str(obs)[:100]}...")
        print()
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")
    
    return result

if __name__ == "__main__":
    test_simple_task()
