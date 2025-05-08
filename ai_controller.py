import logging
import time
import datetime
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AIController:
    def __init__(self, browser_automation, captcha_solver, memory_system):
        self.logger = logging.getLogger(__name__)
        self.browser = browser_automation
        self.captcha_solver = captcha_solver
        self.memory_system = memory_system
        
        # Platform synergy tracking
        self.platform_strengths = {
            "gpt": {
                "coding": 0.85,
                "reasoning": 0.90,
                "creativity": 0.80,
                "technical_precision": 0.85,
                "instruction_following": 0.87
            },
            "gemini": {
                "coding": 0.82,
                "reasoning": 0.88,
                "creativity": 0.83,
                "technical_precision": 0.80,
                "multimodal": 0.92
            },
            "deepseek": {
                "coding": 0.90,
                "reasoning": 0.85,
                "creativity": 0.75,
                "technical_precision": 0.92,
                "problem_solving": 0.88
            },
            "claude": {
                "coding": 0.80,
                "reasoning": 0.92,
                "creativity": 0.85,
                "safety": 0.95,
                "instruction_following": 0.90
            },
            "grok": {
                "coding": 0.80,
                "reasoning": 0.82,
                "creativity": 0.88,
                "technical_precision": 0.78,
                "problem_solving": 0.84
            }
        }
        
        # Track platform performance over time
        self.platform_performance_history = {}
        
        # Cross-platform synergy metrics
        self.cross_platform_synergy = {
            ("gpt", "claude"): 0.85,
            ("gpt", "gemini"): 0.80,
            ("gpt", "deepseek"): 0.82,
            ("gpt", "grok"): 0.75,
            ("claude", "gemini"): 0.78,
            ("claude", "deepseek"): 0.80,
            ("claude", "grok"): 0.76,
            ("gemini", "deepseek"): 0.77,
            ("gemini", "grok"): 0.75,
            ("deepseek", "grok"): 0.72
        }
        
        # Topic specialization mapping
        self.topic_specializations = {
            "code_generation": ["deepseek", "gpt", "claude"],
            "debug_assistance": ["deepseek", "gpt", "claude"],
            "algorithm_design": ["deepseek", "gpt", "claude"],
            "creative_writing": ["claude", "gpt", "gemini"],
            "safety_critical": ["claude", "gemini"],
            "data_analysis": ["gpt", "gemini", "deepseek"],
            "reasoning": ["claude", "gpt", "gemini"],
            "multimodal": ["gemini", "gpt"],
            "problem_solving": ["deepseek", "claude", "gpt"]
        }
        
        # Predefined fallback responses for when browser automation fails
        self.fallback_responses = {
            "gpt": "I'm sorry, I couldn't connect to OpenAI's ChatGPT at the moment due to technical issues. Please try again later or consider trying a different AI platform.",
            "gemini": "I'm sorry, I couldn't connect to Google's Gemini at the moment due to technical issues. Please try again later or consider trying a different AI platform.",
            "deepseek": "I'm sorry, I couldn't connect to DeepSeek at the moment due to technical issues. Please try again later or consider trying a different AI platform.",
            "claude": "I'm sorry, I couldn't connect to Anthropic's Claude at the moment due to technical issues. Please try again later or consider trying a different AI platform.",
            "grok": "I'm sorry, I couldn't connect to Grok at the moment due to technical issues. Please try again later or consider trying a different AI platform."
        }
        
        # AI Platform configurations
        self.platforms = {
            "gpt": {
                "url": "https://chat.openai.com/",
                "login_required": True,
                "selectors": {
                    "login_button": (By.XPATH, "//button[contains(text(), 'Log in')]"),
                    "email_input": (By.ID, "username"),
                    "password_input": (By.ID, "password"),
                    "continue_button": (By.XPATH, "//button[contains(text(), 'Continue')]"),
                    "prompt_input": (By.CSS_SELECTOR, "textarea[data-id='root']"),
                    "submit_button": (By.CSS_SELECTOR, "button[data-testid='send-button']"),
                    "response_element": (By.CSS_SELECTOR, ".markdown"),
                    "new_chat_button": (By.XPATH, "//a[contains(text(), 'New chat')]")
                }
            },
            "gemini": {
                "url": "https://gemini.google.com/",
                "login_required": True,
                "selectors": {
                    "login_button": (By.XPATH, "//a[contains(text(), 'Sign in')]"),
                    "email_input": (By.CSS_SELECTOR, "input[type='email']"),
                    "password_input": (By.CSS_SELECTOR, "input[type='password']"),
                    "next_button": (By.XPATH, "//span[text()='Next']/parent::button"),
                    "prompt_input": (By.CSS_SELECTOR, "textarea[placeholder='Message Gemini']"),
                    "submit_button": (By.XPATH, "//button[@aria-label='Send message']"),
                    "response_element": (By.CSS_SELECTOR, ".message-content")
                }
            },
            "deepseek": {
                "url": "https://chat.deepseek.com/",
                "login_required": True,
                "selectors": {
                    "login_button": (By.XPATH, "//span[contains(text(), 'Sign In')]/parent::button"),
                    "email_input": (By.CSS_SELECTOR, "input[type='email']"),
                    "password_input": (By.CSS_SELECTOR, "input[type='password']"),
                    "sign_in_button": (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                    "prompt_input": (By.CSS_SELECTOR, "textarea[placeholder='Message DeepSeek']"),
                    "submit_button": (By.XPATH, "//button[@type='submit']"),
                    "response_element": (By.CSS_SELECTOR, ".markdown-container")
                }
            },
            "claude": {
                "url": "https://claude.ai/",
                "login_required": True,
                "selectors": {
                    "login_button": (By.XPATH, "//button[contains(text(), 'Sign in')]"),
                    "email_input": (By.CSS_SELECTOR, "input[type='email']"),
                    "continue_button": (By.XPATH, "//button[contains(text(), 'Continue')]"),
                    "prompt_input": (By.CSS_SELECTOR, "div[contenteditable='true']"),
                    "submit_button": (By.XPATH, "//button[@aria-label='Send message']"),
                    "response_element": (By.CSS_SELECTOR, ".message.assistant")
                }
            },
            "grok": {
                "url": "https://grok.x.ai/",
                "login_required": True,
                "selectors": {
                    "login_button": (By.XPATH, "//span[contains(text(), 'Log in')]/parent::button"),
                    "email_input": (By.CSS_SELECTOR, "input[name='username']"),
                    "password_input": (By.CSS_SELECTOR, "input[name='password']"),
                    "login_submit": (By.XPATH, "//span[contains(text(), 'Log in')]/parent::button"),
                    "prompt_input": (By.CSS_SELECTOR, "textarea[placeholder='Ask me anything...']"),
                    "submit_button": (By.XPATH, "//button[@aria-label='Send message']"),
                    "response_element": (By.CSS_SELECTOR, ".message-content")
                }
            }
        }
    
    def recommend_platform(self, prompt, task_type=None):
        """
        Recommend the best AI platform for a given prompt and task type
        
        Args:
            prompt (str): The prompt to be sent to the AI
            task_type (str, optional): Type of task (coding, reasoning, creativity, etc.)
            
        Returns:
            list: Ranked list of platform recommendations
        """
        # Extract keywords from prompt to determine task type if not provided
        if not task_type:
            task_type = self._detect_task_type(prompt)
            
        # If task is a known topic specialization, use predefined ranking
        if task_type in self.topic_specializations:
            return self.topic_specializations[task_type]
            
        # Else, rank platforms based on their strength for the task type
        rankings = []
        for platform, strengths in self.platform_strengths.items():
            # Calculate score for this platform based on relevant strengths
            if task_type in strengths:
                score = strengths[task_type]
            else:
                # Use average of strengths if specific task type not found
                score = sum(strengths.values()) / len(strengths)
            
            rankings.append((platform, score))
            
        # Sort by score (highest first)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the platform names in ranked order
        return [r[0] for r in rankings]
    
    def _detect_task_type(self, prompt):
        """
        Detect the type of task from a prompt
        
        Args:
            prompt (str): The prompt to analyze
            
        Returns:
            str: Detected task type
        """
        prompt_lower = prompt.lower()
        
        # Check for coding tasks
        if any(keyword in prompt_lower for keyword in ['code', 'function', 'class', 'program', 'algorithm', 'implement']):
            return 'coding'
            
        # Check for creative tasks
        if any(keyword in prompt_lower for keyword in ['write', 'create', 'generate', 'story', 'article', 'poem']):
            return 'creativity'
            
        # Check for reasoning tasks
        if any(keyword in prompt_lower for keyword in ['explain', 'why', 'analyze', 'understand', 'reason']):
            return 'reasoning'
            
        # Check for technical precision tasks
        if any(keyword in prompt_lower for keyword in ['technical', 'precise', 'exact', 'detail', 'specification']):
            return 'technical_precision'
            
        # Check for problem-solving tasks
        if any(keyword in prompt_lower for keyword in ['solve', 'solution', 'problem', 'fix', 'debug', 'error']):
            return 'problem_solving'
            
        # Default to reasoning as a general-purpose category
        return 'reasoning'
    
    def update_platform_performance(self, platform, task_type, success_score):
        """
        Update platform performance metrics based on interaction results
        
        Args:
            platform (str): The AI platform used
            task_type (str): Type of task attempted
            success_score (float): Success score (0.0-1.0)
            
        Returns:
            dict: Updated performance metrics
        """
        # Initialize platform history if needed
        if platform not in self.platform_performance_history:
            self.platform_performance_history[platform] = {
                'total_interactions': 0,
                'success_rate': 0.0,
                'task_success': {},
                'recent_scores': []
            }
            
        # Update platform history
        history = self.platform_performance_history[platform]
        history['total_interactions'] += 1
        
        # Update task-specific success rate
        if task_type not in history['task_success']:
            history['task_success'][task_type] = {
                'attempts': 0,
                'success_rate': 0.0
            }
            
        task_history = history['task_success'][task_type]
        task_history['attempts'] += 1
        
        # Update rolling average (last 10 attempts)
        task_history['success_rate'] = ((task_history['success_rate'] * (task_history['attempts'] - 1)) + 
                                        success_score) / task_history['attempts']
        
        # Add to recent scores (keep last 10)
        history['recent_scores'].append((task_type, success_score, time.time()))
        if len(history['recent_scores']) > 10:
            history['recent_scores'].pop(0)
            
        # Update overall success rate
        recent_scores = [score for _, score, _ in history['recent_scores']]
        history['success_rate'] = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        # Update platform strength based on performance
        if platform in self.platform_strengths and task_type in self.platform_strengths[platform]:
            current_strength = self.platform_strengths[platform][task_type]
            # Gradual adaptation: 90% previous strength, 10% new performance
            self.platform_strengths[platform][task_type] = (current_strength * 0.9) + (success_score * 0.1)
            
        return history

    def interact_with_ai(self, platform, prompt, subject=None, goal=None, task_type=None):
        """
        Main method to interact with an AI platform
        
        Args:
            platform (str): The AI platform to use
            prompt (str): The prompt to send
            subject (str, optional): Subject of the conversation
            goal (str, optional): Goal of the interaction
            task_type (str, optional): Type of task (coding, reasoning, etc.)
            
        Returns:
            dict: Conversation data
        """
        if platform not in self.platforms:
            raise ValueError(f"Unsupported AI platform: {platform}")
        
        # Detect task type if not provided
        if not task_type:
            task_type = self._detect_task_type(prompt)
            
        # Check if this platform is optimal for the task
        platform_ranking = self.recommend_platform(prompt, task_type)
        is_optimal = platform == platform_ranking[0]
        
        if not is_optimal:
            self.logger.info(f"Note: {platform} is ranked #{platform_ranking.index(platform)+1} for {task_type} tasks. "
                            f"Consider using {platform_ranking[0]} for optimal results.")
        
        platform_config = self.platforms[platform]
        
        try:
            # Initialize a new browser if needed
            if self.browser.driver is None:
                driver = self.browser.initialize_driver()
                if driver is None:
                    # Return simulated response if browser fails to initialize
                    self.logger.warning("Browser failed to initialize, returning simulated response")
                    return self._generate_fallback_response(platform, prompt, task_type)
            
            # Create a new conversation in the memory system
            conversation_id = self.memory_system.create_conversation(platform, subject, goal)
            
            # Store task context in memory
            context_data = {
                "platform": platform,
                "task_type": task_type,
                "is_optimal_platform": is_optimal,
                "platform_ranking": platform_ranking,
                "prompt_length": len(prompt),
                "timestamp": time.time()
            }
            
            self.memory_system.store_context(f"task_context_{conversation_id}", context_data)
            
            # Try to navigate to the platform; use fallback if it fails
            if not self.browser.navigate_to(platform_config["url"]):
                self.logger.warning(f"Failed to navigate to {platform}, returning simulated response")
                return self._generate_fallback_response(platform, prompt, task_type)
            
            # Handle login if required
            if platform_config["login_required"]:
                if not self._handle_login(platform):
                    self.logger.warning(f"Failed to log in to {platform}, returning simulated response")
                    return self._generate_fallback_response(platform, prompt, task_type)
            
            # Handle any CAPTCHA challenges
            self._check_for_captcha()
            
            # Send the prompt to the AI
            result = self._send_prompt(platform, prompt, conversation_id)
            
            # Update platform performance metrics if successful
            if result.get("status") == "success":
                # Simple success score of 1.0 for successful completions
                self.update_platform_performance(platform, task_type, 1.0)
            else:
                # Lower score for errors
                self.update_platform_performance(platform, task_type, 0.3)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error interacting with {platform}: {str(e)}")
            self.logger.error(traceback.format_exc())
            screenshot_path = self.browser.take_screenshot(f"error_{platform}_{int(time.time())}")
            
            # Update metrics for failure
            self.update_platform_performance(platform, task_type, 0.0)
            
            return {
                "status": "error",
                "message": str(e),
                "screenshot": screenshot_path
            }
    
    def _handle_login(self, platform):
        """Handle login process for the specified platform"""
        self.logger.info(f"Handling login for {platform}")
        
        platform_config = self.platforms[platform]
        selectors = platform_config["selectors"]
        
        # Check if we're already logged in
        # This is a simplified check and might need to be adjusted per platform
        if self._is_logged_in(platform):
            self.logger.info(f"Already logged in to {platform}")
            return True
        
        try:
            # Click login button if it exists
            if "login_button" in selectors:
                login_button = self.browser.find_element(*selectors["login_button"])
                if login_button:
                    self.browser.click_element(*selectors["login_button"])
            
            # Handle email input
            if "email_input" in selectors:
                # In a real implementation, you'd get these from a secure storage
                email = "example@example.com"  # Placeholder
                self.browser.send_keys(*selectors["email_input"], email)
                
                # Some platforms have a continue button after email
                if "continue_button" in selectors:
                    self.browser.click_element(*selectors["continue_button"])
            
            # Handle password input
            if "password_input" in selectors:
                password = "password123"  # Placeholder
                self.browser.send_keys(*selectors["password_input"], password)
            
            # Click sign in/login submit button
            submit_selector = None
            for key in ["sign_in_button", "login_submit", "next_button", "continue_button"]:
                if key in selectors:
                    submit_selector = selectors[key]
                    break
            
            if submit_selector:
                self.browser.click_element(*submit_selector)
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            return self._is_logged_in(platform)
            
        except Exception as e:
            self.logger.error(f"Login error for {platform}: {str(e)}")
            return False
    
    def _is_logged_in(self, platform):
        """Check if we're logged in to the specified platform"""
        # This is a simplified check and should be customized per platform
        platform_config = self.platforms[platform]
        
        # Look for elements that indicate we're logged in
        try:
            if platform == "gpt":
                # ChatGPT shows a "New chat" button when logged in
                return bool(self.browser.find_element(By.XPATH, "//a[contains(text(), 'New chat')]"))
            elif platform == "gemini":
                # Gemini shows the prompt input when logged in
                return bool(self.browser.find_element(*platform_config["selectors"]["prompt_input"]))
            elif platform == "deepseek":
                # DeepSeek shows the prompt input when logged in
                return bool(self.browser.find_element(*platform_config["selectors"]["prompt_input"]))
            elif platform == "claude":
                # Claude shows the prompt input when logged in
                return bool(self.browser.find_element(*platform_config["selectors"]["prompt_input"]))
            elif platform == "grok":
                # Grok shows the prompt input when logged in
                return bool(self.browser.find_element(*platform_config["selectors"]["prompt_input"]))
            
            # Default to checking if the prompt input exists
            return bool(self.browser.find_element(*platform_config["selectors"]["prompt_input"]))
            
        except (TimeoutException, NoSuchElementException):
            return False
        except Exception as e:
            self.logger.error(f"Error checking login status for {platform}: {str(e)}")
            return False
    
    def _check_for_captcha(self):
        """Check and handle any CAPTCHA challenges"""
        try:
            # Check for reCAPTCHA
            recaptcha_frames = self.browser.driver.find_elements(By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")
            if recaptcha_frames:
                self.logger.info("reCAPTCHA detected")
                return self.captcha_solver.solve_recaptcha(self.browser.driver)
            
            # Check for Cloudflare challenge
            cloudflare_elements = self.browser.driver.find_elements(By.CSS_SELECTOR, "#cf-please-wait, #cf-spinner")
            if cloudflare_elements:
                self.logger.info("Cloudflare challenge detected")
                return self.captcha_solver.solve_cloudflare(self.browser.driver)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking for CAPTCHA: {str(e)}")
            return False
    
    def _send_prompt(self, platform, prompt, conversation_id):
        """Send a prompt to the AI and get the response"""
        self.logger.info(f"Sending prompt to {platform}: {prompt[:50]}...")
        
        platform_config = self.platforms[platform]
        selectors = platform_config["selectors"]
        
        try:
            # Find and click on the prompt input
            prompt_input = self.browser.find_element(*selectors["prompt_input"])
            if not prompt_input:
                raise ValueError(f"Could not find prompt input element for {platform}")
            
            # Send the prompt
            self.browser.send_keys(*selectors["prompt_input"], prompt)
            
            # Take a screenshot before sending
            pre_submit_screenshot = self.browser.take_screenshot(f"{platform}_pre_submit_{int(time.time())}")
            
            # Add the user message to the conversation
            self.memory_system.add_message(conversation_id, prompt, is_user=True, screenshot_path=pre_submit_screenshot)
            
            # Click submit button
            self.browser.click_element(*selectors["submit_button"])
            
            # Wait for the response to appear
            self._wait_for_response(platform)
            
            # Get the response
            response = self._extract_response(platform)
            
            # Take a screenshot after receiving response
            post_response_screenshot = self.browser.take_screenshot(f"{platform}_post_response_{int(time.time())}")
            
            # Add the AI response to the conversation
            self.memory_system.add_message(conversation_id, response, is_user=False, screenshot_path=post_response_screenshot)
            
            return {
                "status": "success",
                "platform": platform,
                "prompt": prompt,
                "response": response,
                "conversation_id": conversation_id,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error sending prompt to {platform}: {str(e)}")
            error_screenshot = self.browser.take_screenshot(f"{platform}_error_{int(time.time())}")
            
            # Add the error to the conversation
            error_message = f"Error: {str(e)}"
            self.memory_system.add_message(conversation_id, error_message, is_user=False, screenshot_path=error_screenshot)
            
            return {
                "status": "error",
                "message": str(e),
                "conversation_id": conversation_id,
                "screenshot": error_screenshot
            }
    
    def _wait_for_response(self, platform):
        """Wait for the AI to generate a response"""
        platform_config = self.platforms[platform]
        response_selector = platform_config["selectors"]["response_element"]
        
        # Wait for the response element to appear
        try:
            WebDriverWait(self.browser.driver, 60).until(
                EC.presence_of_element_located(response_selector)
            )
            
            # Some platforms have loading indicators while generating
            if platform == "gpt":
                # Wait for the "Regenerate" button to appear, indicating generation is complete
                try:
                    regenerate_button = (By.XPATH, "//button[contains(text(), 'Regenerate')]")
                    WebDriverWait(self.browser.driver, 60).until(
                        EC.presence_of_element_located(regenerate_button)
                    )
                except TimeoutException:
                    # If no regenerate button appears, wait a bit more for the response to complete
                    time.sleep(10)
            
            # For other platforms, wait a bit for the response to complete
            time.sleep(3)
            
            return True
            
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for {platform} response")
            return False
    
    def _extract_response(self, platform):
        """Extract the AI's response from the page"""
        platform_config = self.platforms[platform]
        response_selector = platform_config["selectors"]["response_element"]
        
        try:
            # Find all response elements (there might be multiple)
            response_elements = self.browser.driver.find_elements(*response_selector)
            
            if not response_elements:
                return "No response found"
            
            # Get the text from the last response element
            response_text = response_elements[-1].text
            
            # Clean up the response if needed
            response_text = response_text.strip()
            
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error extracting response from {platform}: {str(e)}")
            return f"Error extracting response: {str(e)}"
            
    def _generate_fallback_response(self, platform, prompt):
        """Generate a fallback response when browser automation fails"""
        self.logger.info(f"Generating detailed fallback response for {platform}")
        
        # Take a screenshot to capture the current state
        screenshot_path = self.browser.take_screenshot(f"fallback_{platform}_{int(time.time())}")
        
        # Create a conversation in memory system to track the attempt
        conversation_id = self.memory_system.create_conversation(
            platform, 
            f"Fallback interaction with {platform}", 
            "Generated response due to browser automation failure"
        )
        
        # Store the user prompt
        self.memory_system.add_message(conversation_id, prompt, is_user=True)
        
        # Create more detailed and context-specific fallback messages based on platform and failure type
        enhanced_fallbacks = {
            "gpt": {
                "navigation": "Unable to access ChatGPT (chat.openai.com). The site may be experiencing high traffic, undergoing maintenance, or have connection restrictions. Browser automation was unable to load the page properly.",
                "login": "Unable to authenticate with ChatGPT. This could be due to changed login flows, CAPTCHA challenges, or account session issues. The system needs valid credentials to proceed.",
                "interaction": "Connected to ChatGPT but encountered an issue with the chat interface. The site layout may have changed, or there might be a problem with the prompt submission mechanism.",
                "response": "ChatGPT was accessible, but we couldn't properly retrieve its response. This may be due to changes in the response format or interface elements."
            },
            "claude": {
                "navigation": "Unable to access Claude (claude.ai). The service may be experiencing technical difficulties or have geographical access restrictions. Browser automation couldn't establish a proper connection.",
                "login": "Unable to authenticate with Claude. Anthropic may have updated their login process, added additional security measures, or the provided credentials may need verification.",
                "interaction": "Connected to Claude but encountered an issue with the chat interface. The UI elements may have been updated or the interaction flow has changed.",
                "response": "Claude was accessible, but we couldn't properly capture its response. The response structure or rendering may have changed."
            },
            "gemini": {
                "navigation": "Unable to access Google's Gemini (gemini.google.com). This could be due to regional restrictions, service outages, or Google account requirements.",
                "login": "Unable to sign in to Gemini with Google credentials. This may require additional authentication steps, account verification, or consent screens not currently handled.",
                "interaction": "Connected to Gemini but encountered issues with the prompt interface. Google may have updated the UI or changed how inputs are processed.",
                "response": "Gemini was accessible, but we couldn't capture its response correctly. The response format or display method may have changed."
            },
            "deepseek": {
                "navigation": "Unable to access DeepSeek Chat (chat.deepseek.com). The service may have access limitations, be experiencing high traffic, or have changed its URL structure.",
                "login": "Unable to authenticate with DeepSeek. The login process may have changed, or additional verification steps might be required.",
                "interaction": "Connected to DeepSeek but encountered issues with the chat interface. The input mechanism or UI layout may have been updated.",
                "response": "DeepSeek was accessible, but we couldn't properly extract the response. The response format or rendering has likely changed."
            },
            "grok": {
                "navigation": "Unable to access Grok (grok.x.ai). The service may require X (Twitter) authentication, be experiencing technical issues, or have changed its domain.",
                "login": "Unable to authenticate with Grok. This likely requires valid X (Twitter) credentials and possibly additional verification steps not currently handled.",
                "interaction": "Connected to Grok but encountered issues with its interface. The chat components or interaction patterns may have been updated.",
                "response": "Grok was accessible, but we couldn't properly capture its response. The response structure or rendering may have changed."
            }
        }
        
        # Determine the specific failure type based on where we are in the process
        failure_type = "navigation"  # Default assumption
        current_url = self.browser.driver.current_url if self.browser.driver else "unknown"
        
        # Check if we're on the platform's domain
        platform_url = self.platforms[platform]["url"] if platform in self.platforms else ""
        if platform_url and platform_url in current_url:
            # We reached the site but couldn't do something there
            if self._is_logged_in(platform):
                # We're logged in, so either interaction or response issue
                failure_type = "interaction"  # or "response" but harder to determine
            else:
                # We reached the site but couldn't log in
                failure_type = "login"
        
        # Get the detailed platform-specific message for this failure type
        if platform in enhanced_fallbacks:
            platform_msg = enhanced_fallbacks[platform].get(
                failure_type,
                enhanced_fallbacks[platform].get("navigation")  # Default to navigation message
            )
        else:
            platform_msg = f"{platform.capitalize()} is currently unavailable. This may be due to authentication or interface changes."
        
        # Include timestamp for troubleshooting
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build a comprehensive and informative response with context and troubleshooting details
        response = (
            f"⚠️ Unable to process request with {platform.upper()} ({timestamp})\n\n"
            f"**Issue Details**: {platform_msg}\n\n"
            f"**Your prompt** (saved for future processing):\n'{prompt[:150]}{'...' if len(prompt) > 150 else ''}'\n\n"
            f"**Troubleshooting Recommendations**:\n"
            f"• Check network connectivity to {platform_url}\n"
            f"• Verify authentication credentials for {platform}\n"
            f"• Try an alternative AI platform from the dashboard\n"
            f"• Consider using an API-based approach if available\n\n"
            f"**Technical Information**: Failure type: {failure_type}. Last URL: {current_url[:60]}{'...' if len(current_url) > 60 else ''}\n"
            f"A screenshot has been saved for diagnostic purposes. The system will continue to monitor {platform} availability."
        )
        
        # Store the enhanced fallback response
        self.memory_system.add_message(conversation_id, response, is_user=False)
        
        # Return a properly formatted response object
        return {
            "status": "fallback",
            "platform": platform,
            "prompt": prompt,
            "response": response,
            "conversation_id": conversation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "Using fallback response due to browser automation issues"
        }
