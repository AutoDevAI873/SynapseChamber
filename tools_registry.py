import logging
import traceback

logger = logging.getLogger(__name__)


class ToolsRegistry:
    """
    Central registry for all tools available to the ReAct agent.
    Provides a clean API for tool discovery, execution, and error handling.
    """
    
    def __init__(self, flask_app_context=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Tools Registry...")
        self.flask_app_context = flask_app_context
        
        try:
            from browser_automation import BrowserAutomation
            from captcha_solver import CAPTCHASolver
            from file_ops import FileOperations
            
            self.browser_automation = BrowserAutomation()
            self.captcha_solver = CAPTCHASolver()
            self.file_ops = FileOperations()
            
            if flask_app_context:
                with flask_app_context():
                    from memory_system import MemorySystem
                    from ai_controller import AIController
                    from training_engine import TrainingSessionManager
                    
                    self.memory_system = MemorySystem()
                    self.ai_controller = AIController(
                        browser_automation=self.browser_automation,
                        captcha_solver=self.captcha_solver,
                        memory_system=self.memory_system
                    )
                    self.training_manager = TrainingSessionManager(
                        ai_controller=self.ai_controller,
                        memory_system=self.memory_system
                    )
            else:
                self.memory_system = None
                self.ai_controller = None
                self.training_manager = None
                self.logger.warning("Flask app context not provided - database-dependent modules will be unavailable")
            
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing modules: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise
        
        self.tools = self._build_tools()
        self.tool_metadata = self._build_metadata()
        
        self.logger.info(f"Tools Registry initialized with {len(self.tools)} tools")
    
    def _build_tools(self):
        """Build the TOOLS dictionary with lambda functions for each tool"""
        return {
            "call_ai": lambda payload: self._call_ai(payload),
            "recommend_platform": lambda payload: self._recommend_platform(payload),
            "browse_page": lambda payload: self._browse_page(payload),
            "solve_captcha": lambda payload: self._solve_captcha(payload),
            "run_training_cycle": lambda payload: self._run_training_cycle(payload),
            "memory_store": lambda payload: self._memory_store(payload),
            "memory_retrieve": lambda payload: self._memory_retrieve(payload),
            "propose_code_patch": lambda payload: self._propose_code_patch(payload),
            "run_code": lambda payload: self._run_code(payload),
            "create_pr": lambda payload: self._create_pr(payload),
        }
    
    def _build_metadata(self):
        """Build the TOOL_METADATA dictionary with descriptions and requirements"""
        return {
            "call_ai": {
                "description": "Call an AI platform with a prompt and get a response",
                "requires_approval": False,
                "parameters": ["platform", "prompt", "task_type", "subject", "goal"]
            },
            "recommend_platform": {
                "description": "Get the best AI platform recommendation for a given task type",
                "requires_approval": False,
                "parameters": ["prompt", "task_type"]
            },
            "browse_page": {
                "description": "Navigate to a URL using browser automation",
                "requires_approval": False,
                "parameters": ["url"]
            },
            "solve_captcha": {
                "description": "Attempt to solve a CAPTCHA challenge using the browser driver",
                "requires_approval": False,
                "parameters": ["captcha_type"]
            },
            "run_training_cycle": {
                "description": "Start an AI training session on a specific topic with multiple platforms",
                "requires_approval": False,
                "parameters": ["topic", "mode", "platforms", "goal"]
            },
            "memory_store": {
                "description": "Store a conversation or memory entry in the memory system",
                "requires_approval": False,
                "parameters": ["conversation_id", "content", "is_user", "screenshot_path"]
            },
            "memory_retrieve": {
                "description": "Retrieve relevant memories or conversation history from the memory system",
                "requires_approval": False,
                "parameters": ["conversation_id", "platform", "subject", "limit"]
            },
            "propose_code_patch": {
                "description": "Analyze a file and generate a code patch suggestion based on a hint",
                "requires_approval": False,
                "parameters": ["file_path", "patch_hint"]
            },
            "run_code": {
                "description": "Execute Python code safely in a subprocess with timeout",
                "requires_approval": True,
                "parameters": ["code_str", "timeout", "dry_run"]
            },
            "create_pr": {
                "description": "Create a git branch and commit changes (simulated PR creation)",
                "requires_approval": True,
                "parameters": ["branch_name", "title", "diff_content", "dry_run"]
            },
        }
    
    def _call_ai(self, payload):
        """
        Call an AI platform with a prompt
        
        Expected payload:
        {
            "platform": str (e.g., "gpt", "claude", "gemini", "deepseek", "grok"),
            "prompt": str,
            "task_type": str (optional),
            "subject": str (optional),
            "goal": str (optional)
        }
        """
        try:
            if not self.ai_controller:
                return {
                    "success": False,
                    "error": "AI controller not available (Flask app context required)"
                }
            
            platform = payload.get("platform")
            prompt = payload.get("prompt")
            task_type = payload.get("task_type")
            subject = payload.get("subject", "AI Interaction")
            goal = payload.get("goal", "Get AI response")
            
            if not platform:
                return {
                    "success": False,
                    "error": "Missing required parameter: platform"
                }
            
            if not prompt:
                return {
                    "success": False,
                    "error": "Missing required parameter: prompt"
                }
            
            self.logger.info(f"Calling AI platform: {platform} with prompt: {prompt[:50]}...")
            
            result = self.ai_controller.call_platform(
                platform=platform,
                prompt=prompt,
                task_type=task_type,
                subject=subject,
                goal=goal
            )
            
            return {
                "success": result.get("status") == "success",
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in call_ai: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _recommend_platform(self, payload):
        """
        Get platform recommendation for a task
        
        Expected payload:
        {
            "prompt": str,
            "task_type": str (optional)
        }
        """
        try:
            if not self.ai_controller:
                return {
                    "success": False,
                    "error": "AI controller not available (Flask app context required)"
                }
            
            prompt = payload.get("prompt", "")
            task_type = payload.get("task_type")
            
            self.logger.info(f"Recommending platform for task_type: {task_type}")
            
            recommendations = self.ai_controller.recommend_platform(
                prompt=prompt,
                task_type=task_type
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "best_platform": recommendations[0] if recommendations else None
            }
            
        except Exception as e:
            self.logger.error(f"Error in recommend_platform: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _browse_page(self, payload):
        """
        Navigate to a URL and extract content
        
        Expected payload:
        {
            "url": str
        }
        """
        try:
            url = payload.get("url")
            
            if not url:
                return {
                    "success": False,
                    "error": "Missing required parameter: url"
                }
            
            self.logger.info(f"Browsing page: {url}")
            
            navigate_success = self.browser_automation.navigate_to(url)
            
            if not navigate_success:
                return {
                    "success": False,
                    "error": f"Failed to navigate to {url}"
                }
            
            current_url = self.browser_automation.driver.current_url if self.browser_automation.driver else url
            
            page_source = ""
            if self.browser_automation.driver:
                try:
                    page_source = self.browser_automation.driver.page_source
                except Exception as e:
                    self.logger.warning(f"Could not get page source: {str(e)}")
            
            return {
                "success": True,
                "url": url,
                "current_url": current_url,
                "content": page_source[:5000] if page_source else "",
                "content_length": len(page_source) if page_source else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error in browse_page: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _solve_captcha(self, payload):
        """
        Solve CAPTCHA challenge
        
        Expected payload:
        {
            "captcha_type": str ("recaptcha", "cloudflare", "text")
        }
        """
        try:
            captcha_type = payload.get("captcha_type", "recaptcha")
            
            if not self.browser_automation.driver:
                return {
                    "success": False,
                    "error": "Browser driver not initialized"
                }
            
            self.logger.info(f"Attempting to solve {captcha_type} CAPTCHA")
            
            if captcha_type == "recaptcha":
                result = self.captcha_solver.solve_recaptcha(self.browser_automation.driver)
            elif captcha_type == "cloudflare":
                result = self.captcha_solver.solve_cloudflare(self.browser_automation.driver)
            elif captcha_type == "text":
                return {
                    "success": False,
                    "error": "Text CAPTCHA requires image_element parameter"
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown CAPTCHA type: {captcha_type}"
                }
            
            return {
                "success": result,
                "captcha_type": captcha_type,
                "solved": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in solve_captcha: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _run_training_cycle(self, payload):
        """
        Run a training cycle with multiple AI platforms
        
        Expected payload:
        {
            "topic": str,
            "mode": str ("all_ais_train" or "single_ai_teaches"),
            "platforms": list (optional),
            "goal": str (optional)
        }
        """
        try:
            topic = payload.get("topic")
            mode = payload.get("mode", "all_ais_train")
            platforms = payload.get("platforms")
            goal = payload.get("goal")
            
            if not topic:
                return {
                    "success": False,
                    "error": "Missing required parameter: topic"
                }
            
            self.logger.info(f"Starting training cycle: topic={topic}, mode={mode}")
            
            session_info = self.training_manager.start_session(
                topic=topic,
                mode=mode,
                platforms=platforms,
                goal=goal
            )
            
            return {
                "success": True,
                "session": session_info
            }
            
        except Exception as e:
            self.logger.error(f"Error in run_training_cycle: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _memory_store(self, payload):
        """
        Store a memory or message in the memory system
        
        Expected payload:
        {
            "conversation_id": int (optional - will create new if not provided),
            "platform": str (required if creating new conversation),
            "content": str,
            "is_user": bool (default: True),
            "screenshot_path": str (optional)
        }
        """
        try:
            conversation_id = payload.get("conversation_id")
            platform = payload.get("platform", "system")
            content = payload.get("content")
            is_user = payload.get("is_user", True)
            screenshot_path = payload.get("screenshot_path")
            
            if not content:
                return {
                    "success": False,
                    "error": "Missing required parameter: content"
                }
            
            if not conversation_id:
                subject = payload.get("subject", "Memory Entry")
                goal = payload.get("goal", "Store memory")
                conversation_id = self.memory_system.create_conversation(
                    platform=platform,
                    subject=subject,
                    goal=goal
                )
            
            self.logger.info(f"Storing memory in conversation {conversation_id}")
            
            success = self.memory_system.add_message(
                conversation_id=conversation_id,
                content=content,
                is_user=is_user,
                screenshot_path=screenshot_path
            )
            
            return {
                "success": success,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in memory_store: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _memory_retrieve(self, payload):
        """
        Retrieve memories or conversation history
        
        Expected payload:
        {
            "conversation_id": int (optional),
            "platform": str (optional),
            "subject": str (optional),
            "limit": int (optional, default: 10)
        }
        """
        try:
            conversation_id = payload.get("conversation_id")
            platform = payload.get("platform")
            subject = payload.get("subject")
            limit = payload.get("limit", 10)
            
            self.logger.info(f"Retrieving memories: conv_id={conversation_id}, platform={platform}, subject={subject}")
            
            if conversation_id:
                conversation = self.memory_system.get_conversation(conversation_id)
                if not conversation:
                    return {
                        "success": False,
                        "error": f"Conversation {conversation_id} not found"
                    }
                return {
                    "success": True,
                    "conversation": conversation,
                    "count": 1
                }
            else:
                conversations = self.memory_system.get_conversations(
                    platform=platform,
                    subject=subject,
                    limit=limit
                )
                
                return {
                    "success": True,
                    "conversations": conversations,
                    "count": len(conversations)
                }
            
        except Exception as e:
            self.logger.error(f"Error in memory_retrieve: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _propose_code_patch(self, payload):
        """
        Generate a code patch suggestion
        
        Expected payload:
        {
            "file_path": str,
            "patch_hint": str
        }
        """
        try:
            file_path = payload.get("file_path")
            patch_hint = payload.get("patch_hint")
            
            if not file_path:
                return {
                    "success": False,
                    "error": "Missing required parameter: file_path"
                }
            
            if not patch_hint:
                return {
                    "success": False,
                    "error": "Missing required parameter: patch_hint"
                }
            
            self.logger.info(f"Generating patch for {file_path} with hint: {patch_hint[:50]}...")
            
            result = self.file_ops.generate_patch(
                file_path=file_path,
                patch_hint=patch_hint
            )
            
            return {
                "success": "error" not in result,
                "patch": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in propose_code_patch: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _run_code(self, payload):
        """
        Execute Python code safely
        
        Expected payload:
        {
            "code_str": str,
            "timeout": int (optional, default: 30),
            "dry_run": bool (optional, default: False)
        }
        """
        try:
            code_str = payload.get("code_str")
            timeout = payload.get("timeout", 30)
            dry_run = payload.get("dry_run", False)
            
            if not code_str:
                return {
                    "success": False,
                    "error": "Missing required parameter: code_str"
                }
            
            self.logger.info(f"Executing code (dry_run={dry_run}, timeout={timeout})")
            
            result = self.file_ops.safe_run_code(
                code_str=code_str,
                timeout=timeout,
                dry_run=dry_run
            )
            
            return {
                "success": result.get("success", False),
                "execution": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in run_code: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _create_pr(self, payload):
        """
        Create a git branch and commit changes
        
        Expected payload:
        {
            "branch_name": str,
            "title": str,
            "diff_content": str,
            "dry_run": bool (optional, default: True)
        }
        """
        try:
            branch_name = payload.get("branch_name")
            title = payload.get("title")
            diff_content = payload.get("diff_content", "")
            dry_run = payload.get("dry_run", True)
            
            if not branch_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: branch_name"
                }
            
            if not title:
                return {
                    "success": False,
                    "error": "Missing required parameter: title"
                }
            
            self.logger.info(f"Creating PR: branch={branch_name}, dry_run={dry_run}")
            
            result = self.file_ops.git_create_pr(
                branch_name=branch_name,
                title=title,
                diff_content=diff_content,
                dry_run=dry_run
            )
            
            return {
                "success": result.get("success", False),
                "pr": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in create_pr: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def execute_tool(self, tool_name, payload):
        """
        Execute a tool by name with the given payload
        
        Args:
            tool_name (str): Name of the tool to execute
            payload (dict): Parameters for the tool
            
        Returns:
            dict: Tool execution result
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        metadata = self.tool_metadata.get(tool_name, {})
        requires_approval = metadata.get("requires_approval", False)
        
        if requires_approval:
            self.logger.warning(f"Tool '{tool_name}' requires approval before execution")
        
        try:
            return self.tools[tool_name](payload)
        except Exception as e:
            self.logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def get_tool_info(self, tool_name=None):
        """
        Get information about available tools
        
        Args:
            tool_name (str, optional): Specific tool name, or None for all tools
            
        Returns:
            dict: Tool information
        """
        if tool_name:
            if tool_name not in self.tool_metadata:
                return {
                    "error": f"Unknown tool: {tool_name}"
                }
            return {
                "name": tool_name,
                "metadata": self.tool_metadata[tool_name]
            }
        else:
            return {
                "tools": list(self.tools.keys()),
                "metadata": self.tool_metadata,
                "count": len(self.tools)
            }


TOOLS = None
TOOL_METADATA = None


def initialize_tools_registry():
    """Initialize the global tools registry"""
    global TOOLS, TOOL_METADATA
    
    try:
        registry = ToolsRegistry()
        TOOLS = registry.tools
        TOOL_METADATA = registry.tool_metadata
        
        logger.info("Tools registry initialized successfully")
        logger.info(f"Available tools: {list(TOOLS.keys())}")
        
        return registry
        
    except Exception as e:
        logger.error(f"Failed to initialize tools registry: {str(e)}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    print("Tools Registry module should be used within Flask app context.")
    print("See test_tools_registry.py for usage example.")
