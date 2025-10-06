import logging
import json
import re
import os
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

from tools_registry import ToolsRegistry
from ai_controller import AIController

logger = logging.getLogger(__name__)


class ReActAgent:
    """
    Production-ready ReAct (Reasoning + Acting) agent with strict safety controls.
    
    Features:
    - Strict JSON-only prompting (no chain-of-thought allowed)
    - Approval workflow for sensitive actions
    - Audit logging to JSONL file
    - Max steps circuit breaker
    - Dry run mode support
    - Post-task reflection and evaluation
    """
    
    APPROVAL_REQUIRED_ACTIONS: Set[str] = {"create_pr", "run_code", "delete_resource"}
    
    def __init__(self, max_steps: int = 6, audit_log_path: str = "data/audit.jsonl"):
        """
        Initialize the ReAct agent.
        
        Args:
            max_steps: Maximum number of reasoning-action steps allowed
            audit_log_path: Path to the JSONL audit log file
        """
        self.logger = logging.getLogger(__name__)
        self.max_steps = max_steps
        self.audit_log_path = audit_log_path
        self.audit_log: List[Dict[str, Any]] = []
        
        self.logger.info(f"Initializing ReAct Agent (max_steps={max_steps})")
        
        try:
            self.tools_registry = ToolsRegistry()
            self.TOOLS = self.tools_registry.tools
            self.TOOL_METADATA = self.tools_registry.tool_metadata
            
            self.ai_controller = self.tools_registry.ai_controller
            
            os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
            
            self.logger.info(f"ReAct Agent initialized with {len(self.TOOLS)} tools")
            
        except Exception as e:
            self.logger.error(f"Error initializing ReAct Agent: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
    
    def run_task(
        self, 
        task: str, 
        initial_context_query: Optional[str] = None, 
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Main execution loop for the ReAct agent.
        
        Args:
            task: The task description to execute
            initial_context_query: Optional query to gather initial context
            dry_run: If True, don't execute actions that modify state
            
        Returns:
            Dictionary with status, result, history, and audit_log
        """
        task_id = str(uuid.uuid4())
        history: List[Dict[str, Any]] = []
        context_snippets: List[str] = []
        
        self.logger.info(f"Starting ReAct task: {task} (task_id={task_id}, dry_run={dry_run})")
        
        try:
            if initial_context_query:
                self.logger.info(f"Gathering initial context: {initial_context_query}")
                context_result = self._gather_context(initial_context_query)
                if context_result.get("success"):
                    context_snippets.append(context_result.get("context", ""))
            
            for step in range(self.max_steps):
                self.logger.info(f"ReAct Step {step + 1}/{self.max_steps}")
                
                prompt = self._build_prompt(task, context_snippets, history)
                
                platform = self._get_best_platform(task)
                self.logger.info(f"Using platform: {platform} for step {step + 1}")
                
                llm_response = self._call_llm(platform, prompt, task)
                
                if not llm_response.get("success"):
                    error_msg = llm_response.get("error", "Unknown LLM error")
                    self.logger.error(f"LLM call failed: {error_msg}")
                    
                    audit_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "step": step,
                        "task_id": task_id,
                        "action": {"error": "llm_call_failed"},
                        "result": {"error": error_msg}
                    }
                    self._append_audit_log(audit_entry)
                    
                    return {
                        "status": "error",
                        "error": error_msg,
                        "history": history,
                        "audit_log": self.audit_log
                    }
                
                response_text = llm_response.get("result", {}).get("response", "")
                self.logger.debug(f"LLM response (truncated): {response_text[:200]}...")
                
                action_obj = self._parse_json(response_text)
                
                if not action_obj:
                    self.logger.warning(f"Failed to parse JSON from LLM response at step {step + 1}")
                    history.append({
                        "step": step + 1,
                        "thought": "Failed to parse valid JSON from response",
                        "observation": "Error: Invalid JSON format. Please respond with valid JSON only."
                    })
                    continue
                
                validation_result = self._validate_action(action_obj)
                
                if not validation_result.get("valid"):
                    error_msg = validation_result.get("error", "Unknown validation error")
                    self.logger.warning(f"Action validation failed: {error_msg}")
                    history.append({
                        "step": step + 1,
                        "action": action_obj,
                        "observation": f"Error: {error_msg}"
                    })
                    continue
                
                action_name = action_obj.get("action")
                
                if action_name == "finish":
                    result = action_obj.get("action_input", {}).get("result", "Task completed")
                    self.logger.info(f"Task finished at step {step + 1}: {result}")
                    
                    audit_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "step": step,
                        "task_id": task_id,
                        "action": action_obj,
                        "result": {"status": "finished", "result": result}
                    }
                    self._append_audit_log(audit_entry)
                    
                    reflection = self._post_task_reflection(task, history, result)
                    
                    return {
                        "status": "finished",
                        "result": result,
                        "history": history,
                        "audit_log": self.audit_log,
                        "reflection": reflection
                    }
                
                execution_result = self._execute(action_obj, dry_run=dry_run)
                
                if execution_result.get("status") == "awaiting_approval":
                    self.logger.info(f"Action requires approval: {action_name}")
                    return {
                        "status": "awaiting_approval",
                        "entry": execution_result.get("entry"),
                        "history": history,
                        "audit_log": self.audit_log
                    }
                
                audit_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "step": step,
                    "task_id": task_id,
                    "action": action_obj,
                    "result": execution_result
                }
                self._append_audit_log(audit_entry)
                
                observation = self._format_observation(execution_result)
                
                history.append({
                    "step": step + 1,
                    "action": action_obj,
                    "observation": observation
                })
            
            self.logger.warning(f"Task reached max steps ({self.max_steps}) without finishing")
            
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "step": self.max_steps,
                "task_id": task_id,
                "action": {"error": "max_steps_reached"},
                "result": {"status": "failed_max_steps"}
            }
            self._append_audit_log(audit_entry)
            
            return {
                "status": "failed_max_steps",
                "history": history,
                "audit_log": self.audit_log,
                "message": f"Task did not complete within {self.max_steps} steps"
            }
            
        except Exception as e:
            self.logger.error(f"Error in run_task: {str(e)}")
            self.logger.error(traceback.format_exc())
            
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "action": {"error": "exception"},
                "result": {"error": str(e), "traceback": traceback.format_exc()}
            }
            self._append_audit_log(audit_entry)
            
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "history": history,
                "audit_log": self.audit_log
            }
    
    def _build_prompt(
        self, 
        task: str, 
        context_snippets: List[str], 
        history: List[Dict[str, Any]]
    ) -> str:
        """
        Build a strict JSON-only prompt for the LLM.
        
        Args:
            task: The task description
            context_snippets: Any relevant context gathered
            history: Previous action-observation history
            
        Returns:
            Formatted prompt string
        """
        tools_list = list(self.TOOLS.keys())
        tools_list.append("finish")
        
        tools_descriptions = []
        for tool_name in tools_list:
            if tool_name == "finish":
                tools_descriptions.append(
                    "finish: Complete the task and return the final result. "
                    "Input: {\"result\": \"description of what was accomplished\"}"
                )
            else:
                metadata = self.TOOL_METADATA.get(tool_name, {})
                desc = metadata.get("description", "No description available")
                params = metadata.get("parameters", [])
                tools_descriptions.append(
                    f"{tool_name}: {desc}. Parameters: {params}"
                )
        
        tools_description = "\n".join([f"- {desc}" for desc in tools_descriptions])
        
        context_section = ""
        if context_snippets:
            context_section = "\n\nContext:\n" + "\n".join(context_snippets)
        
        history_section = ""
        if history:
            history_lines = []
            for h in history:
                step = h.get("step", "?")
                action = h.get("action", {})
                observation = h.get("observation", "")
                history_lines.append(f"Step {step}:")
                history_lines.append(f"  Action: {json.dumps(action)}")
                history_lines.append(f"  Observation: {observation}")
            history_section = "\n\nPrevious Actions:\n" + "\n".join(history_lines)
        
        prompt = f"""You are a ReAct agent that MUST respond with ONLY valid JSON. No other text is allowed.

CRITICAL: You must respond with ONLY a valid JSON object. DO NOT include any explanatory text, chain-of-thought reasoning, or anything other than the JSON object itself.

Task: {task}{context_section}{history_section}

Available Tools:
{tools_description}

REQUIRED Response Format (respond with ONLY this JSON, nothing else):
{{"action": "tool_name", "action_input": {{"param1": "value1", "param2": "value2"}}, "comment": "optional brief comment"}}

OR to finish:
{{"action": "finish", "action_input": {{"result": "description of what was accomplished"}}}}

Examples of VALID responses:
{{"action": "browse_page", "action_input": {{"url": "https://example.com"}}, "comment": "Gathering data from the website"}}
{{"action": "call_ai", "action_input": {{"platform": "gpt", "prompt": "Explain quantum computing", "task_type": "reasoning"}}, "comment": "Getting explanation"}}
{{"action": "finish", "action_input": {{"result": "Successfully completed the analysis"}}}}

Remember: Respond with ONLY valid JSON. No explanations, no thoughts, just the JSON object."""

        return prompt
    
    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON from LLM response.
        
        Args:
            text: The raw LLM response text
            
        Returns:
            Parsed JSON object or None if parsing fails
        """
        try:
            text = text.strip()
            
            json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
            matches = re.findall(json_pattern, text)
            
            if matches:
                for match in matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict) and "action" in parsed:
                            return parsed
                    except json.JSONDecodeError:
                        continue
            
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and "action" in parsed:
                    return parsed
            except json.JSONDecodeError:
                pass
            
            self.logger.warning(f"Could not extract valid JSON from: {text[:200]}...")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON: {str(e)}")
            return None
    
    def _validate_action(self, action_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an action object against available tools.
        
        Args:
            action_obj: The action object to validate
            
        Returns:
            Dictionary with 'valid' boolean and optional 'error' message
        """
        if not isinstance(action_obj, dict):
            return {"valid": False, "error": "Action must be a dictionary"}
        
        if "action" not in action_obj:
            return {"valid": False, "error": "Missing 'action' field"}
        
        action_name = action_obj.get("action")
        
        if action_name == "finish":
            if "action_input" not in action_obj:
                return {"valid": False, "error": "'finish' action requires 'action_input' with 'result'"}
            return {"valid": True}
        
        if action_name not in self.TOOLS:
            available = list(self.TOOLS.keys()) + ["finish"]
            return {
                "valid": False, 
                "error": f"Unknown action: {action_name}. Available actions: {available}"
            }
        
        if "action_input" not in action_obj:
            return {"valid": False, "error": f"Action '{action_name}' requires 'action_input'"}
        
        action_input = action_obj.get("action_input")
        if not isinstance(action_input, dict):
            return {"valid": False, "error": "'action_input' must be a dictionary"}
        
        return {"valid": True}
    
    def _execute(self, action_obj: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute a validated action.
        
        Args:
            action_obj: The action object to execute
            dry_run: If True, don't execute actions that modify state
            
        Returns:
            Execution result dictionary
        """
        action_name = action_obj.get("action")
        action_input = action_obj.get("action_input", {})
        
        if action_name in self.APPROVAL_REQUIRED_ACTIONS:
            self.logger.info(f"Action '{action_name}' requires approval")
            return {
                "status": "awaiting_approval",
                "entry": {
                    "action": action_name,
                    "input": action_input,
                    "dry_run": dry_run,
                    "timestamp": datetime.now().isoformat()
                }
            }
        
        if dry_run and action_name in ["run_code", "create_pr"]:
            action_input["dry_run"] = True
        
        try:
            self.logger.info(f"Executing action: {action_name}")
            result = self.tools_registry.execute_tool(action_name, action_input)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing action {action_name}: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _post_task_reflection(
        self, 
        task: str, 
        history: List[Dict[str, Any]], 
        result: str
    ) -> Dict[str, Any]:
        """
        Evaluate task success and generate insights for future improvement.
        
        Args:
            task: The original task
            history: Action-observation history
            result: The final result
            
        Returns:
            Reflection evaluation dictionary
        """
        try:
            self.logger.info("Performing post-task reflection")
            
            reflection_prompt = f"""Task: {task}
History: {json.dumps(history, indent=2)}
Result: {result}

Evaluate the task execution and return a JSON object with the following structure:
{{"success": true/false, "metrics": {{"steps_used": number, "efficiency": "low/medium/high"}}, "next_actions": ["suggestion1", "suggestion2"]}}

Respond with ONLY the JSON object, no other text."""

            platform = self._get_best_platform("evaluation and analysis")
            
            llm_response = self._call_llm(platform, reflection_prompt, "Task Reflection")
            
            if not llm_response.get("success"):
                self.logger.warning("Reflection LLM call failed, returning default evaluation")
                return {
                    "success": True,
                    "metrics": {"steps_used": len(history)},
                    "next_actions": []
                }
            
            response_text = llm_response.get("result", {}).get("response", "")
            evaluation = self._parse_json(response_text)
            
            if not evaluation:
                self.logger.warning("Failed to parse reflection JSON, using default")
                evaluation = {
                    "success": True,
                    "metrics": {"steps_used": len(history)},
                    "next_actions": []
                }
            
            memory_result = self.tools_registry.execute_tool("memory_store", {
                "platform": "react_agent",
                "subject": f"Task Reflection: {task[:50]}",
                "content": json.dumps({
                    "task": task,
                    "result": result,
                    "evaluation": evaluation
                }),
                "is_user": False
            })
            
            if memory_result.get("success"):
                self.logger.info("Stored reflection in memory system")
            
            if not evaluation.get("success") and evaluation.get("next_actions"):
                self.logger.info("Task was not fully successful, noting improvement actions")
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Error in post-task reflection: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "metrics": {},
                "next_actions": []
            }
    
    def _append_audit_log(self, entry: Dict[str, Any]) -> None:
        """
        Append an entry to the audit log (both in-memory and file).
        
        Args:
            entry: The audit log entry to append
        """
        try:
            self.audit_log.append(entry)
            
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(entry) + '\n')
            
            self.logger.debug(f"Audit log entry written: {entry.get('action', {}).get('action', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error appending to audit log: {str(e)}")
    
    def _get_best_platform(self, task: str) -> str:
        """
        Get the best AI platform for the given task.
        
        Args:
            task: The task description
            
        Returns:
            Platform name (e.g., "gpt", "claude", etc.)
        """
        try:
            recommendations = self.ai_controller.recommend_platform(
                prompt=task,
                task_type="reasoning"
            )
            
            if recommendations and len(recommendations) > 0:
                return recommendations[0]
            
            return "gpt"
            
        except Exception as e:
            self.logger.warning(f"Error getting platform recommendation: {str(e)}, using default")
            return "gpt"
    
    def _call_llm(self, platform: str, prompt: str, subject: str) -> Dict[str, Any]:
        """
        Call the LLM with the given prompt.
        
        Args:
            platform: The AI platform to use
            prompt: The prompt to send
            subject: Subject/title for the interaction
            
        Returns:
            LLM response dictionary
        """
        try:
            result = self.tools_registry.execute_tool("call_ai", {
                "platform": platform,
                "prompt": prompt,
                "task_type": "reasoning",
                "subject": subject,
                "goal": "ReAct Agent Reasoning"
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling LLM: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _gather_context(self, query: str) -> Dict[str, Any]:
        """
        Gather initial context using memory retrieval or other tools.
        
        Args:
            query: The context query
            
        Returns:
            Context result dictionary
        """
        try:
            result = self.tools_registry.execute_tool("memory_retrieve", {
                "subject": query,
                "limit": 5
            })
            
            if result.get("success"):
                conversations = result.get("conversations", [])
                if conversations:
                    context = f"Found {len(conversations)} relevant past conversations about: {query}"
                    return {"success": True, "context": context}
            
            return {"success": False, "context": ""}
            
        except Exception as e:
            self.logger.error(f"Error gathering context: {str(e)}")
            return {"success": False, "context": ""}
    
    def _format_observation(self, execution_result: Dict[str, Any]) -> str:
        """
        Format an execution result into a concise observation string.
        
        Args:
            execution_result: The result from executing an action
            
        Returns:
            Formatted observation string (truncated to 800 chars)
        """
        try:
            if not execution_result.get("success"):
                error = execution_result.get("error", "Unknown error")
                return f"Error: {error}"[:800]
            
            result_data = execution_result.get("result", execution_result)
            
            if isinstance(result_data, dict):
                observation = json.dumps(result_data, indent=2)
            else:
                observation = str(result_data)
            
            if len(observation) > 800:
                observation = observation[:797] + "..."
            
            return observation
            
        except Exception as e:
            return f"Error formatting observation: {str(e)}"[:800]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    agent = ReActAgent(max_steps=6)
    
    result = agent.run_task(
        task="Find out what the weather is like in San Francisco by browsing weather.com",
        dry_run=True
    )
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(json.dumps(result, indent=2))
