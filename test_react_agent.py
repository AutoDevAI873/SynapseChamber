#!/usr/bin/env python3
"""
Test script for the ReAct Agent.
Runs a simple test to verify the agent's functionality.
"""

import logging
import json
from react_agent import ReActAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_react_agent():
    """Test the ReAct agent with a simple task"""
    print("="*80)
    print("Testing ReAct Agent")
    print("="*80)
    
    agent = ReActAgent(max_steps=6, audit_log_path="data/agent/react_audit.jsonl")
    
    print("\nTest 1: Simple memory retrieval task (dry run)")
    print("-"*80)
    
    result = agent.run_task(
        task="Retrieve the most recent AI conversation from memory and summarize it",
        dry_run=True
    )
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*80)
    print("Test completed")
    print("="*80)

if __name__ == "__main__":
    test_react_agent()
